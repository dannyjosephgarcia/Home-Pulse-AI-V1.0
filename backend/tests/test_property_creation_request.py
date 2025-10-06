import unittest
from backend.db.model.property_creation_request import PropertyCreationRequest, Appliances, Structures
from common.logging.error.error import Error


class TestAppliances(unittest.TestCase):

    # ==================== Nested Format Tests (New Format) ====================

    def test_valid_nested_appliances_with_age_only(self):
        """Test creating Appliances with nested format - age only"""
        appliances_data = {
            'stove': {'age': 5},
            'dishwasher': {'age': 3},
            'dryer': {'age': 7},
            'refrigerator': {'age': 4},
            'washer': {'age': 6}
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.stove, 5)
        self.assertEqual(appliances.dishwasher, 3)
        self.assertEqual(appliances.dryer, 7)
        self.assertEqual(appliances.refrigerator, 4)
        self.assertEqual(appliances.washer, 6)
        # Brand and model should be None
        self.assertIsNone(appliances.stove_brand)
        self.assertIsNone(appliances.stove_model)

    def test_valid_nested_appliances_with_brand_and_model(self):
        """Test creating Appliances with nested format - age, brand, and model"""
        appliances_data = {
            'stove': {'age': 5, 'brand': 'GE', 'model': 'JGB735SPSS'},
            'dishwasher': {'age': 3, 'brand': 'Bosch', 'model': 'SHPM88Z75N'},
            'refrigerator': {'age': 4, 'brand': 'LG'}
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.stove, 5)
        self.assertEqual(appliances.stove_brand, 'GE')
        self.assertEqual(appliances.stove_model, 'JGB735SPSS')
        self.assertEqual(appliances.dishwasher, 3)
        self.assertEqual(appliances.dishwasher_brand, 'Bosch')
        self.assertEqual(appliances.dishwasher_model, 'SHPM88Z75N')
        self.assertEqual(appliances.refrigerator, 4)
        self.assertEqual(appliances.refrigerator_brand, 'LG')
        self.assertIsNone(appliances.refrigerator_model)

    def test_valid_ac_unit_in_appliances(self):
        """Test A/C unit as an appliance with nested format"""
        appliances_data = {
            'a/c unit': {'age': 3, 'brand': 'Carrier', 'model': 'ABC123'}
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.ac_unit, 3)
        self.assertEqual(appliances.ac_unit_brand, 'Carrier')
        self.assertEqual(appliances.ac_unit_model, 'ABC123')

    def test_mixed_nested_format_some_with_brand_some_without(self):
        """Test mixed scenario - some appliances with brand/model, some without"""
        appliances_data = {
            'stove': {'age': 5, 'brand': 'GE', 'model': 'XYZ123'},
            'dishwasher': {'age': 3},
            'refrigerator': {'age': 2, 'brand': 'LG'}
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.stove, 5)
        self.assertEqual(appliances.stove_brand, 'GE')
        self.assertEqual(appliances.stove_model, 'XYZ123')
        self.assertEqual(appliances.dishwasher, 3)
        self.assertIsNone(appliances.dishwasher_brand)
        self.assertIsNone(appliances.dishwasher_model)
        self.assertEqual(appliances.refrigerator, 2)
        self.assertEqual(appliances.refrigerator_brand, 'LG')
        self.assertIsNone(appliances.refrigerator_model)

    def test_empty_appliances_dict(self):
        """Test that empty appliances dict is valid - all appliances are optional"""
        appliances_data = {}

        appliances = Appliances(appliances_data)

        self.assertIsNone(appliances.stove)
        self.assertIsNone(appliances.dishwasher)
        self.assertIsNone(appliances.dryer)
        self.assertIsNone(appliances.refrigerator)
        self.assertIsNone(appliances.washer)
        self.assertIsNone(appliances.ac_unit)

    # ==================== Flat Format Tests (Legacy Backward Compatibility) ====================

    def test_valid_flat_format_appliances(self):
        """Test backward compatibility with flat format"""
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
        # No brand/model in flat format
        self.assertIsNone(appliances.stove_brand)
        self.assertIsNone(appliances.stove_model)

    def test_mixed_flat_and_nested_format(self):
        """Test that flat and nested formats can be mixed"""
        appliances_data = {
            'stove': 5,  # Flat format
            'dishwasher': {'age': 3, 'brand': 'Bosch'}  # Nested format
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.stove, 5)
        self.assertIsNone(appliances.stove_brand)
        self.assertEqual(appliances.dishwasher, 3)
        self.assertEqual(appliances.dishwasher_brand, 'Bosch')

    # ==================== Brand/Model Field Tests - Valid Values ====================

    def test_valid_stove_brand_and_model(self):
        """Test valid stove brand and model strings"""
        appliances_data = {
            'stove': {'age': 5, 'brand': 'GE', 'model': 'Model XYZ-123'}
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.stove_brand, 'GE')
        self.assertEqual(appliances.stove_model, 'Model XYZ-123')

    def test_valid_dishwasher_brand_and_model(self):
        """Test valid dishwasher brand and model strings"""
        appliances_data = {
            'dishwasher': {'age': 3, 'brand': 'Bosch', 'model': 'SHPM88Z75N'}
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.dishwasher_brand, 'Bosch')
        self.assertEqual(appliances.dishwasher_model, 'SHPM88Z75N')

    def test_valid_dryer_brand_and_model(self):
        """Test valid dryer brand and model strings"""
        appliances_data = {
            'dryer': {'age': 7, 'brand': 'Samsung', 'model': 'DVE45R6100C'}
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.dryer_brand, 'Samsung')
        self.assertEqual(appliances.dryer_model, 'DVE45R6100C')

    def test_valid_refrigerator_brand_and_model(self):
        """Test valid refrigerator brand and model strings"""
        appliances_data = {
            'refrigerator': {'age': 4, 'brand': 'LG', 'model': 'LRFVS3006S'}
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.refrigerator_brand, 'LG')
        self.assertEqual(appliances.refrigerator_model, 'LRFVS3006S')

    def test_valid_washer_brand_and_model(self):
        """Test valid washer brand and model strings"""
        appliances_data = {
            'washer': {'age': 6, 'brand': 'Whirlpool', 'model': 'WFW5620HW'}
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.washer_brand, 'Whirlpool')
        self.assertEqual(appliances.washer_model, 'WFW5620HW')

    def test_valid_ac_unit_brand_and_model(self):
        """Test valid A/C unit brand and model strings"""
        appliances_data = {
            'a/c unit': {'age': 8, 'brand': 'Carrier', 'model': 'XYZ789'}
        }

        appliances = Appliances(appliances_data)

        self.assertEqual(appliances.ac_unit_brand, 'Carrier')
        self.assertEqual(appliances.ac_unit_model, 'XYZ789')

    def test_all_brands_and_models_valid(self):
        """Test all brand and model fields with valid strings"""
        appliances_data = {
            'stove': {'age': 5, 'brand': 'GE', 'model': 'JGB735SPSS'},
            'dishwasher': {'age': 3, 'brand': 'Bosch', 'model': 'SHPM88Z75N'},
            'dryer': {'age': 7, 'brand': 'Samsung', 'model': 'DVE45R6100C'},
            'refrigerator': {'age': 4, 'brand': 'LG', 'model': 'LRFVS3006S'},
            'washer': {'age': 6, 'brand': 'Whirlpool', 'model': 'WFW5620HW'},
            'a/c unit': {'age': 8, 'brand': 'Carrier', 'model': 'ABC123'}
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
        self.assertEqual(appliances.ac_unit_brand, 'Carrier')
        self.assertEqual(appliances.ac_unit_model, 'ABC123')

    # ==================== Brand/Model Field Tests - Empty String ====================

    def test_stove_brand_empty_string(self):
        """Test that stove brand cannot be empty string"""
        appliances_data = {
            'stove': {'age': 5, 'brand': ''}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_stove_model_empty_string(self):
        """Test that stove model cannot be empty string"""
        appliances_data = {
            'stove': {'age': 5, 'model': ''}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dishwasher_brand_empty_string(self):
        """Test that dishwasher brand cannot be empty string"""
        appliances_data = {
            'dishwasher': {'age': 3, 'brand': ''}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dishwasher_model_empty_string(self):
        """Test that dishwasher model cannot be empty string"""
        appliances_data = {
            'dishwasher': {'age': 3, 'model': ''}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_refrigerator_brand_empty_string(self):
        """Test that refrigerator brand cannot be empty string"""
        appliances_data = {
            'refrigerator': {'age': 4, 'brand': ''}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    # ==================== Brand/Model Field Tests - Whitespace Only ====================

    def test_stove_brand_whitespace_only(self):
        """Test that stove brand cannot be whitespace-only"""
        appliances_data = {
            'stove': {'age': 5, 'brand': '   '}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_stove_model_whitespace_only(self):
        """Test that stove model cannot be whitespace-only"""
        appliances_data = {
            'stove': {'age': 5, 'model': '   '}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_washer_brand_whitespace_only(self):
        """Test that washer brand cannot be whitespace-only"""
        appliances_data = {
            'washer': {'age': 6, 'brand': '\t\n  '}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    # ==================== Brand/Model Field Tests - Non-String Types ====================

    def test_stove_brand_integer(self):
        """Test that stove brand cannot be an integer"""
        appliances_data = {
            'stove': {'age': 5, 'brand': 123}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_stove_model_boolean(self):
        """Test that stove model cannot be a boolean"""
        appliances_data = {
            'stove': {'age': 5, 'model': True}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dishwasher_brand_dict(self):
        """Test that dishwasher brand cannot be a dict"""
        appliances_data = {
            'dishwasher': {'age': 3, 'brand': {'brand': 'Bosch'}}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dishwasher_model_list(self):
        """Test that dishwasher model cannot be a list"""
        appliances_data = {
            'dishwasher': {'age': 3, 'model': ['Model123']}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dryer_brand_float(self):
        """Test that dryer brand cannot be a float"""
        appliances_data = {
            'dryer': {'age': 7, 'brand': 12.34}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_refrigerator_model_integer(self):
        """Test that refrigerator model cannot be an integer"""
        appliances_data = {
            'refrigerator': {'age': 4, 'model': 999}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_washer_brand_list(self):
        """Test that washer brand cannot be a list"""
        appliances_data = {
            'washer': {'age': 6, 'brand': ['Whirlpool']}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    # ==================== Brand/Model Field Tests - Max Length ====================

    def test_stove_brand_max_length_valid(self):
        """Test that stove brand at exactly 100 characters is valid"""
        appliances_data = {
            'stove': {'age': 5, 'brand': 'A' * 100}
        }

        appliances = Appliances(appliances_data)
        self.assertEqual(appliances.stove_brand, 'A' * 100)

    def test_stove_model_exceeds_max_length(self):
        """Test that stove model exceeding 100 characters is invalid"""
        appliances_data = {
            'stove': {'age': 5, 'model': 'A' * 101}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_dishwasher_brand_exceeds_max_length(self):
        """Test that dishwasher brand exceeding 100 characters is invalid"""
        appliances_data = {
            'dishwasher': {'age': 3, 'brand': 'B' * 150}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_refrigerator_model_exceeds_max_length(self):
        """Test that refrigerator model exceeding 100 characters is invalid"""
        appliances_data = {
            'refrigerator': {'age': 4, 'model': 'X' * 200}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    # ==================== Brand/Model Field Tests - Mixed Valid and Invalid ====================

    def test_mixed_valid_brand_only_one_appliance(self):
        """Test providing only brand for one appliance (model omitted)"""
        appliances_data = {
            'stove': {'age': 5, 'brand': 'GE'}
        }

        appliances = Appliances(appliances_data)
        self.assertEqual(appliances.stove_brand, 'GE')
        self.assertIsNone(appliances.stove_model)

    def test_mixed_valid_model_only_one_appliance(self):
        """Test providing only model for one appliance (brand omitted)"""
        appliances_data = {
            'dishwasher': {'age': 3, 'model': 'SHPM88Z75N'}
        }

        appliances = Appliances(appliances_data)
        self.assertIsNone(appliances.dishwasher_brand)
        self.assertEqual(appliances.dishwasher_model, 'SHPM88Z75N')

    # ==================== Invalid Age Tests ====================

    def test_nested_format_missing_age_field(self):
        """Test that nested format requires age field when validated through PropertyCreationRequest"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': {'brand': 'GE', 'model': 'XYZ'}},
            'structures': {'roof': 10}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_nested_format_age_not_integer(self):
        """Test that age must be an integer in nested format"""
        appliances_data = {
            'stove': {'age': 'five'}
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)

    def test_flat_format_invalid_string(self):
        """Test that flat format rejects non-integer values"""
        appliances_data = {
            'stove': 'invalid'
        }

        with self.assertRaises(Error):
            Appliances(appliances_data)


class TestStructures(unittest.TestCase):

    def test_valid_structures(self):
        """Test creating valid Structures object - A/C unit removed"""
        structures_data = {
            'roof': 10,
            'driveway': 15,
            'water heater': 8,
            'furnace': 12
        }

        structures = Structures(structures_data)

        self.assertEqual(structures.roof, 10)
        self.assertEqual(structures.driveway, 15)
        self.assertEqual(structures.water_heater, 8)
        self.assertEqual(structures.furnace, 12)

    def test_empty_structures_dict(self):
        """Test that empty structures dict is valid - all structures are optional"""
        structures_data = {}

        structures = Structures(structures_data)

        self.assertIsNone(structures.roof)
        self.assertIsNone(structures.driveway)
        self.assertIsNone(structures.water_heater)
        self.assertIsNone(structures.furnace)

    def test_partial_structures(self):
        """Test that only some structures can be provided"""
        structures_data = {
            'roof': 10,
            'furnace': 12
        }

        structures = Structures(structures_data)

        self.assertEqual(structures.roof, 10)
        self.assertIsNone(structures.driveway)
        self.assertIsNone(structures.water_heater)
        self.assertEqual(structures.furnace, 12)

    def test_invalid_structure_type(self):
        """Test that non-integer structure values are rejected"""
        structures_data = {
            'roof': 'invalid'
        }

        with self.assertRaises(Error):
            Structures(structures_data)


class TestPropertyCreationRequest(unittest.TestCase):

    def test_valid_property_creation_request_nested_format(self):
        """Test creating a valid PropertyCreationRequest with nested appliances"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {
                'stove': {'age': 5, 'brand': 'GE', 'model': 'XYZ123'},
                'dishwasher': {'age': 3},
                'refrigerator': {'age': 4, 'brand': 'LG'}
            },
            'structures': {
                'roof': 10,
                'driveway': 15,
                'water heater': 8,
                'furnace': 12
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

    def test_valid_property_with_ac_unit_in_appliances(self):
        """Test property creation with A/C unit as an appliance"""
        user_id = 456
        request = {
            'street': '789 Pine St',
            'city': 'Boston',
            'state': 'MA',
            'zip': '02101',
            'homeAge': 20,
            'appliances': {
                'a/c unit': {'age': 8, 'brand': 'Carrier', 'model': 'ABC123'}
            },
            'structures': {
                'roof': 15
            }
        }

        obj = PropertyCreationRequest(user_id, request)

        self.assertEqual(obj.appliances.ac_unit, 8)
        self.assertEqual(obj.appliances.ac_unit_brand, 'Carrier')
        self.assertEqual(obj.appliances.ac_unit_model, 'ABC123')

    def test_valid_property_empty_appliances_and_structures(self):
        """Test property creation with empty appliances and structures"""
        user_id = 789
        request = {
            'street': '456 Oak Ave',
            'city': 'Cambridge',
            'state': 'MA',
            'zip': '02139',
            'homeAge': 25,
            'appliances': {},
            'structures': {}
        }

        obj = PropertyCreationRequest(user_id, request)

        self.assertEqual(obj.user_id, user_id)
        self.assertIsNone(obj.appliances.stove)
        self.assertIsNone(obj.structures.roof)

    def test_valid_property_missing_appliances_field(self):
        """Test that appliances field is optional - defaults to empty dict"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'structures': {'roof': 10}
        }

        obj = PropertyCreationRequest(user_id, request)
        self.assertIsNone(obj.appliances.stove)

    def test_valid_property_missing_structures_field(self):
        """Test that structures field is optional - defaults to empty dict"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': {'age': 5}}
        }

        obj = PropertyCreationRequest(user_id, request)
        self.assertIsNone(obj.structures.roof)

    def test_valid_property_flat_format_backward_compatibility(self):
        """Test backward compatibility with flat appliance format"""
        user_id = 999
        request = {
            'street': '321 Elm St',
            'city': 'Portland',
            'state': 'OR',
            'zip': '97201',
            'homeAge': 10,
            'appliances': {
                'stove': 5,
                'refrigerator': 3
            },
            'structures': {
                'roof': 15
            }
        }

        obj = PropertyCreationRequest(user_id, request)

        self.assertEqual(obj.appliances.stove, 5)
        self.assertEqual(obj.appliances.refrigerator, 3)
        self.assertIsNone(obj.appliances.stove_brand)

    def test_missing_street_field(self):
        """Test that Error is raised when street field is missing"""
        user_id = 123
        request = {
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': {'age': 5}},
            'structures': {'roof': 10}
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
            'appliances': {'stove': {'age': 5}},
            'structures': {'roof': 10}
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
            'appliances': {'stove': {'age': 5}},
            'structures': {'roof': 10}
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
            'appliances': {'stove': {'age': 5}},
            'structures': {'roof': 10}
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
            'appliances': {'stove': {'age': 5}},
            'structures': {'roof': 10}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_invalid_appliance_datatype_nested(self):
        """Test that Error is raised when appliance has invalid datatype in nested format"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': {'age': 'invalid'}},
            'structures': {'roof': 10}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_invalid_appliance_datatype_flat(self):
        """Test that Error is raised when appliance has invalid datatype in flat format"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': 'invalid'},
            'structures': {'roof': 10}
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
            'appliances': {'stove': {'age': 5}},
            'structures': {'roof': 'invalid'}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_invalid_unknown_appliance_type(self):
        """Test that Error is raised for unknown appliance types"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'microwave': {'age': 5}},
            'structures': {'roof': 10}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_invalid_unknown_structure_type(self):
        """Test that Error is raised for unknown structure types"""
        user_id = 123
        request = {
            'street': '123 Main St',
            'city': 'Springfield',
            'state': 'IL',
            'zip': '62701',
            'homeAge': 15,
            'appliances': {'stove': {'age': 5}},
            'structures': {'deck': 10}
        }

        with self.assertRaises(Error):
            PropertyCreationRequest(user_id, request)

    def test_construct_property_address(self):
        """Test the construct_property_address static method"""
        address = PropertyCreationRequest.construct_property_address('456 Oak Ave', 'Portland', 'OR')
        self.assertEqual(address, '456 Oak Ave, Portland, OR')


if __name__ == '__main__':
    unittest.main()
