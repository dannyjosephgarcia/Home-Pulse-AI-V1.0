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
        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, 'not a list')

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

    # ==================== Brand/Model Field Tests - Omitted/None ====================

    def test_brand_model_fields_omitted(self):
        """Test that applianceBrand and applianceModel fields can be omitted"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {'appliance_id': 1, 'age': 5}
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.property_id, property_id)
        self.assertEqual(len(obj.appliance_updates), 1)

    def test_brand_model_fields_none(self):
        """Test that applianceBrand and applianceModel can be None"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': None,
                    'applianceModel': None
                }
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.property_id, property_id)
        self.assertEqual(len(obj.appliance_updates), 1)

    def test_multiple_updates_with_none_brand_model(self):
        """Test multiple appliance updates with None brand and model"""
        property_id = "456"
        request = {
            'applianceUpdates': [
                {'appliance_id': 1, 'age': 5, 'applianceBrand': None, 'applianceModel': None},
                {'appliance_id': 2, 'age': 3, 'applianceBrand': None, 'applianceModel': None}
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(len(obj.appliance_updates), 2)

    # ==================== Brand/Model Field Tests - Valid Values ====================

    def test_valid_brand_and_model(self):
        """Test valid applianceBrand and applianceModel strings"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 'GE',
                    'applianceModel': 'JGB735SPSS'
                }
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.appliance_updates[0]['applianceBrand'], 'GE')
        self.assertEqual(obj.appliance_updates[0]['applianceModel'], 'JGB735SPSS')

    def test_valid_brand_only(self):
        """Test providing only brand (model omitted)"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 'Samsung'
                }
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.appliance_updates[0]['applianceBrand'], 'Samsung')

    def test_valid_model_only(self):
        """Test providing only model (brand omitted)"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceModel': 'DVE45R6100C'
                }
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.appliance_updates[0]['applianceModel'], 'DVE45R6100C')

    def test_multiple_updates_with_valid_brand_model(self):
        """Test multiple appliance updates with valid brand and model"""
        property_id = "789"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 'GE',
                    'applianceModel': 'JGB735SPSS'
                },
                {
                    'appliance_id': 2,
                    'age': 3,
                    'applianceBrand': 'Bosch',
                    'applianceModel': 'SHPM88Z75N'
                }
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(len(obj.appliance_updates), 2)
        self.assertEqual(obj.appliance_updates[0]['applianceBrand'], 'GE')
        self.assertEqual(obj.appliance_updates[1]['applianceBrand'], 'Bosch')

    def test_mixed_updates_some_with_brand_model(self):
        """Test multiple updates where only some have brand/model"""
        property_id = "999"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 'LG',
                    'applianceModel': 'LRFVS3006S'
                },
                {
                    'appliance_id': 2,
                    'age': 3
                },
                {
                    'appliance_id': 3,
                    'age': 7,
                    'applianceBrand': 'Whirlpool'
                }
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(len(obj.appliance_updates), 3)
        self.assertEqual(obj.appliance_updates[0]['applianceBrand'], 'LG')
        self.assertEqual(obj.appliance_updates[2]['applianceBrand'], 'Whirlpool')

    # ==================== Brand/Model Field Tests - Empty String ====================

    def test_brand_empty_string(self):
        """Test that applianceBrand cannot be empty string"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': ''
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_model_empty_string(self):
        """Test that applianceModel cannot be empty string"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceModel': ''
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_both_brand_and_model_empty_string(self):
        """Test that both fields cannot be empty strings"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': '',
                    'applianceModel': ''
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_empty_string_in_multiple_updates(self):
        """Test that empty string in any update raises error"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 'GE',
                    'applianceModel': 'JGB735SPSS'
                },
                {
                    'appliance_id': 2,
                    'age': 3,
                    'applianceBrand': ''
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    # ==================== Brand/Model Field Tests - Whitespace Only ====================

    def test_brand_whitespace_only(self):
        """Test that applianceBrand cannot be whitespace-only"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': '   '
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_model_whitespace_only(self):
        """Test that applianceModel cannot be whitespace-only"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceModel': '\t\n  '
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_brand_tabs_and_spaces(self):
        """Test that applianceBrand cannot be tabs and spaces"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': '\t  \t'
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    # ==================== Brand/Model Field Tests - Non-String Types ====================

    def test_brand_integer(self):
        """Test that applianceBrand cannot be an integer"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 123
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_model_boolean(self):
        """Test that applianceModel cannot be a boolean"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceModel': True
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_brand_dict(self):
        """Test that applianceBrand cannot be a dict"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': {'brand': 'GE'}
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_model_list(self):
        """Test that applianceModel cannot be a list"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceModel': ['Model123']
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_brand_float(self):
        """Test that applianceBrand cannot be a float"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 12.34
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_model_integer(self):
        """Test that applianceModel cannot be an integer"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceModel': 999
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    # ==================== Brand/Model Field Tests - Max Length ====================

    def test_brand_max_length_valid(self):
        """Test that applianceBrand at exactly 100 characters is valid"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 'A' * 100
                }
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.appliance_updates[0]['applianceBrand'], 'A' * 100)

    def test_model_max_length_valid(self):
        """Test that applianceModel at exactly 100 characters is valid"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceModel': 'B' * 100
                }
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.appliance_updates[0]['applianceModel'], 'B' * 100)

    def test_brand_exceeds_max_length(self):
        """Test that applianceBrand exceeding 100 characters is invalid"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 'A' * 101
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_model_exceeds_max_length(self):
        """Test that applianceModel exceeding 100 characters is invalid"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceModel': 'X' * 150
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    def test_both_exceed_max_length(self):
        """Test that both fields exceeding 100 characters is invalid"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 'A' * 200,
                    'applianceModel': 'B' * 200
                }
            ]
        }

        with self.assertRaises(Error):
            UpdateApplianceInformationRequest(property_id, request)

    # ==================== Edge Case Tests ====================

    def test_valid_brand_with_special_characters(self):
        """Test that brand with special characters is valid"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 'GE - General Electric & Co.'
                }
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.appliance_updates[0]['applianceBrand'], 'GE - General Electric & Co.')

    def test_valid_model_with_numbers_and_dashes(self):
        """Test that model with numbers and dashes is valid"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceModel': 'JGB735-SPSS-2024'
                }
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.appliance_updates[0]['applianceModel'], 'JGB735-SPSS-2024')

    def test_single_character_brand_valid(self):
        """Test that single character brand is valid"""
        property_id = "123"
        request = {
            'applianceUpdates': [
                {
                    'appliance_id': 1,
                    'age': 5,
                    'applianceBrand': 'X'
                }
            ]
        }

        obj = UpdateApplianceInformationRequest(property_id, request)
        self.assertEqual(obj.appliance_updates[0]['applianceBrand'], 'X')


if __name__ == '__main__':
    unittest.main()
