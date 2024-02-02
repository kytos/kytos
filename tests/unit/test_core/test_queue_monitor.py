from kytos.core.queue_monitor import QueueMonitorWindow, QueueRecord
from kytos.core.exceptions import KytosCoreException
from kytos.core.helpers import now
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest


class TestQueueMonitor:
    """TestQueueMonitor."""

    @pytest.mark.parametrize(
        "min_hits,delta_secs,min_size_threshold,exc_str",
        [
            (5, 1, 10, "min_hits/delta_secs: 5.0 must be <= 1"),
            (-1, 10, 10, "min_hits: -1 must be positive"),
            (2, -1, 10, "delta_secs: -1 must be positive"),
            (2, 10, -1, "min_size_threshold: -1 must be positive"),
        ],
    )
    def test_validate_constructor(
        self, min_hits, delta_secs, min_size_threshold, exc_str
    ) -> None:
        """Test validate."""
        with pytest.raises(KytosCoreException) as exc:
            QueueMonitorWindow(
                "app",
                min_hits,
                delta_secs,
                min_size_threshold,
                qsize_func=lambda: 1,
            )
        assert exc_str in str(exc)

    def test_try_to_append(self) -> None:
        """Test try to append."""
        qmon = QueueMonitorWindow(
            "app",
            min_hits=2,
            delta_secs=10,
            min_size_threshold=128,
            qsize_func=lambda: 1,
        )
        assert not qmon.deque
        assert not qmon._try_to_append(QueueRecord(size=64))
        assert not qmon.deque
        assert qmon._try_to_append(QueueRecord(size=256))
        assert len(qmon.deque) == 1

    def test_popleft_passed_records(self) -> None:
        """Test popleft passed records."""
        delta_secs = 10
        qmon = QueueMonitorWindow(
            "app",
            min_hits=2,
            delta_secs=delta_secs,
            min_size_threshold=128,
            qsize_func=lambda: 1,
        )
        n_records = 5
        for _ in range(n_records):
            created_at = now() - timedelta(seconds=delta_secs + 1)
            assert qmon._try_to_append(QueueRecord(size=256, created_at=created_at))
        assert len(qmon.deque) == n_records
        qmon._popleft_passed_records()
        assert not qmon.deque

        # it shouldn't popleft now if delta_secs haven't passed
        for _ in range(n_records):
            assert qmon._try_to_append(QueueRecord(size=256, created_at=now()))
        assert len(qmon.deque) == n_records
        qmon._popleft_passed_records()
        assert len(qmon.deque) == n_records

    @pytest.mark.parametrize(
        "log_at_most_n, gen_n_records, expected_log_count",
        [(5, 5, 5), (5, 10, 5), (5, 3, 3), (0, 10, 0)],
    )
    def test_log_at_most_n_records(
        self, monkeypatch, log_at_most_n, gen_n_records, expected_log_count
    ) -> None:
        """Test log_at_most_n_records."""
        log_mock = MagicMock()
        monkeypatch.setattr("kytos.core.queue_monitor.LOG", log_mock)
        qmon = QueueMonitorWindow(
            "app",
            min_hits=2,
            delta_secs=10,
            min_size_threshold=128,
            qsize_func=lambda: 1,
            log_at_most_n=log_at_most_n,
        )
        qmon._log_at_most_n_records([])
        assert not log_mock.call_count

        records = [QueueRecord(size=129) for _ in range(gen_n_records)]
        qmon._log_at_most_n_records(records)
        assert log_mock.warning.call_count == expected_log_count

    def test_log_queue_stats(self, monkeypatch) -> None:
        """Test log queue stats."""
        log_mock = MagicMock()
        monkeypatch.setattr("kytos.core.queue_monitor.LOG", log_mock)
        qmon = QueueMonitorWindow(
            "app",
            min_hits=2,
            delta_secs=10,
            min_size_threshold=128,
            qsize_func=lambda: 1,
        )
        qmon._log_queue_stats([])
        assert not log_mock.warning.call_count
        n_records = 5
        records = [QueueRecord(size=128 + i) for i in range(n_records)]
        qmon._log_queue_stats(records)
        assert log_mock.warning.call_count == 1
        rec_sizes = [rec.size for rec in records]
        min_size, max_size = min(rec_sizes), max(rec_sizes)
        avg = sum(rec_sizes) / len(rec_sizes)
        expected = (
            f"{qmon.name}, counted: {len(records)}, "
            f"min_size: {min_size}, "
            f"max_size: {max_size}, "
            f"avg: {avg}, first at: {str(records[0].created_at)}, "
            f"last at: {str(records[-1].created_at)}, "
            f"delta seconds: {qmon.delta_secs}, min_hits: {qmon.min_hits}"
        )
        log_mock.warning.assert_called_with(expected)

    async def test_start_stop(self, monkeypatch) -> None:
        """Test start stop."""
        sleep_mock = AsyncMock
        monkeypatch.setattr("asyncio.sleep", sleep_mock)
        qmon = QueueMonitorWindow(
            "app",
            min_hits=2,
            delta_secs=10,
            min_size_threshold=128,
            qsize_func=lambda: 1,
        )
        qmon.start()
        assert qmon._tasks
        qmon.stop()

    def test_get_records(self) -> None:
        """Test get_records."""
        delta_secs = 10
        qmon = QueueMonitorWindow(
            "app",
            min_hits=2,
            delta_secs=delta_secs,
            min_size_threshold=128,
            qsize_func=lambda: 1,
        )

        assert not qmon._get_records()
        n_records = 5
        for _ in range(n_records):
            assert qmon._try_to_append(QueueRecord(size=256, created_at=now()))
        # all elements are expected to be returned
        assert len(qmon.deque) == n_records
        records = qmon._get_records()
        assert len(records) == n_records
        assert not qmon.deque

        # old elements are expected to be discarded, resulting in no records
        for _ in range(n_records):
            created_at = now() + timedelta(seconds=delta_secs + 1)
            assert qmon._try_to_append(QueueRecord(size=256, created_at=created_at))
        assert len(qmon.deque) == n_records
        records = qmon._get_records()
        assert not len(records)
        assert not qmon.deque

    def test_get_records_partial(self) -> None:
        """Test get_records partial."""
        delta_secs = 5
        qmon = QueueMonitorWindow(
            "app",
            min_hits=3,
            delta_secs=delta_secs,
            min_size_threshold=128,
            qsize_func=lambda: 1,
        )

        n_records = 10
        for i in range(n_records, 0, -1):
            assert qmon._try_to_append(
                QueueRecord(size=256, created_at=now() - timedelta(seconds=i))
            )
        assert len(qmon.deque) == n_records

        # only 5 out of these 10 records are expected, given delta_secs = 5
        records = qmon._get_records()
        assert len(records) == 5
        assert not len(qmon.deque)

        n_records = 2
        for i in range(n_records, 0, -1):
            assert qmon._try_to_append(
                QueueRecord(size=256, created_at=now() - timedelta(seconds=i))
            )
        assert len(qmon.deque) == n_records

        # no records are expected now since n_records 2 < min_hits 3
        records = qmon._get_records()
        assert not len(records)
