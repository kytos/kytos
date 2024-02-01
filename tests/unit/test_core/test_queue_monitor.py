from kytos.core.queue_monitor import QueueMonitorWindow
from kytos.core.exceptions import KytosCoreException

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
