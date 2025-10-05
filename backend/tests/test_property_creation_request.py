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

    # ==================== Brand/Model Field Tests - Omitted/None ====================

    def test_brand_model_fields_omitted(self):
        """Test that brand and model fields can be omitted entirely"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6
        }

        appliances = Appliances(appliances_data)

        self.assertIsNone(appliances.stove_brand)
        self.assertIsNone(appliances.stove_model)
        self.assertIsNone(appliances.dishwasher_brand)
        self.assertIsNone(appliances.dishwasher_model)
        self.assertIsNone(appliances.dryer_brand)
        self.assertIsNone(appliances.dryer_model)
        self.assertIsNone(appliances.refrigerator_brand)
        self.assertIsNone(appliances.refrigerator_model)
        self.assertIsNone(appliances.washer_brand)
        self.assertIsNone(appliances.washer_model)

    def test_brand_model_fields_none(self):
        """Test that brand and model fields can be None"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveBrand': None,
            'stoveModel': None,
            'dishwasherBrand': None,
            'dishwasherModel': None,
            'dryerBrand': None,
            'dryerModel': None,
            'refrigeratorBrand': None,
            'refrigeratorModel': None,
            'washerBrand': None,
            'washerModel': None
        }

        appliances = Appliances(appliances_data)

        self.assertIsNone(appliances.stove_brand)
        self.assertIsNone(appliances.stove_model)
        self.assertIsNone(appliances.dishwasher_brand)
        self.assertIsNone(appliances.dishwasher_model)
        self.assertIsNone(appliances.dryer_brand)
        self.assertIsNone(appliances.dryer_model)
        self.assertIsNone(appliances.refrigerator_brand)
        self.assertIsNone(appliances.refrigerator_model)
        self.assertIsNone(appliances.washer_brand)
        self.assertIsNone(appliances.washer_model)

    # ==================== Brand/Model Field Tests - Valid Values ====================

    def test_valid_stove_brand_and_model(self):
        """Test valid stove brand and model strings"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveBrand': 'GE',
            'stoveModel': 'Model XYZ-123'
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.stove_brand, 'GE')
        self.assertEqual(appliances.stove_model, 'Model XYZ-123')

    def test_valid_dishwasher_brand_and_model(self):
        """Test valid dishwasher brand and model strings"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'dishwasherBrand': 'Bosch',
            'dishwasherModel': 'SHPM88Z75N'
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.dishwasher_brand, 'Bosch')
        self.assertEqual(appliances.dishwasher_model, 'SHPM88Z75N')

    def test_valid_dryer_brand_and_model(self):
        """Test valid dryer brand and model strings"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'dryerBrand': 'Samsung',
            'dryerModel': 'DVE45R6100C'
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.dryer_brand, 'Samsung')
        self.assertEqual(appliances.dryer_model, 'DVE45R6100C')

    def test_valid_refrigerator_brand_and_model(self):
        """Test valid refrigerator brand and model strings"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'refrigeratorBrand': 'LG',
            'refrigeratorModel': 'LRFVS3006S'
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.refrigerator_brand, 'LG')
        self.assertEqual(appliances.refrigerator_model, 'LRFVS3006S')

    def test_valid_washer_brand_and_model(self):
        """Test valid washer brand and model strings"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'washerBrand': 'Whirlpool',
            'washerModel': 'WFW5620HW'
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.washer_brand, 'Whirlpool')
        self.assertEqual(appliances.washer_model, 'WFW5620HW')

    def test_all_brands_and_models_valid(self):
        """Test all brand and model fields with valid strings"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveBrand': 'GE',
            'stoveModel': 'JGB735SPSS',
            'dishwasherBrand': 'Bosch',
            'dishwasherModel': 'SHPM88Z75N',
            'dryerBrand': 'Samsung',
            'dryerModel': 'DVE45R6100C',
            'refrigeratorBrand': 'LG',
            'refrigeratorModel': 'LRFVS3006S',
            'washerBrand': 'Whirlpool',
            'washerModel': 'WFW5620HW'
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.stove_brand, 'GE')
        self.assertEqual(appliances.stove_model, 'JGB735SPSS')
        self.assertEqual(appliances.dishwasher_brand, 'Bosch')
        self.assertEqual(appliances.dishwasher_model, 'SHPM88Z75N')
        self.assertEqual(appliances.dryer_brand, 'Samsung')
        self.assertEqual(appliances.dryer_model, 'DVE45R6100C')
        self.assertEqual(appliances.refrigerator_brand, 'LG')
        self.assertEqual(appliances.refrigerator_model, 'LRFVS3006S')
        self.assertEqual(appliances.washer_brand, 'Whirlpool')
        self.assertEqual(appliances.washer_model, 'WFW5620HW')

    # ==================== Brand/Model Field Tests - Empty String ====================

    def test_stove_brand_empty_string(self):
        """Test that stove brand cannot be empty string"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveBrand': ''
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_stove_model_empty_string(self):
        """Test that stove model cannot be empty string"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveModel': ''
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dishwasher_brand_empty_string(self):
        """Test that dishwasher brand cannot be empty string"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'dishwasherBrand': ''
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dishwasher_model_empty_string(self):
        """Test that dishwasher model cannot be empty string"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'dishwasherModel': ''
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_refrigerator_brand_empty_string(self):
        """Test that refrigerator brand cannot be empty string"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'refrigeratorBrand': ''
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    # ==================== Brand/Model Field Tests - Whitespace Only ====================

    def test_stove_brand_whitespace_only(self):
        """Test that stove brand cannot be whitespace-only"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveBrand': '   '
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_stove_model_whitespace_only(self):
        """Test that stove model cannot be whitespace-only"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveModel': '   '
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_washer_brand_whitespace_only(self):
        """Test that washer brand cannot be whitespace-only"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'washerBrand': '\t\n  '
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    # ==================== Brand/Model Field Tests - Non-String Types ====================

    def test_stove_brand_integer(self):
        """Test that stove brand cannot be an integer"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveBrand': 123
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_stove_model_boolean(self):
        """Test that stove model cannot be a boolean"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveModel': True
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dishwasher_brand_dict(self):
        """Test that dishwasher brand cannot be a dict"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'dishwasherBrand': {'brand': 'Bosch'}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dishwasher_model_list(self):
        """Test that dishwasher model cannot be a list"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'dishwasherModel': ['Model123']
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dryer_brand_float(self):
        """Test that dryer brand cannot be a float"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'dryerBrand': 12.34
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_refrigerator_model_integer(self):
        """Test that refrigerator model cannot be an integer"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'refrigeratorModel': 999
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_washer_brand_list(self):
        """Test that washer brand cannot be a list"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'washerBrand': ['Whirlpool']
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    # ==================== Brand/Model Field Tests - Max Length ====================

    def test_stove_brand_max_length_valid(self):
        """Test that stove brand at exactly 100 characters is valid"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveBrand': 'A' * 100
        }

        appliances = Appliances(appliances_data)
        self.assertEqual(appliances.stove_brand, 'A' * 100)

    def test_stove_model_exceeds_max_length(self):
        """Test that stove model exceeding 100 characters is invalid"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveModel': 'A' * 101
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dishwasher_brand_exceeds_max_length(self):
        """Test that dishwasher brand exceeding 100 characters is invalid"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'dishwasherBrand': 'B' * 150
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_refrigerator_model_exceeds_max_length(self):
        """Test that refrigerator model exceeding 100 characters is invalid"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'refrigeratorModel': 'X' * 200
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    # ==================== Brand/Model Field Tests - Mixed Valid and Invalid ====================

    def test_mixed_valid_brand_only_one_appliance(self):
        """Test providing only brand for one appliance (model omitted)"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'stoveBrand': 'GE'
        }

        appliances = Appliances(appliances_data)
        self.assertEqual(appliances.stove_brand, 'GE')
        self.assertIsNone(appliances.stove_model)

    def test_mixed_valid_model_only_one_appliance(self):
        """Test providing only model for one appliance (brand omitted)"""
        appliances_data = {
            'stove': 5,
            'dishwasher': 3,
            'dryer': 7,
            'refrigerator': 4,
            'washer': 6,
            'dishwasherModel': 'SHPM88Z75N'
        }

        appliances = Appliances(appliances_data)
        self.assertIsNone(appliances.dishwasher_brand)
        self.assertEqual(appliances.dishwasher_model, 'SHPM88Z75N')


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
