"""Test kytos.core.cpm module."""

from unittest import TestCase
from unittest.mock import MagicMock, patch

from kytos.core.apm import ElasticAPM, begin_span, init_apm
from kytos.core.exceptions import KytosAPMInitException


class TestElasticAPM(TestCase):
    """TestElasticAPM."""

    def setUp(self):
        """setUp."""
        ElasticAPM._client = None
        ElasticAPM._flask_apm = None

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

        with self.assertRaises(KytosAPMInitException):
            init_apm("unknown_apm")
        assert mock_init.call_count == 1

    @patch("kytos.core.apm.ElasticAPM.init_client")
    def test_get_client(self, mock_init):
        """Test get_client."""
        assert not ElasticAPM._client
        assert not ElasticAPM._flask_apm
        ElasticAPM.get_client()
        assert mock_init.call_count == 1
        ElasticAPM._client = MagicMock()
        ElasticAPM.get_client()
        assert mock_init.call_count == 1

    @patch("kytos.core.apm.ElasticAPM._flask_apm")
    def test_init_flask_app(self, mock_flask_apm):
        """Test init_flask_app."""
        assert not ElasticAPM._client
        ElasticAPM.init_flask_app(MagicMock())
        assert mock_flask_apm.init_app.call_count == 1

    @patch("kytos.core.apm.FlaskAPM")
    @patch("kytos.core.apm.Client")
    def test_init_client(self, mock_client, mock_flask_apm):
        """Test init_client."""
        assert not ElasticAPM._client
        assert not ElasticAPM._flask_apm
        ElasticAPM.init_client()
        assert mock_client.call_count == 1
        assert mock_flask_apm.call_count == 1
