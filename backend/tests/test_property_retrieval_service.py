import unittest
from unittest.mock import MagicMock, patch
from backend.db.service.property_retrieval_service import PropertyRetrievalService
from common.logging.error.error import Error
from datetime import datetime


class TestPropertyRetrievalService(unittest.TestCase):
    """Test cases for PropertyRetrievalService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_pool = MagicMock()
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_pool.pool.get_connection.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.service = PropertyRetrievalService(self.mock_pool)


class TestFetchPropertyInformation(TestPropertyRetrievalService):
    """Tests for fetch_property_information method"""

    def test_fetch_all_properties_success(self):
        """Test fetching all properties for a user"""
        # Arrange
        user_id = 123
        created_at = datetime.now()
        properties_data = [
            (1, 123, 10, 'street1', 'city1', 'state1', '12345', '123 Main St', created_at, 0),
            (2, 123, 15, 'street2', 'city2', 'state2', '67890', '456 Oak Ave', created_at, 1)
        ]
        self.mock_cursor.fetchall.return_value = properties_data

        # Act
        result = self.service.fetch_property_information(user_id=user_id, retrieval_type='ALL')

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['user_id'], 123)
        self.assertEqual(result[0]['age'], 10)
        self.assertEqual(result[0]['postal_code'], '12345')
        self.assertEqual(result[0]['address'], '123 Main St')
        self.assertEqual(result[0]['isMultifamily'], False)
        self.assertEqual(result[1]['isMultifamily'], True)
        self.mock_connection.close.assert_called_once()

    def test_fetch_single_property_success(self):
        """Test fetching a single property by property_id"""
        # Arrange
        property_id = 1
        created_at = datetime.now()
        property_data = [
            (1, 123, 10, 'street', 'city', 'state', '12345', '123 Main St', created_at, 0)
        ]
        self.mock_cursor.fetchall.return_value = property_data

        # Act
        result = self.service.fetch_property_information(property_id=property_id, retrieval_type='SINGLE')

        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['user_id'], 123)
        self.assertEqual(result['age'], 10)
        self.assertEqual(result['postal_code'], '12345')
        self.assertEqual(result['address'], '123 Main St')
        self.assertEqual(result['isMultifamily'], False)
        self.mock_connection.close.assert_called_once()

    def test_fetch_appliances_for_property(self):
        """Test fetching appliances for a property"""
        # Arrange
        property_id = 1
        forecasted_date = datetime(2025, 6, 15)
        # Correct tuple order: id, property_id, appliance_type, brand, model, age, cost, forecasted_date, unit_id
        appliances_data = [
            (1, 1, 'refrigerator', 'LG', 'Model1', 3, 800.0, forecasted_date, None),
            (2, 1, 'stove', 'GE', 'Model2', 5, 500.0, None, None)
        ]
        self.mock_cursor.fetchall.return_value = appliances_data

        # Act
        result = self.service.fetch_property_information(property_id=property_id, retrieval_type='APPLIANCES')

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['property_id'], 1)
        self.assertEqual(result[0]['unit_id'], None)
        self.assertEqual(result[0]['appliance_type'], 'refrigerator')
        self.assertEqual(result[0]['applianceBrand'], 'LG')
        self.assertEqual(result[0]['applianceModel'], 'Model1')
        self.assertEqual(result[0]['age_in_years'], 3)
        self.assertEqual(result[0]['estimated_replacement_cost'], 800.0)
        self.assertEqual(result[0]['forecasted_replacement_date'], '2025-06-15 00:00:00')
        self.assertEqual(result[1]['forecasted_replacement_date'], 'TBD')
        self.mock_connection.close.assert_called_once()

    def test_fetch_appliances_with_unit_id(self):
        """Test that appliances with unit_id are properly formatted"""
        # Arrange
        property_id = 1
        forecasted_date = datetime(2025, 6, 15)
        # Correct tuple order: id, property_id, appliance_type, brand, model, age, cost, forecasted_date, unit_id
        appliances_data = [
            (1, 1, 'refrigerator', 'Samsung', 'RF28', 3, 850.0, forecasted_date, 100),
            (2, 1, 'stove', 'Whirlpool', 'WFE515S0ES', 2, 450.0, None, 101)
        ]
        self.mock_cursor.fetchall.return_value = appliances_data

        # Act
        result = self.service.fetch_property_information(property_id=property_id, retrieval_type='APPLIANCES')

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['unit_id'], 100)
        self.assertEqual(result[1]['unit_id'], 101)

    def test_fetch_structures_for_property(self):
        """Test fetching structures for a property"""
        # Arrange
        property_id = 1
        forecasted_date = datetime(2026, 12, 31)
        structures_data = [
            (1, 1, 'roof', 15, 5000.0, forecasted_date),
            (2, 1, 'furnace', 10, 3000.0, None)
        ]
        self.mock_cursor.fetchall.return_value = structures_data

        # Act
        result = self.service.fetch_property_information(property_id=property_id, retrieval_type='STRUCTURES')

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['property_id'], 1)
        self.assertEqual(result[0]['structure_type'], 'roof')
        self.assertEqual(result[0]['age_in_years'], 15)
        self.assertEqual(result[0]['estimated_replacement_cost'], 5000.0)
        self.assertEqual(result[0]['forecasted_replacement_date'], '2026-12-31 00:00:00')
        self.assertEqual(result[1]['forecasted_replacement_date'], 'TBD')
        self.mock_connection.close.assert_called_once()

    def test_fetch_addresses_for_user(self):
        """Test fetching addresses for a user"""
        # Arrange
        user_id = 123
        addresses_data = [
            (1, '123 Main St'),
            (2, '456 Oak Ave')
        ]
        self.mock_cursor.fetchall.return_value = addresses_data

        # Act
        result = self.service.fetch_property_information(user_id=user_id, retrieval_type='ADDRESSES')

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['property_id'], 1)
        self.assertEqual(result[0]['address'], '123 Main St')
        self.assertEqual(result[1]['property_id'], 2)
        self.assertEqual(result[1]['address'], '456 Oak Ave')
        self.mock_connection.close.assert_called_once()


class TestExecuteRetrievalStatement(TestPropertyRetrievalService):
    """Tests for execute_retrieval_statement static method"""

    def test_execute_retrieval_all_properties(self):
        """Test executing retrieval for all properties"""
        # Arrange
        user_id = 123
        retrieval_type = 'ALL'
        properties_data = [(1, 123, 10, 'street', 'city', 'state', '12345', '123 Main St', datetime.now(), 0)]
        self.mock_cursor.fetchall.return_value = properties_data

        # Act
        result = PropertyRetrievalService.execute_retrieval_statement(
            self.mock_connection, user_id, None, retrieval_type
        )

        # Assert
        self.assertEqual(result, properties_data)
        self.mock_cursor.close.assert_called_once()

    def test_execute_retrieval_single_property(self):
        """Test executing retrieval for a single property"""
        # Arrange
        property_id = 1
        retrieval_type = 'SINGLE'
        property_data = [(1, 123, 10, 'street', 'city', 'state', '12345', '123 Main St', datetime.now(), 0)]
        self.mock_cursor.fetchall.return_value = property_data

        # Act
        result = PropertyRetrievalService.execute_retrieval_statement(
            self.mock_connection, None, property_id, retrieval_type
        )

        # Assert
        self.assertEqual(result, property_data)

    def test_execute_retrieval_appliances(self):
        """Test executing retrieval for appliances"""
        # Arrange
        property_id = 1
        retrieval_type = 'APPLIANCES'
        # Correct tuple order: id, property_id, appliance_type, brand, model, age, cost, forecasted_date, unit_id
        appliances_data = [(1, 1, 'stove', 'GE', 'Model', 5, 500.0, None, None)]
        self.mock_cursor.fetchall.return_value = appliances_data

        # Act
        result = PropertyRetrievalService.execute_retrieval_statement(
            self.mock_connection, None, property_id, retrieval_type
        )

        # Assert
        self.assertEqual(result, appliances_data)

    def test_execute_retrieval_structures(self):
        """Test executing retrieval for structures"""
        # Arrange
        property_id = 1
        retrieval_type = 'STRUCTURES'
        structures_data = [(1, 1, 'roof', 15, 5000.0, None)]
        self.mock_cursor.fetchall.return_value = structures_data

        # Act
        result = PropertyRetrievalService.execute_retrieval_statement(
            self.mock_connection, None, property_id, retrieval_type
        )

        # Assert
        self.assertEqual(result, structures_data)

    def test_execute_retrieval_addresses(self):
        """Test executing retrieval for addresses"""
        # Arrange
        user_id = 123
        retrieval_type = 'ADDRESSES'
        addresses_data = [(1, '123 Main St')]
        self.mock_cursor.fetchall.return_value = addresses_data

        # Act
        result = PropertyRetrievalService.execute_retrieval_statement(
            self.mock_connection, user_id, None, retrieval_type
        )

        # Assert
        self.assertEqual(result, addresses_data)

    def test_execute_retrieval_database_error(self):
        """Test that database errors raise Error exception"""
        # Arrange
        self.mock_cursor.execute.side_effect = Exception('Database connection failed')

        # Act & Assert
        with self.assertRaises(Error):
            PropertyRetrievalService.execute_retrieval_statement(
                self.mock_connection, 123, None, 'ALL'
            )


class TestFormatPropertyResults(TestPropertyRetrievalService):
    """Tests for format_property_results static method"""

    def test_format_empty_results(self):
        """Test formatting empty results returns empty list"""
        # Arrange
        results = []

        # Act
        formatted = PropertyRetrievalService.format_property_results(results, 'ALL')

        # Assert
        self.assertEqual(formatted, [])

    def test_format_all_properties(self):
        """Test formatting results for ALL retrieval type"""
        # Arrange
        created_at = datetime.now()
        results = [
            (1, 123, 10, 'street1', 'city1', 'state1', '12345', '123 Main St', created_at, 0),
            (2, 123, 15, 'street2', 'city2', 'state2', '67890', '456 Oak Ave', created_at, 1)
        ]

        # Act
        formatted = PropertyRetrievalService.format_property_results(results, 'ALL')

        # Assert
        self.assertEqual(len(formatted), 2)
        self.assertEqual(formatted[0]['id'], 1)
        self.assertEqual(formatted[0]['user_id'], 123)
        self.assertEqual(formatted[0]['age'], 10)
        self.assertEqual(formatted[0]['postal_code'], '12345')
        self.assertEqual(formatted[0]['address'], '123 Main St')
        self.assertEqual(formatted[0]['isMultifamily'], False)
        self.assertEqual(formatted[1]['isMultifamily'], True)

    def test_format_single_property(self):
        """Test formatting results for SINGLE retrieval type"""
        # Arrange
        created_at = datetime.now()
        results = [
            (1, 123, 10, 'street', 'city', 'state', '12345', '123 Main St', created_at, 0)
        ]

        # Act
        formatted = PropertyRetrievalService.format_property_results(results, 'SINGLE')

        # Assert
        self.assertIsInstance(formatted, dict)
        self.assertEqual(formatted['id'], 1)
        self.assertEqual(formatted['user_id'], 123)
        self.assertEqual(formatted['isMultifamily'], False)

    def test_format_appliances_includes_unit_id_none(self):
        """Test that appliances formatting includes unit_id field when it's None"""
        # Arrange
        forecasted_date = datetime(2025, 6, 15)
        # Correct tuple order: id, property_id, appliance_type, brand, model, age, cost, forecasted_date, unit_id
        results = [
            (1, 1, 'refrigerator', 'LG', 'Model1', 3, 800.0, forecasted_date, None)
        ]

        # Act
        formatted = PropertyRetrievalService.format_property_results(results, 'APPLIANCES')

        # Assert
        self.assertEqual(len(formatted), 1)
        self.assertIn('unit_id', formatted[0])
        self.assertIsNone(formatted[0]['unit_id'])

    def test_format_appliances_includes_unit_id_with_value(self):
        """Test that appliances formatting includes unit_id field when it has a value"""
        # Arrange
        forecasted_date = datetime(2025, 6, 15)
        # Correct tuple order: id, property_id, appliance_type, brand, model, age, cost, forecasted_date, unit_id
        results = [
            (1, 1, 'refrigerator', 'LG', 'Model1', 3, 800.0, forecasted_date, 100),
            (2, 1, 'stove', 'GE', 'Model2', 5, 500.0, None, 101)
        ]

        # Act
        formatted = PropertyRetrievalService.format_property_results(results, 'APPLIANCES')

        # Assert
        self.assertEqual(len(formatted), 2)
        self.assertEqual(formatted[0]['unit_id'], 100)
        self.assertEqual(formatted[1]['unit_id'], 101)

    def test_format_appliances_mixed_unit_ids(self):
        """Test formatting appliances with both None and valued unit_ids"""
        # Arrange
        # Correct tuple order: id, property_id, appliance_type, brand, model, age, cost, forecasted_date, unit_id
        results = [
            (1, 1, 'dishwasher', 'Bosch', 'SHPM88', 2, 600.0, None, None),
            (2, 1, 'refrigerator', 'Samsung', 'RF28', 3, 850.0, None, 100),
            (3, 1, 'stove', 'GE', 'JB645', 4, 450.0, None, None)
        ]

        # Act
        formatted = PropertyRetrievalService.format_property_results(results, 'APPLIANCES')

        # Assert
        self.assertEqual(len(formatted), 3)
        self.assertIsNone(formatted[0]['unit_id'])
        self.assertEqual(formatted[1]['unit_id'], 100)
        self.assertIsNone(formatted[2]['unit_id'])

    def test_format_appliances_with_forecasted_date(self):
        """Test formatting appliances with forecasted replacement date"""
        # Arrange
        forecasted_date = datetime(2025, 6, 15, 10, 30, 0)
        # Correct tuple order: id, property_id, appliance_type, brand, model, age, cost, forecasted_date, unit_id
        results = [
            (1, 1, 'washer', 'Whirlpool', 'WFW5620', 4, 600.0, forecasted_date, None)
        ]

        # Act
        formatted = PropertyRetrievalService.format_property_results(results, 'APPLIANCES')

        # Assert
        self.assertEqual(formatted[0]['forecasted_replacement_date'], '2025-06-15 10:30:00')

    def test_format_appliances_without_forecasted_date(self):
        """Test formatting appliances without forecasted replacement date shows TBD"""
        # Arrange
        # Correct tuple order: id, property_id, appliance_type, brand, model, age, cost, forecasted_date, unit_id
        results = [
            (1, 1, 'dryer', 'LG', 'DLEX3900', 3, 500.0, None, None)
        ]

        # Act
        formatted = PropertyRetrievalService.format_property_results(results, 'APPLIANCES')

        # Assert
        self.assertEqual(formatted[0]['forecasted_replacement_date'], 'TBD')

    def test_format_structures(self):
        """Test formatting structures"""
        # Arrange
        forecasted_date = datetime(2026, 12, 31)
        results = [
            (1, 1, 'roof', 15, 5000.0, forecasted_date)
        ]

        # Act
        formatted = PropertyRetrievalService.format_property_results(results, 'STRUCTURES')

        # Assert
        self.assertEqual(len(formatted), 1)
        self.assertEqual(formatted[0]['id'], 1)
        self.assertEqual(formatted[0]['property_id'], 1)
        self.assertEqual(formatted[0]['structure_type'], 'roof')
        self.assertEqual(formatted[0]['forecasted_replacement_date'], '2026-12-31 00:00:00')

    def test_format_addresses(self):
        """Test formatting addresses"""
        # Arrange
        results = [
            (1, '123 Main St'),
            (2, '456 Oak Ave')
        ]

        # Act
        formatted = PropertyRetrievalService.format_property_results(results, 'ADDRESSES')

        # Assert
        self.assertEqual(len(formatted), 2)
        self.assertEqual(formatted[0]['property_id'], 1)
        self.assertEqual(formatted[0]['address'], '123 Main St')


class TestObtainConnection(TestPropertyRetrievalService):
    """Tests for obtain_connection method"""

    def test_obtain_connection_success(self):
        """Test successfully obtaining a database connection"""
        # Act
        result = self.service.obtain_connection()

        # Assert
        self.assertEqual(result, self.mock_connection)
        self.mock_pool.pool.get_connection.assert_called_once()

    def test_obtain_connection_pool_error(self):
        """Test that connection pool errors raise Error exception"""
        # Arrange
        self.mock_pool.pool.get_connection.side_effect = Exception('Connection pool exhausted')

        # Act & Assert
        with self.assertRaises(Error):
            self.service.obtain_connection()


if __name__ == '__main__':
    unittest.main()
