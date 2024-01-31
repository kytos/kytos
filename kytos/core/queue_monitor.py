#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Callable, Optional
from collections import deque
from uuid import uuid4
from pydantic.dataclasses import dataclass
from pydantic import Field
from datetime import datetime, timedelta, timezone
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
        delta_secs: int,
        min_size_threshold: int,
        min_hits: int,
        qsize_func: Callable[[], int],
    ) -> None:
        """QueueMonitorWindow."""
        self.name = name
        self.deque: deque[QueueData] = deque()
        self.delta_secs = delta_secs
        self.min_size_threshold = min_size_threshold
        self.min_hits = min_hits
        self._default_last_logged = datetime(
            year=1970, month=1, day=1, tzinfo=timezone.utc
        )
        self._last_logged: datetime = self._default_last_logged
        self._tasks: set[asyncio.Task] = set()
        self.qsize_func = qsize_func
        self._sampling_freq_secs = 1

    def __repr__(self) -> str:
        """Repr."""
        last_logged = (
            self._last_logged
            if self._last_logged != self._default_last_logged
            else None
        )
        return (
            f"QueueMonitorWindow(name={self.name}, len={len(self.deque)}, "
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
                self._try_to_log_stats()
                await asyncio.sleep(self._sampling_freq_secs)
        except asyncio.CancelledError:
            pass

    def _try_to_append(self, queue_data: QueueData) -> Optional[QueueData]:
        """Try to append."""
        if queue_data.size < self.min_size_threshold:
            return None

        self.deque.append(queue_data)
        return queue_data

    def _try_to_log_stats(self) -> None:
        """Try to log stats."""
        self._popleft_passed_records()
        if (
            self.deque
            and len(self.deque) >= self.min_hits
            and self._last_logged + timedelta(seconds=self.delta_secs) <= now()
        ):
            first = self.deque.popleft()
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
            avg = size_acc / count
            self._last_logged = cur.created_at
            msg = (
                f"QueueMonitorWindow alert: {self.name}, counted: {count}, "
                f"min size: {minv}, max size: {maxv}, avg: {avg}, "
                f"first at: {first.created_at}, last at: {cur.created_at},"
                f" delta seconds: {self.delta_secs}, min_hits: {self.min_hits}"
            )
            LOG.warning(msg)

    def _popleft_passed_records(self) -> None:
        """Pop left passed records."""
        delta = self.delta_secs
        while (
            self.deque and (now() - self.deque[0].created_at).seconds > delta
        ):
            self.deque.popleft()
