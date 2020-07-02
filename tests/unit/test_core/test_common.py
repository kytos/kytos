"""Test kytos.core.common module."""
from unittest import TestCase
from unittest.mock import MagicMock

from kytos.core.common import GenericEntity


# pylint: disable=protected-access, too-many-public-methods
class TestGenericEntity(TestCase):
    """GenericEntity tests."""

    def setUp(self):
        """Instantiate a GenericEntity."""
        self.generic_entity = GenericEntity()
        self.generic_entity._active = True
        self.generic_entity._enabled = True

    def test_is_enabled__true(self):
        """Test is_enabled method if _enabled is true."""
        enabled = self.generic_entity.is_enabled()

        self.assertTrue(enabled)

    def test_is_enabled__false(self):
        """Test is_enabled method if _enabled is false."""
        self.generic_entity._enabled = False
        enabled = self.generic_entity.is_enabled()

        self.assertFalse(enabled)

    def test_is_active__true(self):
        """Test is_active method if _active is true."""
        active = self.generic_entity.is_active()

        self.assertTrue(active)

    def test_is_active__false(self):
        """Test is_active method if _active is false."""
        self.generic_entity._active = False
        active = self.generic_entity.is_active()

        self.assertFalse(active)

    def test_activate(self):
        """Test activate method."""
        self.generic_entity.activate()

        self.assertTrue(self.generic_entity._active)

    def test_deactivate(self):
        """Test deactivate method."""
        self.generic_entity.deactivate()

        self.assertFalse(self.generic_entity._active)

    def test_enable(self):
        """Test enable method."""
        self.generic_entity.enable()

        self.assertTrue(self.generic_entity._enabled)

    def test_disable(self):
        """Test disable method."""
        self.generic_entity.disable()

        self.assertFalse(self.generic_entity._enabled)

    def test_status__up(self):
        """Test status property if _enabled and _active are true."""
        self.generic_entity._enabled = True
        self.generic_entity._active = True

        status = self.generic_entity.status

        self.assertEqual(status.value, 1)

    def test_status__disabled(self):
        """Test status property if _enabled is false."""
        self.generic_entity._enabled = False

        status = self.generic_entity.status

        self.assertEqual(status.value, 2)

    def test_status__down(self):
        """Test status property if _active is false."""
        self.generic_entity._active = False

        status = self.generic_entity.status

        self.assertEqual(status.value, 3)

    def test_add_metadata__exists(self):
        """Test add_metadata method if metadata exists."""
        self.generic_entity.metadata = {'ABC': 123}

        self.generic_entity.add_metadata('ABC', 123)

        metadata = self.generic_entity.metadata
        self.assertEqual(metadata, {'ABC': 123})

    def test_add_metadata__not_exists(self):
        """Test add_metadata method if metadata does not exist."""
        self.generic_entity.add_metadata('ABC', 123)

        metadata = self.generic_entity.metadata
        self.assertEqual(metadata, {'ABC': 123})

    def test_remove_metadata__exists(self):
        """Test remove_metadata method if metadata exists."""
        self.generic_entity.metadata = {'ABC': 123}

        self.generic_entity.remove_metadata('ABC')

        metadata = self.generic_entity.metadata
        self.assertEqual(metadata, {})

    def test_remove_metadata__not_exists(self):
        """Test remove_metadata method if metadata does not exist."""
        self.generic_entity.remove_metadata('ABC')

        metadata = self.generic_entity.metadata
        self.assertEqual(metadata, {})

    def test_get_metadata(self):
        """Test get_metadata method."""
        self.generic_entity.metadata = {'ABC': 123}

        value = self.generic_entity.get_metadata('ABC')

        self.assertEqual(value, 123)

    def test_get_metadata_as_dict(self):
        """Test get_metadata_as_dict method."""
        value = MagicMock()
        value.as_dict.return_value = {'A': 1, 'B': 2, 'C': 3}
        self.generic_entity.metadata = {'ABC': value}

        metadata = self.generic_entity.get_metadata_as_dict()

        self.assertEqual(metadata, {'ABC': {'A': 1, 'B': 2, 'C': 3}})

    def test_update_metadata(self):
        """Test update_metadata method."""
        self.generic_entity.metadata = {'ABC': 123}

        self.generic_entity.update_metadata('ABC', 456)

        metadata = self.generic_entity.metadata
        self.assertEqual(metadata, {'ABC': 456})

    def test_clear_metadata(self):
        """Test clear_metadata method."""
        self.generic_entity.metadata = {'ABC': 123}

        self.generic_entity.clear_metadata()

        metadata = self.generic_entity.metadata
        self.assertEqual(metadata, {})

    def test_extend_metadata__not_force(self):
        """Test extend_metadata method by not forcing update."""
        self.generic_entity.metadata = {'ABC': 123}

        self.generic_entity.extend_metadata({'ABC': 456, 'DEF': 789}, False)

        metadata = self.generic_entity.metadata
        self.assertEqual(metadata, {'ABC': 123, 'DEF': 789})

    def test_extend_metadata__force(self):
        """Test extend_metadata method by forcing update."""
        self.generic_entity.metadata = {'ABC': 123}

        self.generic_entity.extend_metadata({'ABC': 456, 'DEF': 789}, True)

        metadata = self.generic_entity.metadata
        self.assertEqual(metadata, {'ABC': 456, 'DEF': 789})
