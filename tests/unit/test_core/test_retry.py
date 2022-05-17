"""Test kytos.core.retry module."""

from unittest.mock import patch, MagicMock
from kytos.core.retry import before_sleep, for_all_methods, retries
from tenacity import retry_if_exception_type, stop_after_attempt


@patch("kytos.core.retry.LOG")
def test_before_sleep(mock_log):
    """Test before sleep."""
    state = MagicMock()
    state.fn.__name__ = "some_name"
    state.seconds_since_start = 1
    before_sleep(state)
    assert mock_log.warning.call_count == 1


def test_for_all_methods_retries():
    """test for_all_methods retries."""

    mock = MagicMock()
    max_retries = 3

    @for_all_methods(
        retries,
        retry=retry_if_exception_type((ValueError,)),
        stop=stop_after_attempt(max_retries),
        reraise=True,
    )
    class SomeClass:
        def some_method(self, mock) -> None:
            mock()
            raise ValueError("some error")

    some_class = SomeClass()
    try:
        some_class.some_method(mock)
    except ValueError:
        pass
    assert mock.call_count == max_retries
