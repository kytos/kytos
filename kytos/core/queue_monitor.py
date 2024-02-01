#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import logging
import math
from typing import Callable, Optional
from collections import deque
from uuid import uuid4
from pydantic.dataclasses import dataclass
from pydantic import Field
from datetime import datetime, timedelta, timezone
from kytos.core.exceptions import KytosCoreException
from kytos.core.helpers import now

LOG = logging.getLogger(__name__)


@dataclass
class QueueData:
    """QueueData Record."""

    size: int
    id: str = Field(default_factory=lambda: uuid4())
    created_at: datetime = Field(default_factory=lambda: now())


class QueueMonitorWindow:
    """QueueMonitorWindow."""

    def __init__(
        self,
        name: str,
        min_hits: int,
        delta_secs: int,
        min_size_threshold: int,
        qsize_func: Callable[[], int],
        log_at_most_n=0,
    ) -> None:
        """QueueMonitorWindow."""
        self.name = name
        self.min_hits = min_hits
        self.delta_secs = delta_secs
        self.min_size_threshold = min_size_threshold
        self.qsize_func = qsize_func
        self.log_at_most_n = log_at_most_n

        self.deque: deque[QueueData] = deque()
        self._default_last_logged = datetime(
            year=1970, month=1, day=1, tzinfo=timezone.utc
        )
        self._last_logged: datetime = self._default_last_logged
        self._tasks: set[asyncio.Task] = set()
        self._sampling_freq_secs = 1
        self._validate()

    def _validate(self) -> None:
        """Validate QueueMonitorWindow."""
        positive_attrs = (
            "min_hits",
            "delta_secs",
            "min_size_threshold",
        )
        for attr in positive_attrs:
            val = getattr(self, attr)
            if val < 0:
                raise KytosCoreException(
                    f"{attr}: {val} must be positive"
                )
        ratio = self.min_hits / self.delta_secs
        if ratio > 1:
            raise KytosCoreException(
                f"min_hits/delta_secs: {ratio} must be <= 1 "
            )

    def __repr__(self) -> str:
        """Repr."""
        last_logged = (
            self._last_logged
            if self._last_logged != self._default_last_logged
            else None
        )
        return (
            f"QueueMonitor(name={self.name}, len={len(self.deque)}, "
            f"last_logged={last_logged}, "
            f"min_hits={self.min_hits}, "
            f"min_size_threshold={self.min_size_threshold}, "
            f"delta_secs={self.delta_secs})"
        )

    def start(self) -> None:
        """Start sampling."""
        LOG.info(f"Starting {self}")
        task = asyncio.create_task(self._keep_sampling())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    def stop(self):
        """Stop."""
        for task in self._tasks:
            task.cancel()

    async def _keep_sampling(self) -> None:
        """Keep sampling."""
        try:
            while True:
                self._try_to_append(QueueData(size=self.qsize_func()))
                records = self._try_to_log_stats()
                self._try_to_log_at_most_n_records(records)
                await asyncio.sleep(self._sampling_freq_secs)
        except asyncio.CancelledError:
            pass

    def _try_to_append(self, queue_data: QueueData) -> Optional[QueueData]:
        """Try to append."""
        if queue_data.size < self.min_size_threshold:
            return None

        self.deque.append(queue_data)
        return queue_data

    def _try_to_log_at_most_n_records(self, records: list[QueueData]) -> None:
        """Try to log at most n records."""
        if self.log_at_most_n <= 0 or not records:
            return

        for i in range(
            0,
            len(records),
            math.ceil(len(records) / self.log_at_most_n),
        ):
            record = records[i]
            msg = (
                f"{self.name}, "
                f"record[{i}]/[{len(records)}]: size: {record.size}, "
                f"at: {record.created_at}"
            )
            LOG.warning(msg)

    def _try_to_log_stats(self) -> list[QueueData]:
        """Try to log stats."""
        self._popleft_passed_records()
        records = []
        if (
            self.deque
            and len(self.deque) >= self.min_hits
            and self._last_logged + timedelta(seconds=self.delta_secs) <= now()
        ):
            first = self.deque.popleft()
            if self.log_at_most_n > 0:
                records.append(first)
            cur = first
            minv, maxv, size_acc, count = first.size, first.size, first.size, 1
            while (
                self.deque
                and (self.deque[0].created_at - first.created_at).seconds
                <= self.delta_secs
            ):
                cur = self.deque.popleft()
                minv = min(minv, cur.size)
                maxv = max(maxv, cur.size)
                count += 1
                if self.log_at_most_n > 0:
                    records.append(first)
            avg = size_acc / count
            self._last_logged = cur.created_at
            msg = (
                f"{self.name}, counted: {count}, "
                f"min size: {minv}, max size: {maxv}, avg: {avg}, "
                f"first at: {first.created_at}, last at: {cur.created_at},"
                f" delta seconds: {self.delta_secs}, min_hits: {self.min_hits}"
            )
            LOG.warning(msg)
        return records

    def _popleft_passed_records(self) -> None:
        """Pop left passed records."""
        delta = self.delta_secs
        while self.deque and (now() - self.deque[0].created_at).seconds > delta:
            self.deque.popleft()
