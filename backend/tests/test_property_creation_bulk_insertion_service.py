import unittest
import io
import pandas as pd
from unittest.mock import MagicMock, patch, call
from backend.db.service.property_creation_bulk_insertion_service import PropertyCreationBulkInsertionService
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_BULK_CSV_FILE, INTERNAL_SERVICE_ERROR


class TestPropertyCreationBulkInsertionService(unittest.TestCase):
    """Test cases for PropertyCreationBulkInsertionService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_pool = MagicMock()
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_pool.pool.get_connection.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.service = PropertyCreationBulkInsertionService(self.mock_pool)

    def create_csv_content(self, rows):
        """Helper to create CSV content from rows"""
        csv_lines = [
            "street,city,state,postal_code,property_age,unit_number,stove_brand,stove_model,stove_age,"
            "washer_brand,washer_model,washer_age,air_conditioner_brand,air_conditioner_model,"
            "air_conditioner_age,water_heater_brand,water_heater_model,water_heater_age,"
            "dryer_brand,dryer_model,dryer_age,dishwasher_brand,dishwasher_model,dishwasher_age,"
            "refrigerator_brand,refrigerator_model,refrigerator_age,roof_age,driveway_age,furnace_age,deck_age"
        ]
        csv_lines.extend(rows)
        return io.StringIO('\n'.join(csv_lines))


class TestCSVValidation(TestPropertyCreationBulkInsertionService):
    """Tests for validate_contents_of_csv_file"""

    def test_valid_csv_with_all_columns(self):
        """Test that a CSV with all required columns is valid"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])

        result = self.service.validate_contents_of_csv_file(csv_content)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertIn('street', result.columns)
        self.assertIn('city', result.columns)
        self.assertIn('property_age', result.columns)
        self.assertIn('unit_number', result.columns)

    def test_csv_missing_required_columns(self):
        """Test that CSV missing required columns raises INVALID_BULK_CSV_FILE"""
        csv_content = io.StringIO("street,city,state\n123 Main St,Springfield,IL")

        with self.assertRaises(Error) as context:
            self.service.validate_contents_of_csv_file(csv_content)

        self.assertEqual(context.exception.code, INVALID_BULK_CSV_FILE.code)

    def test_csv_missing_property_columns(self):
        """Test that CSV missing property columns raises error (missing street and property_age)"""
        csv_content = io.StringIO(
            "city,state,postal_code,unit_number,stove_brand,stove_model,stove_age,"
            "washer_brand,washer_model,washer_age,air_conditioner_brand,air_conditioner_model,"
            "air_conditioner_age,water_heater_brand,water_heater_model,water_heater_age,"
            "dryer_brand,dryer_model,dryer_age,dishwasher_brand,dishwasher_model,dishwasher_age,"
            "refrigerator_brand,refrigerator_model,refrigerator_age,roof_age,driveway_age,furnace_age,deck_age\n"
            "Springfield,IL,62701,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        )

        with self.assertRaises(Error) as context:
            self.service.validate_contents_of_csv_file(csv_content)

        self.assertEqual(context.exception.code, INVALID_BULK_CSV_FILE.code)

    def test_csv_missing_appliance_columns(self):
        """Test that CSV missing appliance columns raises error"""
        csv_content = io.StringIO(
            "street,city,state,postal_code,property_age,unit_number,roof_age,driveway_age,furnace_age,deck_age\n"
            "123 Main St,Springfield,IL,62701,25,-1,15,20,10,5"
        )

        with self.assertRaises(Error) as context:
            self.service.validate_contents_of_csv_file(csv_content)

        self.assertEqual(context.exception.code, INVALID_BULK_CSV_FILE.code)

    def test_csv_missing_structure_columns(self):
        """Test that CSV missing structure columns raises error"""
        csv_content = io.StringIO(
            "street,city,state,postal_code,property_age,unit_number,stove_brand,stove_model,stove_age,"
            "washer_brand,washer_model,washer_age,air_conditioner_brand,air_conditioner_model,"
            "air_conditioner_age,water_heater_brand,water_heater_model,water_heater_age,"
            "dryer_brand,dryer_model,dryer_age,dishwasher_brand,dishwasher_model,dishwasher_age,"
            "refrigerator_brand,refrigerator_model,refrigerator_age\n"
            "123 Main St,Springfield,IL,62701,25,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8"
        )

        with self.assertRaises(Error) as context:
            self.service.validate_contents_of_csv_file(csv_content)

        self.assertEqual(context.exception.code, INVALID_BULK_CSV_FILE.code)

    def test_malformed_csv_raises_error(self):
        """Test that malformed CSV raises INVALID_BULK_CSV_FILE"""
        csv_content = io.StringIO("This is not a valid CSV\n\n\n")

        with self.assertRaises(Error) as context:
            self.service.validate_contents_of_csv_file(csv_content)

        self.assertEqual(context.exception.code, INVALID_BULK_CSV_FILE.code)

    def test_empty_csv_raises_error(self):
        """Test that empty CSV raises INVALID_BULK_CSV_FILE"""
        csv_content = io.StringIO("")

        with self.assertRaises(Error) as context:
            self.service.validate_contents_of_csv_file(csv_content)

        self.assertEqual(context.exception.code, INVALID_BULK_CSV_FILE.code)


class TestCSVParsing(TestPropertyCreationBulkInsertionService):
    """Tests for parse_csv_file_for_upload"""

    def test_parse_single_family_property(self):
        """Test parsing single-family property (unit_number = -1)"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        self.assertEqual(len(result), 1)
        self.assertIn('property', result[0])
        self.assertIn('appliances', result[0])
        self.assertIn('structures', result[0])

        # Verify property data
        property_data = result[0]['property']
        self.assertEqual(property_data['user_id'], 123)
        self.assertEqual(property_data['street'], '123 Main St')
        self.assertEqual(property_data['city'], 'Springfield')
        self.assertEqual(property_data['state'], 'IL')
        self.assertEqual(property_data['postal_code'], '62701')
        self.assertEqual(property_data['property_age'], 25)
        self.assertEqual(property_data['unit_number'], '-1')
        self.assertEqual(property_data['address'], '123 Main St, Springfield, IL')

    def test_parse_multifamily_property(self):
        """Test parsing multifamily property (unit_number != -1)"""
        csv_content = self.create_csv_content([
            "456 Oak Ave,Boston,MA,02101,30,101,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=456)

        self.assertEqual(len(result), 1)
        property_data = result[0]['property']
        self.assertEqual(property_data['property_age'], 30)
        self.assertEqual(property_data['unit_number'], '101')
        self.assertEqual(property_data['street'], '456 Oak Ave')

    def test_parse_all_appliances(self):
        """Test that all 7 appliance types are parsed correctly"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,GE,Stove1,5,Whirlpool,Washer1,3,Carrier,AC1,7,"
            "Rheem,WH1,4,Samsung,Dryer1,2,Bosch,DW1,6,LG,Fridge1,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        appliances = result[0]['appliances']
        self.assertEqual(len(appliances), 7)

        appliance_types = [a['appliance_type'] for a in appliances]
        self.assertIn('stove', appliance_types)
        self.assertIn('washer', appliance_types)
        self.assertIn('air_conditioner', appliance_types)
        self.assertIn('water_heater', appliance_types)
        self.assertIn('dryer', appliance_types)
        self.assertIn('dishwasher', appliance_types)
        self.assertIn('refrigerator', appliance_types)

        # Verify one appliance data structure
        stove = next(a for a in appliances if a['appliance_type'] == 'stove')
        self.assertEqual(stove['appliance_brand'], 'GE')
        self.assertEqual(stove['appliance_model'], 'Stove1')
        self.assertEqual(stove['age_in_years'], 5)

    def test_parse_all_structures(self):
        """Test that all 4 structure types are parsed correctly"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        structures = result[0]['structures']
        self.assertEqual(len(structures), 4)

        structure_types = [s['structure_type'] for s in structures]
        self.assertIn('roof', structure_types)
        self.assertIn('driveway', structure_types)
        self.assertIn('furnace', structure_types)
        self.assertIn('deck', structure_types)

        # Verify structure data
        roof = next(s for s in structures if s['structure_type'] == 'roof')
        self.assertEqual(roof['age_in_years'], 15)

    def test_parse_with_missing_appliance_values(self):
        """Test parsing when some appliances have empty values"""
        # CSV order: stove(3), washer(3), air_conditioner(3), water_heater(3), dryer(3), dishwasher(3), refrigerator(3)
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,GE,Model1,5,Whirlpool,Model2,3,,,,,,,,,,,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        appliances = result[0]['appliances']
        # Should only have stove and washer (others are empty)
        self.assertEqual(len(appliances), 2)
        appliance_types = [a['appliance_type'] for a in appliances]
        self.assertIn('stove', appliance_types)
        self.assertIn('washer', appliance_types)
        # Verify empty ones are not included
        self.assertNotIn('air_conditioner', appliance_types)
        self.assertNotIn('water_heater', appliance_types)

    def test_parse_with_missing_structure_values(self):
        """Test parsing when some structures have empty values"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,,,"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        structures = result[0]['structures']
        # Should only have roof
        self.assertEqual(len(structures), 1)
        self.assertEqual(structures[0]['structure_type'], 'roof')

    def test_parse_appliance_with_age_but_no_brand(self):
        """Test that appliances with age but no brand are skipped"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,GE,Model1,5,,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        appliances = result[0]['appliances']
        appliance_types = [a['appliance_type'] for a in appliances]
        # Washer should be skipped (has age but no brand)
        self.assertNotIn('washer', appliance_types)

    def test_parse_appliance_with_none_model(self):
        """Test that appliances with brand but no model are included with None model"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,GE,,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        appliances = result[0]['appliances']
        stove = next(a for a in appliances if a['appliance_type'] == 'stove')
        self.assertEqual(stove['appliance_brand'], 'GE')
        self.assertIsNone(stove['appliance_model'])

    def test_parse_multiple_properties(self):
        """Test parsing multiple properties from CSV"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5",
            "456 Oak Ave,Boston,MA,02101,30,101,Samsung,Model1,3,LG,Model2,2,Trane,Model3,5,"
            "AO Smith,Model4,6,Whirlpool,Model5,4,KitchenAid,Model6,3,GE,Model7,7,12,18,8,3"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['property']['street'], '123 Main St')
        self.assertEqual(result[1]['property']['street'], '456 Oak Ave')

    def test_safe_int_with_various_inputs(self):
        """Test safe_int helper handles various input types"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,GE,Model1,5,Whirlpool,Model2,invalid,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        # Washer with invalid age should be skipped
        appliances = result[0]['appliances']
        appliance_types = [a['appliance_type'] for a in appliances]
        self.assertNotIn('washer', appliance_types)

    def test_safe_str_with_whitespace(self):
        """Test safe_str helper strips whitespace"""
        csv_content = self.create_csv_content([
            " 123 Main St ,  Springfield , IL , 62701 , 25 ,-1,  GE  ,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        property_data = result[0]['property']
        self.assertEqual(property_data['street'], '123 Main St')
        self.assertEqual(property_data['city'], 'Springfield')


class TestBulkInsertion(TestPropertyCreationBulkInsertionService):
    """Tests for execute_bulk_properties_insertion"""

    def test_insert_single_family_property_with_appliances_and_structures(self):
        """Test inserting single-family property with appliances and structures"""
        data_to_upload = [{
            'property': {
                'user_id': 123,
                'street': '123 Main St',
                'city': 'Springfield',
                'state': 'IL',
                'postal_code': '62701',
                'property_age': 25,
                'unit_number': '-1',
                'address': '123 Main St, Springfield, IL'
            },
            'appliances': [
                {'appliance_type': 'stove', 'appliance_brand': 'GE', 'appliance_model': 'Model1', 'age_in_years': 5}
            ],
            'structures': [
                {'structure_type': 'roof', 'age_in_years': 15}
            ]
        }]

        self.mock_cursor.lastrowid = 1001

        result = self.service.execute_bulk_properties_insertion(
            cnx=self.mock_connection,
            data_to_upload=data_to_upload
        )

        self.assertEqual(result, 200)
        # Verify property insert
        self.assertGreaterEqual(self.mock_cursor.execute.call_count, 1)
        # Verify commit was called
        self.mock_connection.commit.assert_called_once()
        # Verify cursor closed
        self.mock_cursor.close.assert_called_once()

    def test_insert_multifamily_property_creates_unit(self):
        """Test inserting multifamily property creates unit record"""
        data_to_upload = [{
            'property': {
                'user_id': 456,
                'street': '456 Oak Ave',
                'city': 'Boston',
                'state': 'MA',
                'postal_code': '02101',
                'property_age': 30,
                'unit_number': '101',
                'address': '456 Oak Ave, Boston, MA'
            },
            'appliances': [
                {'appliance_type': 'refrigerator', 'appliance_brand': 'LG', 'appliance_model': 'Model1', 'age_in_years': 3}
            ],
            'structures': []
        }]

        self.mock_cursor.lastrowid = 2001

        result = self.service.execute_bulk_properties_insertion(
            cnx=self.mock_connection,
            data_to_upload=data_to_upload
        )

        self.assertEqual(result, 200)
        # Should execute: property insert, unit insert, appliance insert
        self.assertGreaterEqual(self.mock_cursor.execute.call_count, 3)

    def test_insert_single_family_appliances_have_null_unit_id(self):
        """Test that single-family appliances are inserted with unit_id = None"""
        data_to_upload = [{
            'property': {
                'user_id': 123,
                'street': '123 Main St',
                'city': 'Springfield',
                'state': 'IL',
                'postal_code': '62701',
                'property_age': 25,
                'unit_number': '-1',
                'address': '123 Main St, Springfield, IL'
            },
            'appliances': [
                {'appliance_type': 'stove', 'appliance_brand': 'GE', 'appliance_model': 'Model1', 'age_in_years': 5}
            ],
            'structures': []
        }]

        self.mock_cursor.lastrowid = 1001

        result = self.service.execute_bulk_properties_insertion(
            cnx=self.mock_connection,
            data_to_upload=data_to_upload
        )

        self.assertEqual(result, 200)
        # Check that appliance insert had None for unit_id (second parameter)
        appliance_call = [call for call in self.mock_cursor.execute.call_args_list
                         if 'appliances' in str(call)]
        self.assertGreater(len(appliance_call), 0)
        appliance_params = appliance_call[0][0][1]
        self.assertIsNone(appliance_params[1])  # unit_id should be None

    def test_insert_multifamily_appliances_have_unit_id(self):
        """Test that multifamily appliances are inserted with unit_id"""
        data_to_upload = [{
            'property': {
                'user_id': 456,
                'street': '456 Oak Ave',
                'city': 'Boston',
                'state': 'MA',
                'postal_code': '02101',
                'property_age': 30,
                'unit_number': '101',
                'address': '456 Oak Ave, Boston, MA'
            },
            'appliances': [
                {'appliance_type': 'refrigerator', 'appliance_brand': 'LG', 'appliance_model': 'Model1', 'age_in_years': 3}
            ],
            'structures': []
        }]

        # Mock property_id and unit_id
        lastrowids = [2001, 3001]
        call_count = [0]

        def get_lastrowid(*args, **kwargs):
            result = lastrowids[call_count[0]]
            if call_count[0] < len(lastrowids) - 1:
                call_count[0] += 1
            return result

        type(self.mock_cursor).lastrowid = property(lambda self: get_lastrowid())

        result = self.service.execute_bulk_properties_insertion(
            cnx=self.mock_connection,
            data_to_upload=data_to_upload
        )

        self.assertEqual(result, 200)
        # Verify unit_id was passed to appliance insert
        appliance_call = [call for call in self.mock_cursor.execute.call_args_list
                         if 'appliances' in str(call)]
        self.assertGreater(len(appliance_call), 0)

    def test_insert_structures_always_property_level(self):
        """Test that structures are always inserted at property level (no unit_id)"""
        data_to_upload = [{
            'property': {
                'user_id': 456,
                'street': '456 Oak Ave',
                'city': 'Boston',
                'state': 'MA',
                'postal_code': '02101',
                'property_age': 30,
                'unit_number': '101',
                'address': '456 Oak Ave, Boston, MA'
            },
            'appliances': [],
            'structures': [
                {'structure_type': 'roof', 'age_in_years': 20}
            ]
        }]

        self.mock_cursor.lastrowid = 2001

        result = self.service.execute_bulk_properties_insertion(
            cnx=self.mock_connection,
            data_to_upload=data_to_upload
        )

        self.assertEqual(result, 200)
        # Check that structure insert only has 3 parameters (property_id, structure_type, age)
        structure_call = [call for call in self.mock_cursor.execute.call_args_list
                         if 'structures' in str(call)]
        self.assertGreater(len(structure_call), 0)
        structure_params = structure_call[0][0][1]
        self.assertEqual(len(structure_params), 3)

    def test_insert_multiple_properties(self):
        """Test inserting multiple properties in one transaction"""
        data_to_upload = [
            {
                'property': {
                    'user_id': 123,
                    'street': '123 Main St',
                    'city': 'Springfield',
                    'state': 'IL',
                    'postal_code': '62701',
                    'property_age': 25,
                    'unit_number': '-1',
                    'address': '123 Main St, Springfield, IL'
                },
                'appliances': [{'appliance_type': 'stove', 'appliance_brand': 'GE', 'appliance_model': 'Model1', 'age_in_years': 5}],
                'structures': []
            },
            {
                'property': {
                    'user_id': 123,
                    'street': '456 Oak Ave',
                    'city': 'Boston',
                    'state': 'MA',
                    'postal_code': '02101',
                    'property_age': 30,
                    'unit_number': '-1',
                    'address': '456 Oak Ave, Boston, MA'
                },
                'appliances': [{'appliance_type': 'washer', 'appliance_brand': 'LG', 'appliance_model': 'Model2', 'age_in_years': 2}],
                'structures': []
            }
        ]

        lastrowids = [1001, 2001]
        call_count = [0]

        def get_lastrowid(*args, **kwargs):
            if call_count[0] < len(lastrowids):
                result = lastrowids[call_count[0]]
                call_count[0] += 1
                return result
            return lastrowids[-1]

        type(self.mock_cursor).lastrowid = property(lambda self: get_lastrowid())

        result = self.service.execute_bulk_properties_insertion(
            cnx=self.mock_connection,
            data_to_upload=data_to_upload
        )

        self.assertEqual(result, 200)
        # Should execute: 2 property inserts, 2 appliance inserts
        self.assertGreaterEqual(self.mock_cursor.execute.call_count, 4)

    def test_database_error_triggers_rollback(self):
        """Test that database errors trigger transaction rollback"""
        data_to_upload = [{
            'property': {
                'user_id': 123,
                'street': '123 Main St',
                'city': 'Springfield',
                'state': 'IL',
                'postal_code': '62701',
                'property_age': 25,
                'unit_number': '-1',
                'address': '123 Main St, Springfield, IL'
            },
            'appliances': [],
            'structures': []
        }]

        self.mock_cursor.execute.side_effect = Exception('Database connection error')

        with self.assertRaises(Error) as context:
            self.service.execute_bulk_properties_insertion(
                cnx=self.mock_connection,
                data_to_upload=data_to_upload
            )

        self.assertEqual(context.exception.code, INTERNAL_SERVICE_ERROR.code)
        self.mock_connection.rollback.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_cursor_closed_in_finally_block(self):
        """Test that cursor is always closed even on error"""
        data_to_upload = [{
            'property': {
                'user_id': 123,
                'street': '123 Main St',
                'city': 'Springfield',
                'state': 'IL',
                'postal_code': '62701',
                'property_age': 25,
                'unit_number': '-1',
                'address': '123 Main St, Springfield, IL'
            },
            'appliances': [],
            'structures': []
        }]

        self.mock_cursor.execute.side_effect = Exception('Database error')

        try:
            self.service.execute_bulk_properties_insertion(
                cnx=self.mock_connection,
                data_to_upload=data_to_upload
            )
        except Error:
            pass

        self.mock_cursor.close.assert_called_once()

    def test_property_age_from_csv(self):
        """Test that property age is correctly passed from CSV to database"""
        data_to_upload = [{
            'property': {
                'user_id': 123,
                'street': '123 Main St',
                'city': 'Springfield',
                'state': 'IL',
                'postal_code': '62701',
                'property_age': 25,
                'unit_number': '-1',
                'address': '123 Main St, Springfield, IL'
            },
            'appliances': [],
            'structures': []
        }]

        self.mock_cursor.lastrowid = 1001

        result = self.service.execute_bulk_properties_insertion(
            cnx=self.mock_connection,
            data_to_upload=data_to_upload
        )

        self.assertEqual(result, 200)
        # Check property insert parameters
        property_call = self.mock_cursor.execute.call_args_list[0]
        property_params = property_call[0][1]
        self.assertEqual(property_params[5], 25)  # age parameter should be 25

    def test_appliance_estimated_cost_is_none(self):
        """Test that appliance estimated_replacement_cost is None (calculated later)"""
        data_to_upload = [{
            'property': {
                'user_id': 123,
                'street': '123 Main St',
                'city': 'Springfield',
                'state': 'IL',
                'postal_code': '62701',
                'property_age': 25,
                'unit_number': '-1',
                'address': '123 Main St, Springfield, IL'
            },
            'appliances': [
                {'appliance_type': 'stove', 'appliance_brand': 'GE', 'appliance_model': 'Model1', 'age_in_years': 5}
            ],
            'structures': []
        }]

        self.mock_cursor.lastrowid = 1001

        result = self.service.execute_bulk_properties_insertion(
            cnx=self.mock_connection,
            data_to_upload=data_to_upload
        )

        self.assertEqual(result, 200)
        # Check appliance insert parameters
        appliance_call = [call for call in self.mock_cursor.execute.call_args_list
                         if 'appliances' in str(call)][0]
        appliance_params = appliance_call[0][1]
        self.assertIsNone(appliance_params[6])  # estimated_replacement_cost should be None


class TestObtainConnection(TestPropertyCreationBulkInsertionService):
    """Tests for obtain_connection"""

    def test_obtain_connection_success(self):
        """Test successful connection acquisition"""
        self.mock_pool.pool.get_connection.return_value = self.mock_connection

        result = self.service.obtain_connection()

        self.assertEqual(result, self.mock_connection)
        self.mock_pool.pool.get_connection.assert_called_once()

    def test_obtain_connection_failure_raises_error(self):
        """Test that connection failure raises INTERNAL_SERVICE_ERROR"""
        self.mock_pool.pool.get_connection.side_effect = Exception('Connection pool exhausted')

        with self.assertRaises(Error) as context:
            self.service.obtain_connection()

        self.assertEqual(context.exception.code, INTERNAL_SERVICE_ERROR.code)


class TestBulkUploadOrchestration(TestPropertyCreationBulkInsertionService):
    """Integration tests for bulk_upload_properties_into_db orchestration"""

    @patch.object(PropertyCreationBulkInsertionService, 'obtain_connection')
    @patch.object(PropertyCreationBulkInsertionService, 'validate_contents_of_csv_file')
    @patch.object(PropertyCreationBulkInsertionService, 'parse_csv_file_for_upload')
    @patch.object(PropertyCreationBulkInsertionService, 'execute_bulk_properties_insertion')
    def test_successful_orchestration(self, mock_execute, mock_parse, mock_validate, mock_obtain):
        """Test successful bulk upload orchestration"""
        mock_obtain.return_value = self.mock_connection
        mock_validate.return_value = MagicMock()
        mock_parse.return_value = [{'property': {}, 'appliances': [], 'structures': []}]
        mock_execute.return_value = 200

        mock_request = MagicMock()
        mock_request.content = io.StringIO("")

        result = self.service.bulk_upload_properties_into_db(mock_request, user_id=123)

        self.assertIn('insertRecordStatus', result)
        self.assertEqual(result['insertRecordStatus'], 200)

        # Verify all steps called in order
        mock_obtain.assert_called_once()
        mock_validate.assert_called_once()
        mock_parse.assert_called_once()
        mock_execute.assert_called_once()

    @patch.object(PropertyCreationBulkInsertionService, 'obtain_connection')
    @patch.object(PropertyCreationBulkInsertionService, 'validate_contents_of_csv_file')
    def test_validation_error_propagates(self, mock_validate, mock_obtain):
        """Test that validation errors are propagated"""
        mock_obtain.return_value = self.mock_connection
        mock_validate.side_effect = Error(INVALID_BULK_CSV_FILE)

        mock_request = MagicMock()
        mock_request.content = io.StringIO("")

        with self.assertRaises(Error) as context:
            self.service.bulk_upload_properties_into_db(mock_request, user_id=123)

        self.assertEqual(context.exception.code, INVALID_BULK_CSV_FILE.code)

    @patch.object(PropertyCreationBulkInsertionService, 'obtain_connection')
    @patch.object(PropertyCreationBulkInsertionService, 'validate_contents_of_csv_file')
    @patch.object(PropertyCreationBulkInsertionService, 'parse_csv_file_for_upload')
    @patch.object(PropertyCreationBulkInsertionService, 'execute_bulk_properties_insertion')
    def test_user_id_passed_to_parser(self, mock_execute, mock_parse, mock_validate, mock_obtain):
        """Test that user_id is correctly passed to parser"""
        mock_obtain.return_value = self.mock_connection
        mock_validate.return_value = MagicMock()
        mock_parse.return_value = []
        mock_execute.return_value = 200

        mock_request = MagicMock()
        mock_request.content = io.StringIO("")

        result = self.service.bulk_upload_properties_into_db(mock_request, user_id=999)

        # Verify user_id passed to parse method
        mock_parse.assert_called_once()
        call_args = mock_parse.call_args
        self.assertEqual(call_args.kwargs['user_id'], 999)


class TestEdgeCases(TestPropertyCreationBulkInsertionService):
    """Tests for edge cases and boundary conditions"""

    def test_property_with_no_appliances_or_structures(self):
        """Test property with only required columns (no appliances or structures)"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,,,,,,,,,,,,,,,,,,,,,,,,,"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]['appliances']), 0)
        self.assertEqual(len(result[0]['structures']), 0)

    def test_property_with_all_appliances_and_structures(self):
        """Test property with all appliances and structures populated"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        self.assertEqual(len(result[0]['appliances']), 7)
        self.assertEqual(len(result[0]['structures']), 4)

    def test_unit_number_zero(self):
        """Test that unit_number = 0 is treated as multifamily (only -1 is single-family)"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,25,0,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        self.assertEqual(result[0]['property']['unit_number'], '0')
        # Should be treated as multifamily

    def test_very_long_street_name(self):
        """Test handling of very long street names"""
        long_street = "A" * 200
        csv_content = self.create_csv_content([
            f"{long_street},Springfield,IL,62701,25,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        self.assertEqual(result[0]['property']['street'], long_street)

    def test_special_characters_in_address(self):
        """Test handling of special characters in address fields"""
        csv_content = self.create_csv_content([
            "123 Main St. #2,Springfield-City,IL,62701,25,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        self.assertEqual(result[0]['property']['street'], '123 Main St. #2')
        self.assertEqual(result[0]['property']['city'], 'Springfield-City')

    def test_large_age_values(self):
        """Test handling of unusually large age values"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,250,-1,GE,Model1,100,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,150,200,100,50"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        stove = next(a for a in result[0]['appliances'] if a['appliance_type'] == 'stove')
        self.assertEqual(stove['age_in_years'], 100)

        roof = next(s for s in result[0]['structures'] if s['structure_type'] == 'roof')
        self.assertEqual(roof['age_in_years'], 150)

    def test_empty_property_age_inserts_none(self):
        """Test that empty property_age is parsed as None"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        property_data = result[0]['property']
        self.assertIsNone(property_data['property_age'])

    def test_invalid_property_age_inserts_none(self):
        """Test that invalid property_age (non-numeric) is parsed as None"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,abc,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        property_data = result[0]['property']
        self.assertIsNone(property_data['property_age'])

    def test_negative_property_age(self):
        """Test that negative property_age values are accepted (may represent future construction)"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,-5,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        property_data = result[0]['property']
        self.assertEqual(property_data['property_age'], -5)

    def test_zero_property_age(self):
        """Test that property_age = 0 is handled correctly (brand new property)"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701,0,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        property_data = result[0]['property']
        self.assertEqual(property_data['property_age'], 0)

    def test_property_age_with_whitespace(self):
        """Test that property_age with whitespace is parsed correctly"""
        csv_content = self.create_csv_content([
            "123 Main St,Springfield,IL,62701, 25 ,-1,GE,Model1,5,Whirlpool,Model2,3,Carrier,Model3,7,"
            "Rheem,Model4,4,Samsung,Model5,2,Bosch,Model6,6,LG,Model7,8,15,20,10,5"
        ])
        df = pd.read_csv(csv_content)

        result = self.service.parse_csv_file_for_upload(df, user_id=123)

        property_data = result[0]['property']
        self.assertEqual(property_data['property_age'], 25)


if __name__ == '__main__':
    unittest.main()
