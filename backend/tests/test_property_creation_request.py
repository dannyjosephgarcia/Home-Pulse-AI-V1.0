import unittest
from backend.db.model.property_creation_request import PropertyCreationRequest, Appliances, Structures
from common.logging.error.error import Error


class TestAppliances(unittest.TestCase):

    def test_valid_appliances(self):
        """Test creating valid Appliances object"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.stove, 5)
        self.assertEqual(appliances.dishwasher, 3)
        self.assertEqual(appliances.dryer, 7)
        self.assertEqual(appliances.refrigerator, 4)
        self.assertEqual(appliances.washer, 6)


class TestStructures(unittest.TestCase):

    def test_valid_structures(self):
        """Test creating valid Structures object"""
        structures_data = {
            'roof': 10,
            'driveway': 15,
            'water heater': 8,
            'furnace': 12,
            'a/c unit': 9
        }

        structures = Structures(structures_data)

        self.assertEqual(structures.roof, 10)
        self.assertEqual(structures.driveway, 15)
        self.assertEqual(structures.water_heater, 8)
        self.assertEqual(structures.furnace, 12)
        self.assertEqual(structures.ac_unit, 9)


class TestPropertyCreationRequest(unittest.TestCase):

    def test_valid_property_creation_request(self):
        """Test creating a valid PropertyCreationRequest"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {
                'stove': 5,
                'dishwasher': 3,
                'dryer': 7,
                'refrigerator': 4,
                'washer': 6
            },
            'structures': {
                'roof': 10,
                'driveway': 15,
                'water heater': 8,
                'furnace': 12,
                'a/c unit': 9
            }
        }

        obj = PropertyCreationRequest(user_id, request)

        self.assertEqual(obj.user_id, user_id)
        self.assertEqual(obj.street, '123 Main St')
        self.assertEqual(obj.city, 'Springfield')
        self.assertEqual(obj.state, 'IL')
        self.assertEqual(obj.zip, '62701')
        self.assertEqual(obj.home_age, 15)
        self.assertEqual(obj.home_address, '123 Main St, Springfield, IL')
        self.assertIsInstance(obj.appliances, Appliances)
        self.assertIsInstance(obj.structures, Structures)

    def test_missing_street_field(self):
        """Test that Error is raised when street field is missing"""
        user_id = 123
        request = {
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': 5, 'dishwasher': 3, 'dryer': 7, 'refrigerator': 4, 'washer': 6},
            'structures': {'roof': 10, 'driveway': 15, 'water heater': 8, 'furnace': 12, 'a/c unit': 9}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_missing_city_field(self):
        """Test that Error is raised when city field is missing"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': 5, 'dishwasher': 3, 'dryer': 7, 'refrigerator': 4, 'washer': 6},
            'structures': {'roof': 10, 'driveway': 15, 'water heater': 8, 'furnace': 12, 'a/c unit': 9}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_missing_state_field(self):
        """Test that Error is raised when state field is missing"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': 5, 'dishwasher': 3, 'dryer': 7, 'refrigerator': 4, 'washer': 6},
            'structures': {'roof': 10, 'driveway': 15, 'water heater': 8, 'furnace': 12, 'a/c unit': 9}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_missing_zip_field(self):
        """Test that Error is raised when zip field is missing"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'homeAge': 15,
            'appliances': {'stove': 5, 'dishwasher': 3, 'dryer': 7, 'refrigerator': 4, 'washer': 6},
            'structures': {'roof': 10, 'driveway': 15, 'water heater': 8, 'furnace': 12, 'a/c unit': 9}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_missing_home_age_field(self):
        """Test that Error is raised when homeAge field is missing"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'appliances': {'stove': 5, 'dishwasher': 3, 'dryer': 7, 'refrigerator': 4, 'washer': 6},
            'structures': {'roof': 10, 'driveway': 15, 'water heater': 8, 'furnace': 12, 'a/c unit': 9}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_missing_appliances_field(self):
        """Test that Error is raised when appliances field is missing"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'structures': {'roof': 10, 'driveway': 15, 'water heater': 8, 'furnace': 12, 'a/c unit': 9}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_missing_structures_field(self):
        """Test that Error is raised when structures field is missing"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': 5, 'dishwasher': 3, 'dryer': 7, 'refrigerator': 4, 'washer': 6}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_invalid_appliance_datatype(self):
        """Test that Error is raised when appliance has invalid datatype"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': 'invalid', 'dishwasher': 3, 'dryer': 7, 'refrigerator': 4, 'washer': 6},
            'structures': {'roof': 10, 'driveway': 15, 'water heater': 8, 'furnace': 12, 'a/c unit': 9}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_invalid_structure_datatype(self):
        """Test that Error is raised when structure has invalid datatype"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': 5, 'dishwasher': 3, 'dryer': 7, 'refrigerator': 4, 'washer': 6},
            'structures': {'roof': 'invalid', 'driveway': 15, 'water heater': 8, 'furnace': 12, 'a/c unit': 9}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_construct_property_address(self):
        """Test the construct_property_address static method"""
        address = PropertyCreationRequest.construct_property_address('456 Oak Ave', 'Portland', 'OR')
        self.assertEqual(address, '456 Oak Ave, Portland, OR')


if __name__ == '__main__':
    unittest.main()
