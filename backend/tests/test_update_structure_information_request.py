import unittest
from unittest.mock import patch
from backend.db.model.update_structure_information_request import UpdateStructureInformationRequest
from common.logging.error.error import Error


class TestUpdateStructureInformationRequest(unittest.TestCase):

    def test_valid_request(self):
        """Test creating a valid UpdateStructureInformationRequest"""
        property_id = "123"
        request = {
            'structureUpdates': [
                {'structure_id': 1, 'condition': 'good'},
                {'structure_id': 2, 'condition': 'needs_repair'}
            ]
        }

        obj = UpdateStructureInformationRequest(property_id, request)

        self.assertEqual(obj.property_id, property_id)
        self.assertEqual(obj.structure_updates, request['structureUpdates'])

    def test_missing_structure_updates_field(self):
        """Test that Error is raised when structureUpdates field is missing"""
        property_id = "123"
        request = {}

        with self.assertRaises(Error):
            UpdateStructureInformationRequest(property_id, request)

    def test_structure_updates_not_list(self):
        """Test validation when structureUpdates is not a list"""
        property_id = "123"
        request = {
            'structureUpdates': 'not a list'
        }

        # Note: The current implementation logs an error but doesn't raise
        # This test ensures the object is still created despite the warning
        obj = UpdateStructureInformationRequest(property_id, request)
        self.assertEqual(obj.structure_updates, 'not a list')

    def test_invalid_property_id(self):
        """Test that Error is raised when property_id cannot be converted to int"""
        property_id = "invalid"
        request = {
            'structureUpdates': []
        }

        with self.assertRaises(Error):
            UpdateStructureInformationRequest(property_id, request)

    def test_valid_property_id_conversion(self):
        """Test that valid property_id string is accepted"""
        property_id = "456"
        request = {
            'structureUpdates': []
        }

        obj = UpdateStructureInformationRequest(property_id, request)
        self.assertEqual(obj.property_id, property_id)

    def test_empty_structure_updates_list(self):
        """Test that empty structureUpdates list is valid"""
        property_id = "789"
        request = {
            'structureUpdates': []
        }

        obj = UpdateStructureInformationRequest(property_id, request)
        self.assertEqual(obj.structure_updates, [])


if __name__ == '__main__':
    unittest.main()
