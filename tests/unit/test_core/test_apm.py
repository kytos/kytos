"""Test kytos.core.cpm module."""
from unittest.mock import MagicMock, patch

import pytest

from kytos.core.apm import ElasticAPM, begin_span, init_apm
from kytos.core.exceptions import KytosAPMInitException


class TestElasticAPM:
    """TestElasticAPM."""

    def setup_method(self):
        """setUp."""
        ElasticAPM._client = None

    @patch("kytos.core.apm.execution_context")
    def test_begin_span_decorator(self, context):
        """Test begin span_decorator."""

        def inner():
            pass

        begin_span(inner)()
        assert context.get_transaction.call_count == 1

    @patch("kytos.core.apm.ElasticAPM.init_client")
    def test_init_apm(self, mock_init):
        """Test init_apm."""
        init_apm("es")
        assert mock_init.call_count == 1

        with pytest.raises(KytosAPMInitException):
            init_apm("unknown_apm")
        assert mock_init.call_count == 1

    @patch("kytos.core.apm.ElasticAPM.init_client")
    def test_get_client(self, mock_init):
        """Test get_client."""
        assert not ElasticAPM._client
        ElasticAPM.get_client()
        assert mock_init.call_count == 1
        ElasticAPM._client = MagicMock()
        ElasticAPM.get_client()
        assert mock_init.call_count == 1

    @patch("kytos.core.apm.Client")
    def test_init_client(self, mock_client):
        """Test init_client."""
        mock_app = MagicMock()
        assert not ElasticAPM._client
        ElasticAPM.init_client(app=mock_app)
        assert mock_client.call_count == 1
        assert mock_app.add_middleware.call_count == 1
