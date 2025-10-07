import unittest
from unittest.mock import MagicMock, patch, call
from backend.db.service.property_creation_insertion_service import PropertyCreationInsertionService
from backend.db.model.property_creation_request import PropertyCreationRequest


class MockAppliances:
    """Mock class for Appliances to avoid MagicMock __dict__ issues"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockStructures:
    """Mock class for Structures to avoid MagicMock __dict__ issues"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockProperty:
    """Mock class for PropertyCreationRequest"""
    def __init__(self, is_multifamily=False, appliances=None, structures=None, units=None):
        self.is_multifamily = is_multifamily
        self.appliances = appliances
        self.structures = structures
        self.units = units


class TestPropertyCreationInsertionService(unittest.TestCase):
    """Test cases for PropertyCreationInsertionService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_pool = MagicMock()
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_pool.pool.get_connection.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.service = PropertyCreationInsertionService(self.mock_pool)


class TestUnitsInsertion(TestPropertyCreationInsertionService):
    """Tests for execute_insertion_statement_for_units_table"""

    def test_insert_units_for_single_family_property(self):
        """Test that single-family properties skip units insertion"""
        properties = {
            1: MagicMock(is_multifamily=False, units=None)
        }

        status, unit_id_mappings = self.service.execute_insertion_statement_for_units_table(
            cnx=self.mock_connection,
            properties=properties
        )

        self.assertEqual(status, 200)
        self.assertEqual(unit_id_mappings, {})
        self.mock_cursor.execute.assert_not_called()

    def test_insert_units_for_multifamily_with_single_unit(self):
        """Test inserting units for multifamily property with one unit"""
        mock_unit = MagicMock(unit_number='Unit 101')
        properties = {
            1: MagicMock(is_multifamily=True, units=[mock_unit])
        }
        self.mock_cursor.lastrowid = 100

        status, unit_id_mappings = self.service.execute_insertion_statement_for_units_table(
            cnx=self.mock_connection,
            properties=properties
        )

        self.assertEqual(status, 200)
        self.assertEqual(unit_id_mappings, {(1, 'Unit 101'): 100})
        self.mock_cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()

    def test_insert_units_for_multifamily_with_multiple_units(self):
        """Test inserting units for multifamily property with multiple units"""
        mock_unit1 = MagicMock(unit_number='Unit 1A')
        mock_unit2 = MagicMock(unit_number='Unit 1B')
        mock_unit3 = MagicMock(unit_number='Unit 2A')
        properties = {
            1: MagicMock(is_multifamily=True, units=[mock_unit1, mock_unit2, mock_unit3])
        }
        self.mock_cursor.lastrowid = None
        # Simulate different lastrowid values for each insert
        self.mock_cursor.configure_mock(**{'lastrowid': 100})
        lastrowids = [100, 101, 102]
        self.mock_cursor.lastrowid = None

        def side_effect_lastrowid(*args, **kwargs):
            if not hasattr(side_effect_lastrowid, 'call_count'):
                side_effect_lastrowid.call_count = 0
            result = lastrowids[side_effect_lastrowid.call_count]
            side_effect_lastrowid.call_count += 1
            return result

        type(self.mock_cursor).lastrowid = property(lambda self: side_effect_lastrowid())

        status, unit_id_mappings = self.service.execute_insertion_statement_for_units_table(
            cnx=self.mock_connection,
            properties=properties
        )

        self.assertEqual(status, 200)
        self.assertEqual(len(unit_id_mappings), 3)
        self.assertEqual(self.mock_cursor.execute.call_count, 3)
        self.assertEqual(self.mock_connection.commit.call_count, 3)

    def test_insert_units_for_multiple_multifamily_properties(self):
        """Test inserting units for multiple multifamily properties"""
        mock_unit1_prop1 = MagicMock(unit_number='Unit A')
        mock_unit1_prop2 = MagicMock(unit_number='Unit B')
        properties = {
            1: MagicMock(is_multifamily=True, units=[mock_unit1_prop1]),
            2: MagicMock(is_multifamily=True, units=[mock_unit1_prop2])
        }
        lastrowids = [100, 200]
        call_count = [0]

        def side_effect(*args, **kwargs):
            result = lastrowids[call_count[0]]
            call_count[0] += 1
            return result

        type(self.mock_cursor).lastrowid = property(lambda self: side_effect())

        status, unit_id_mappings = self.service.execute_insertion_statement_for_units_table(
            cnx=self.mock_connection,
            properties=properties
        )

        self.assertEqual(status, 200)
        self.assertEqual(len(unit_id_mappings), 2)
        self.assertEqual(self.mock_cursor.execute.call_count, 2)

    def test_insert_units_database_error_rollback(self):
        """Test that database errors trigger rollback"""
        mock_unit = MagicMock(unit_number='Unit 101')
        properties = {
            1: MagicMock(is_multifamily=True, units=[mock_unit])
        }
        self.mock_cursor.execute.side_effect = Exception('Database error')

        status, unit_id_mappings = self.service.execute_insertion_statement_for_units_table(
            cnx=self.mock_connection,
            properties=properties
        )

        self.assertEqual(status, 500)
        self.mock_connection.rollback.assert_called_once()

    def test_insert_units_returns_correct_mapping(self):
        """Test that unit_id mappings are returned correctly"""
        mock_unit = MagicMock(unit_number='Apt 5B')
        properties = {
            42: MagicMock(is_multifamily=True, units=[mock_unit])
        }
        self.mock_cursor.lastrowid = 999

        status, unit_id_mappings = self.service.execute_insertion_statement_for_units_table(
            cnx=self.mock_connection,
            properties=properties
        )

        self.assertEqual(status, 200)
        self.assertIn((42, 'Apt 5B'), unit_id_mappings)
        self.assertEqual(unit_id_mappings[(42, 'Apt 5B')], 999)


class TestAppliancesFormatting(TestPropertyCreationInsertionService):
    """Tests for format_appliances_for_table_insertion"""

    def test_format_appliances_single_family_property(self):
        """Test formatting appliances for single-family property (unit_id = NULL)"""
        mock_appliances = MockAppliances(
            stove=5,
            stove_brand='GE',
            stove_model='XYZ',
            refrigerator=3,
            refrigerator_brand=None,
            refrigerator_model=None,
            dishwasher=None
        )
        properties = {
            1: MockProperty(is_multifamily=False, appliances=mock_appliances, units=None)
        }
        unit_id_mappings = {}
        appliance_replacement_cost = {
            'STOVE': 500.0,
            'REFRIGERATOR': 800.0,
            'DISHWASHER': 400.0
        }

        result = self.service.format_appliances_for_table_insertion(
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost
        )

        self.assertEqual(len(result), 2)
        # Check stove entry
        stove_entry = [r for r in result if r[2] == 'stove'][0]
        self.assertEqual(stove_entry[0], 1)  # property_id
        self.assertIsNone(stove_entry[1])  # unit_id = NULL
        self.assertEqual(stove_entry[2], 'stove')  # appliance_type
        self.assertEqual(stove_entry[3], 'GE')  # brand
        self.assertEqual(stove_entry[4], 'XYZ')  # model
        self.assertEqual(stove_entry[5], 5)  # age
        self.assertEqual(stove_entry[6], 500.0)  # cost

        # Check refrigerator entry
        fridge_entry = [r for r in result if r[2] == 'refrigerator'][0]
        self.assertEqual(fridge_entry[0], 1)
        self.assertIsNone(fridge_entry[1])  # unit_id = NULL
        self.assertIsNone(fridge_entry[3])  # brand = None
        self.assertIsNone(fridge_entry[4])  # model = None

    def test_format_appliances_multifamily_property(self):
        """Test formatting appliances for multifamily property (unit_id populated)"""
        mock_appliances = MockAppliances(
            refrigerator=3,
            refrigerator_brand='Samsung',
            refrigerator_model='RF28',
            stove=None
        )
        mock_unit = MagicMock(unit_number='Unit 101', appliances=mock_appliances)
        properties = {
            1: MockProperty(is_multifamily=True, units=[mock_unit], appliances=None)
        }
        unit_id_mappings = {(1, 'Unit 101'): 100}
        appliance_replacement_cost = {'REFRIGERATOR': 800.0}

        result = self.service.format_appliances_for_table_insertion(
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost
        )

        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertEqual(entry[0], 1)  # property_id
        self.assertEqual(entry[1], 100)  # unit_id
        self.assertEqual(entry[2], 'refrigerator')
        self.assertEqual(entry[3], 'Samsung')
        self.assertEqual(entry[4], 'RF28')
        self.assertEqual(entry[5], 3)
        self.assertEqual(entry[6], 800.0)

    def test_format_appliances_multifamily_multiple_units(self):
        """Test formatting appliances for multifamily with multiple units"""
        mock_appliances1 = MockAppliances(
            stove=5,
            stove_brand=None,
            stove_model=None
        )
        mock_appliances2 = MockAppliances(
            refrigerator=2,
            refrigerator_brand='LG',
            refrigerator_model=None
        )
        mock_unit1 = MagicMock(unit_number='Unit 1A', appliances=mock_appliances1)
        mock_unit2 = MagicMock(unit_number='Unit 1B', appliances=mock_appliances2)
        properties = {
            1: MockProperty(is_multifamily=True, units=[mock_unit1, mock_unit2], appliances=None)
        }
        unit_id_mappings = {
            (1, 'Unit 1A'): 100,
            (1, 'Unit 1B'): 101
        }
        appliance_replacement_cost = {'STOVE': 500.0, 'REFRIGERATOR': 800.0}

        result = self.service.format_appliances_for_table_insertion(
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost
        )

        self.assertEqual(len(result), 2)
        # Check unit 1A stove
        stove_entry = [r for r in result if r[1] == 100][0]
        self.assertEqual(stove_entry[2], 'stove')
        self.assertEqual(stove_entry[1], 100)
        # Check unit 1B refrigerator
        fridge_entry = [r for r in result if r[1] == 101][0]
        self.assertEqual(fridge_entry[2], 'refrigerator')
        self.assertEqual(fridge_entry[1], 101)

    def test_format_appliances_tuple_structure(self):
        """Test that appliances tuple format is correct: (property_id, unit_id, type, brand, model, age, cost)"""
        mock_appliances = MockAppliances(
            washer=7,
            washer_brand='Whirlpool',
            washer_model='WFW5620HW'
        )
        properties = {
            42: MockProperty(is_multifamily=False, appliances=mock_appliances, units=None)
        }
        unit_id_mappings = {}
        appliance_replacement_cost = {'WASHER': 600.0}

        result = self.service.format_appliances_for_table_insertion(
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost
        )

        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertEqual(len(entry), 7)
        self.assertEqual(entry[0], 42)  # property_id
        self.assertIsNone(entry[1])  # unit_id
        self.assertEqual(entry[2], 'washer')  # appliance_type
        self.assertEqual(entry[3], 'Whirlpool')  # brand
        self.assertEqual(entry[4], 'WFW5620HW')  # model
        self.assertEqual(entry[5], 7)  # age
        self.assertEqual(entry[6], 600.0)  # cost

    def test_format_appliances_handles_missing_brand_model(self):
        """Test that missing brand/model are handled as None"""
        mock_appliances = MockAppliances(
            dryer=4,
            dryer_brand=None,
            dryer_model=None
        )
        properties = {
            1: MockProperty(is_multifamily=False, appliances=mock_appliances, units=None)
        }
        unit_id_mappings = {}
        appliance_replacement_cost = {'DRYER': 450.0}

        result = self.service.format_appliances_for_table_insertion(
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost
        )

        entry = result[0]
        self.assertIsNone(entry[3])  # brand should be None
        self.assertIsNone(entry[4])  # model should be None

    def test_format_appliances_water_heater_included(self):
        """Test that water_heater appliance is included in mappings"""
        mock_appliances = MockAppliances(
            water_heater=8,
            water_heater_brand='Rheem',
            water_heater_model='XE50'
        )
        properties = {
            1: MockProperty(is_multifamily=False, appliances=mock_appliances, units=None)
        }
        unit_id_mappings = {}
        appliance_replacement_cost = {'WATER_HEATER': 700.0}

        result = self.service.format_appliances_for_table_insertion(
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost
        )

        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertEqual(entry[2], 'water_heater')
        self.assertEqual(entry[3], 'Rheem')
        self.assertEqual(entry[6], 700.0)

    def test_format_appliances_skips_none_appliances(self):
        """Test that None appliances are skipped"""
        mock_appliances = MockAppliances(
            stove=5,
            stove_brand='GE',
            stove_model=None,
            dishwasher=None,
            dishwasher_brand=None,
            dishwasher_model=None,
            refrigerator=None,
            refrigerator_brand=None,
            refrigerator_model=None
        )
        properties = {
            1: MockProperty(is_multifamily=False, appliances=mock_appliances, units=None)
        }
        unit_id_mappings = {}
        appliance_replacement_cost = {'STOVE': 500.0}

        result = self.service.format_appliances_for_table_insertion(
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost
        )

        # Only stove should be included
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], 'stove')

    def test_format_appliances_unit_id_lookup_from_mappings(self):
        """Test that unit_id is correctly looked up from mappings for multifamily"""
        mock_appliances = MockAppliances(ac_unit=10, ac_unit_brand='Carrier', ac_unit_model='XYZ')
        mock_unit = MagicMock(unit_number='Apt 3C', appliances=mock_appliances)
        properties = {
            5: MockProperty(is_multifamily=True, units=[mock_unit], appliances=None)
        }
        unit_id_mappings = {(5, 'Apt 3C'): 777}
        appliance_replacement_cost = {'AC_UNIT': 3000.0}

        result = self.service.format_appliances_for_table_insertion(
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost
        )

        entry = result[0]
        self.assertEqual(entry[0], 5)  # property_id
        self.assertEqual(entry[1], 777)  # unit_id from mapping
        self.assertEqual(entry[2], 'ac_unit')

    def test_format_appliances_empty_properties(self):
        """Test formatting with no properties"""
        properties = {}
        unit_id_mappings = {}
        appliance_replacement_cost = {'STOVE': 500.0}

        result = self.service.format_appliances_for_table_insertion(
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost
        )

        self.assertEqual(result, [])

    def test_format_appliances_property_with_no_appliances(self):
        """Test property with appliances object but all None values"""
        mock_appliances = MockAppliances(
            stove=None,
            dishwasher=None,
            refrigerator=None
        )
        properties = {
            1: MockProperty(is_multifamily=False, appliances=mock_appliances, units=None)
        }
        unit_id_mappings = {}
        appliance_replacement_cost = {}

        result = self.service.format_appliances_for_table_insertion(
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost
        )

        self.assertEqual(result, [])


class TestResponseFormatting(TestPropertyCreationInsertionService):
    """Tests for format_property_creation_response"""

    def test_response_includes_units_status(self):
        """Test that response includes unitsRecordStatus"""
        response = self.service.format_property_creation_response(
            insert_property_record_status=200,
            insert_appliance_record_status=200,
            insert_structures_record_status=200,
            insert_units_status=200,
            property_data={},
            appliance_data=[],
            structure_data=[]
        )

        self.assertIn('unitsRecordStatus', response)
        self.assertEqual(response['unitsRecordStatus'], 200)

    def test_response_with_unit_id_in_appliance_data(self):
        """Test that response correctly parses appliance data with unit_id at index 1"""
        appliance_data = [
            (1, None, 'stove', 'GE', 'XYZ', 5, 500.0),  # Single-family: unit_id = None
            (2, 100, 'refrigerator', 'LG', 'ABC', 3, 800.0)  # Multifamily: unit_id = 100
        ]

        response = self.service.format_property_creation_response(
            insert_property_record_status=200,
            insert_appliance_record_status=200,
            insert_structures_record_status=200,
            insert_units_status=200,
            property_data={},
            appliance_data=appliance_data,
            structure_data=[]
        )

        # Verify property 1 has stove
        self.assertIn(1, response['appliancesTableResponse'])
        self.assertEqual(response['appliancesTableResponse'][1], [{'stove': 5}])

        # Verify property 2 has refrigerator
        self.assertIn(2, response['appliancesTableResponse'])
        self.assertEqual(response['appliancesTableResponse'][2], [{'refrigerator': 3}])

    def test_response_appliance_age_at_correct_index(self):
        """Test that appliance age is read from index 5 (shifted due to unit_id)"""
        appliance_data = [
            (1, None, 'washer', 'Whirlpool', 'WFW', 12, 600.0)
        ]

        response = self.service.format_property_creation_response(
            insert_property_record_status=200,
            insert_appliance_record_status=200,
            insert_structures_record_status=200,
            insert_units_status=200,
            property_data={},
            appliance_data=appliance_data,
            structure_data=[]
        )

        # Age should be 12 (at index 5)
        self.assertEqual(response['appliancesTableResponse'][1][0]['washer'], 12)

    def test_response_all_status_codes(self):
        """Test that all status codes are included in response"""
        response = self.service.format_property_creation_response(
            insert_property_record_status=200,
            insert_appliance_record_status=200,
            insert_structures_record_status=200,
            insert_units_status=200,
            property_data={},
            appliance_data=[],
            structure_data=[]
        )

        self.assertIn('propertyRecordStatus', response)
        self.assertIn('applianceRecordStatus', response)
        self.assertIn('applianceStructuresStatus', response)
        self.assertIn('unitsRecordStatus', response)


class TestIntegrationOrchestration(TestPropertyCreationInsertionService):
    """Integration tests for insert_properties_into_db orchestration"""

    @patch.object(PropertyCreationInsertionService, 'execute_insertion_statement_for_properties_table')
    @patch.object(PropertyCreationInsertionService, 'execute_insertion_statement_for_units_table')
    @patch.object(PropertyCreationInsertionService, 'execute_retrieval_statement_for_replacement_cost')
    @patch.object(PropertyCreationInsertionService, 'execute_insertion_statement_for_appliances_table')
    @patch.object(PropertyCreationInsertionService, 'execute_insertion_statement_for_structures_table')
    @patch.object(PropertyCreationInsertionService, 'format_property_creation_response')
    def test_single_family_orchestration(self, mock_format, mock_structures, mock_appliances,
                                        mock_replacement_cost, mock_units, mock_properties):
        """Test orchestration for single-family property"""
        user_id = 123
        property_requests = [MagicMock()]

        mock_properties.return_value = (200, {1: property_requests[0]})
        mock_units.return_value = (200, {})
        mock_replacement_cost.return_value = {'STOVE': 500.0}
        mock_appliances.return_value = (200, [(1, None, 'stove', None, None, 5, 500.0)])
        mock_structures.return_value = (200, [(1, 'roof', 10)])
        mock_format.return_value = {'status': 'success'}

        result = self.service.insert_properties_into_db(user_id, property_requests)

        # Verify all steps called in order
        mock_properties.assert_called_once()
        mock_units.assert_called_once()
        mock_replacement_cost.assert_called_once()
        mock_appliances.assert_called_once()
        mock_structures.assert_called_once()
        mock_format.assert_called_once()

    @patch.object(PropertyCreationInsertionService, 'execute_insertion_statement_for_properties_table')
    @patch.object(PropertyCreationInsertionService, 'execute_insertion_statement_for_units_table')
    @patch.object(PropertyCreationInsertionService, 'execute_retrieval_statement_for_replacement_cost')
    @patch.object(PropertyCreationInsertionService, 'execute_insertion_statement_for_appliances_table')
    @patch.object(PropertyCreationInsertionService, 'execute_insertion_statement_for_structures_table')
    @patch.object(PropertyCreationInsertionService, 'format_property_creation_response')
    def test_multifamily_orchestration(self, mock_format, mock_structures, mock_appliances,
                                      mock_replacement_cost, mock_units, mock_properties):
        """Test orchestration for multifamily property"""
        user_id = 456
        property_requests = [MagicMock()]

        mock_properties.return_value = (200, {1: property_requests[0]})
        mock_units.return_value = (200, {(1, 'Unit 101'): 100})
        mock_replacement_cost.return_value = {'REFRIGERATOR': 800.0}
        mock_appliances.return_value = (200, [(1, 100, 'refrigerator', 'LG', None, 3, 800.0)])
        mock_structures.return_value = (200, [(1, 'roof', 15)])
        mock_format.return_value = {'status': 'success'}

        result = self.service.insert_properties_into_db(user_id, property_requests)

        # Verify units were inserted
        mock_units.assert_called_once()
        # Verify unit_id_mappings passed to appliances formatting
        call_args = mock_appliances.call_args
        self.assertIn('unit_id_mappings', call_args.kwargs)
        self.assertEqual(call_args.kwargs['unit_id_mappings'], {(1, 'Unit 101'): 100})

    def test_structures_always_property_level(self):
        """Test that structures are always at property-level (unit_id = NULL)"""
        # Test that format_structures_for_table_insertion signature doesn't include unit_id_mappings
        mock_structures = MockStructures(roof=20, water_heater=10)
        properties = {1: MockProperty(structures=mock_structures)}

        result = self.service.format_structures_for_table_insertion(properties=properties)

        # Verify structures are formatted correctly with only property_id (no unit_id)
        self.assertEqual(len(result), 2)
        for entry in result:
            self.assertEqual(len(entry), 3)  # Only (property_id, structure_type, age)
            self.assertIsInstance(entry[0], int)  # property_id
            self.assertIsInstance(entry[1], str)  # structure_type
            self.assertIsInstance(entry[2], int)  # age


class TestStructuresFormatting(TestPropertyCreationInsertionService):
    """Tests for format_structures_for_table_insertion"""

    def test_format_structures_single_family(self):
        """Test structures formatting for single-family property"""
        mock_structures = MockStructures(roof=10, furnace=8)
        properties = {1: MockProperty(structures=mock_structures)}

        result = self.service.format_structures_for_table_insertion(properties=properties)

        self.assertEqual(len(result), 2)
        self.assertIn((1, 'roof', 10), result)
        self.assertIn((1, 'furnace', 8), result)

    def test_format_structures_multifamily(self):
        """Test structures formatting for multifamily property (always property-level)"""
        mock_structures = MockStructures(roof=20, water_heater=12)
        properties = {1: MockProperty(structures=mock_structures)}

        result = self.service.format_structures_for_table_insertion(properties=properties)

        # Structures should have property_id but no unit_id
        self.assertEqual(len(result), 2)
        for entry in result:
            self.assertEqual(len(entry), 3)  # (property_id, structure_type, age)
            self.assertEqual(entry[0], 1)  # property_id

    def test_format_structures_skips_none_values(self):
        """Test that None structure values are skipped"""
        mock_structures = MockStructures(roof=10, driveway=None, furnace=None)
        properties = {1: MockProperty(structures=mock_structures)}

        result = self.service.format_structures_for_table_insertion(properties=properties)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (1, 'roof', 10))


if __name__ == '__main__':
    unittest.main()
