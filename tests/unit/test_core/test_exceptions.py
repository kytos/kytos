"""Test kytos.core.exceptions module."""
from unittest.mock import MagicMock

import pytest

from kytos.core.exceptions import (KytosCoreException, KytosEventException,
                                   KytosNAppException,
                                   KytosNoTagAvailableError,
                                   KytosSwitchOfflineException)


class TestExceptions:
    """Exceptions tests."""

    def test_kytos_core_exception(self):
        """Test KytosCoreException exception."""
        with pytest.raises(Exception) as exc:
            raise KytosCoreException('msg')

        expected_msg = 'KytosCore exception: msg'
        assert exc.match(expected_msg)

    def test_kytos_switch_offline_exception(self):
        """Test KytosSwitchOfflineException exception."""
        with pytest.raises(Exception) as exc:
            switch = MagicMock()
            switch.dpid = '00:00:00:00:00:00:00:01'
            raise KytosSwitchOfflineException(switch)

        expected_msg = 'The switch 00:00:00:00:00:00:00:01 is not reachable. '
        expected_msg += 'Please check the connection between the switch and '
        expected_msg += 'the controller.'

        assert exc.match(expected_msg)

    def test_kytos_event_exception(self):
        """Test KytosEventException exception."""
        with pytest.raises(Exception) as exc:
            raise KytosEventException

        expected_msg = 'KytosEvent exception'
        assert exc.match(expected_msg)

    def test_kytos_no_tag_avaible_error(self):
        """Test KytosNoTagAvailableError exception."""
        with pytest.raises(Exception) as exc:
            link = MagicMock()
            link.id = '123'
            raise KytosNoTagAvailableError(link)

        expected_msg = 'Link 123 has no vlan available.'
        assert exc.match(expected_msg)

    def test_kytos_napp_exception(self):
        """Test KytosNAppException exception."""
        with pytest.raises(Exception) as exc:
            raise KytosNAppException()

        expected_msg = 'KytosNApp exception'
        assert exc.match(expected_msg)
