import unittest
from backend.db.model.update_appliance_information_request import UpdateApplianceInformationRequest
from common.logging.error.error import Error


class TestUpdateApplianceInformationRequest(unittest.TestCase):

    def test_valid_request(self):
        """Test creating a valid UpdateApplianceInformationRequest"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {'appliance_id': 1, 'age': 5},
                {'appliance_id': 2, 'age': 3}
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)

        self.assertEqual(obj.property_id, property_id)
        self.assertEqual(obj.appliance_updates, request['applianceUpdates'])

    def test_missing_appliance_updates_field(self):
        """Test that Error is raised when applianceUpdates field is missing"""
        property_id = "123"
        request = {}

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_appliance_updates_not_list(self):
        """Test validation when applianceUpdates is not a list"""
        property_id = "123"
        request = {
            'applianceUpdates': 'not a list'
        }

        # Note: The current implementation logs an error but doesn't raise
        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.appliance_updates, 'not a list')

    def test_invalid_property_id(self):
        """Test that Error is raised when property_id cannot be converted to int"""
        property_id = "invalid"
        request = {
            'applianceUpdates': []
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_valid_property_id_conversion(self):
        """Test that valid property_id string is accepted"""
        property_id = "456"
        request = {
            'applianceUpdates': []
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.property_id, property_id)

    def test_empty_appliance_updates_list(self):
        """Test that empty applianceUpdates list is valid"""
        property_id = "789"
        request = {
            'applianceUpdates': []
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.appliance_updates, [])

    def test_integer_property_id(self):
        """Test that integer property_id is accepted"""
        property_id = 999
        request = {
            'applianceUpdates': [{'appliance_id': 1, 'age': 10}]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.property_id, property_id)


if __name__ == '__main__':
    unittest.main()
