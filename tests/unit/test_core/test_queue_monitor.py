from kytos.core.queue_monitor import QueueMonitorWindow, QueueData
from kytos.core.exceptions import KytosCoreException
from kytos.core.helpers import now
from datetime import timedelta
from unittest.mock import MagicMock

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
        assert not qmon._try_to_append(QueueData(size=64))
        assert not qmon.deque
        assert qmon._try_to_append(QueueData(size=256))
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
            dt = now() - timedelta(seconds=delta_secs + 1)
            assert qmon._try_to_append(QueueData(size=256, created_at=dt))
        assert len(qmon.deque) == n_records
        qmon._popleft_passed_records()
        assert not qmon.deque

        # it shouldn't popleft now if delta_secs haven't passed
        for _ in range(n_records):
            assert qmon._try_to_append(QueueData(size=256, created_at=now()))
        assert len(qmon.deque) == n_records
        qmon._popleft_passed_records()
        assert len(qmon.deque) == n_records

    @pytest.mark.parametrize(
        "log_at_most_n, gen_n_records, expected_log_count",
        [(5, 5, 5), (5, 10, 5), (5, 3, 3), (0, 10, 0)],
    )
    def test_try_to_log_at_most_n_records(
        self, monkeypatch, log_at_most_n, gen_n_records, expected_log_count
    ) -> None:
        """Test try_to_log_at_most_n_records."""
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
        qmon._try_to_log_at_most_n_records([])
        assert not log_mock.call_count

        records = [QueueData(size=129) for _ in range(gen_n_records)]
        qmon._try_to_log_at_most_n_records(records)
        assert log_mock.warning.call_count == expected_log_count
