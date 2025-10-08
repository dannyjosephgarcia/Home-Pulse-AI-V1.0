import unittest
from unittest.mock import MagicMock, patch
from backend.db.service.unit_retrieval_service import UnitRetrievalService
from common.logging.error.error import Error
from datetime import datetime


class TestUnitRetrievalService(unittest.TestCase):
    """Test cases for UnitRetrievalService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_pool = MagicMock()
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_pool.pool.get_connection.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.service = UnitRetrievalService(self.mock_pool)

    def test_fetch_units_by_property_id_success(self):
        """Test successfully fetching units for a property owned by the user"""
        # Arrange
        property_id = 123
        user_id = 456

        # Mock property ownership verification (returns property data)
        property_data = (123, 456, 10, 'street', 'city', 'state', '12345', '123 Main St',
                        datetime.now(), datetime.now())
        self.mock_cursor.fetchone.return_value = property_data

        # Mock units retrieval
        units_data = [
            (1, 'Unit 101', 123, datetime(2024, 1, 1), datetime(2024, 1, 1)),
            (2, 'Unit 102', 123, datetime(2024, 1, 1), datetime(2024, 1, 1)),
            (3, 'Unit 103', 123, datetime(2024, 1, 1), datetime(2024, 1, 1))
        ]

        # First call returns property, second call returns units
        self.mock_cursor.fetchone.side_effect = [property_data]
        self.mock_cursor.fetchall.return_value = units_data

        # Act
        result = self.service.fetch_units_by_property_id(property_id, user_id)

        # Assert
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['unit_id'], 1)
        self.assertEqual(result[0]['unit_number'], 'Unit 101')
        self.assertEqual(result[0]['property_id'], 123)
        self.assertIn('created_at', result[0])
        self.assertIn('updated_at', result[0])
        self.assertEqual(result[1]['unit_number'], 'Unit 102')
        self.assertEqual(result[2]['unit_number'], 'Unit 103')
        self.mock_connection.close.assert_called_once()

    def test_fetch_units_property_not_owned_by_user(self):
        """Test returning empty list when property doesn't belong to user"""
        # Arrange
        property_id = 123
        user_id = 456
        different_user_id = 999

        # Mock property data with different user_id
        property_data = (123, different_user_id, 10, 'street', 'city', 'state', '12345',
                        '123 Main St', datetime.now(), datetime.now())
        self.mock_cursor.fetchone.return_value = property_data

        # Act
        result = self.service.fetch_units_by_property_id(property_id, user_id)

        # Assert
        self.assertEqual(result, [])
        self.mock_connection.close.assert_called_once()
        # Should not execute units query
        self.mock_cursor.fetchall.assert_not_called()

    def test_fetch_units_property_not_found(self):
        """Test returning empty list when property doesn't exist"""
        # Arrange
        property_id = 999
        user_id = 456

        # Mock property not found
        self.mock_cursor.fetchone.return_value = None

        # Act
        result = self.service.fetch_units_by_property_id(property_id, user_id)

        # Assert
        self.assertEqual(result, [])
        self.mock_connection.close.assert_called_once()
        self.mock_cursor.fetchall.assert_not_called()

    def test_fetch_units_property_has_no_units(self):
        """Test returning empty list when property has no units"""
        # Arrange
        property_id = 123
        user_id = 456

        # Mock property ownership verification
        property_data = (123, 456, 10, 'street', 'city', 'state', '12345', '123 Main St',
                        datetime.now(), datetime.now())
        self.mock_cursor.fetchone.return_value = property_data

        # Mock empty units result
        self.mock_cursor.fetchall.return_value = []

        # Act
        result = self.service.fetch_units_by_property_id(property_id, user_id)

        # Assert
        self.assertEqual(result, [])
        self.mock_connection.close.assert_called_once()

    def test_fetch_units_ordered_by_unit_number(self):
        """Test that units are returned ordered by unit_number"""
        # Arrange
        property_id = 123
        user_id = 456

        # Mock property ownership
        property_data = (123, 456, 10, 'street', 'city', 'state', '12345', '123 Main St',
                        datetime.now(), datetime.now())
        self.mock_cursor.fetchone.return_value = property_data

        # Mock units data in specific order (should be ordered by SQL query)
        units_data = [
            (5, 'Unit 101', 123, datetime(2024, 1, 1), datetime(2024, 1, 1)),
            (3, 'Unit 102', 123, datetime(2024, 1, 1), datetime(2024, 1, 1)),
            (7, 'Unit 201', 123, datetime(2024, 1, 1), datetime(2024, 1, 1)),
            (1, 'Unit 202', 123, datetime(2024, 1, 1), datetime(2024, 1, 1))
        ]
        self.mock_cursor.fetchall.return_value = units_data

        # Act
        result = self.service.fetch_units_by_property_id(property_id, user_id)

        # Assert - Order maintained from SQL query
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0]['unit_number'], 'Unit 101')
        self.assertEqual(result[1]['unit_number'], 'Unit 102')
        self.assertEqual(result[2]['unit_number'], 'Unit 201')
        self.assertEqual(result[3]['unit_number'], 'Unit 202')

    def test_verify_property_ownership_success(self):
        """Test verify_property_ownership static method with valid ownership"""
        # Arrange
        property_id = 123
        user_id = 456
        property_data = (123, 456, 10, 'street', 'city', 'state', '12345', '123 Main St',
                        datetime.now(), datetime.now())
        self.mock_cursor.fetchone.return_value = property_data

        # Act
        result = UnitRetrievalService.verify_property_ownership(
            self.mock_connection, property_id, user_id
        )

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result, property_data)
        self.mock_cursor.close.assert_called_once()

    def test_verify_property_ownership_wrong_user(self):
        """Test verify_property_ownership returns None when user doesn't own property"""
        # Arrange
        property_id = 123
        user_id = 456
        wrong_user_id = 999
        property_data = (123, wrong_user_id, 10, 'street', 'city', 'state', '12345',
                        '123 Main St', datetime.now(), datetime.now())
        self.mock_cursor.fetchone.return_value = property_data

        # Act
        result = UnitRetrievalService.verify_property_ownership(
            self.mock_connection, property_id, user_id
        )

        # Assert
        self.assertIsNone(result)

    def test_verify_property_ownership_property_not_found(self):
        """Test verify_property_ownership returns None when property doesn't exist"""
        # Arrange
        property_id = 999
        user_id = 456
        self.mock_cursor.fetchone.return_value = None

        # Act
        result = UnitRetrievalService.verify_property_ownership(
            self.mock_connection, property_id, user_id
        )

        # Assert
        self.assertIsNone(result)

    def test_verify_property_ownership_database_error(self):
        """Test verify_property_ownership raises Error on database exception"""
        # Arrange
        property_id = 123
        user_id = 456
        self.mock_cursor.execute.side_effect = Exception('Database error')

        # Act & Assert
        with self.assertRaises(Error) as context:
            UnitRetrievalService.verify_property_ownership(
                self.mock_connection, property_id, user_id
            )

    def test_execute_retrieval_statement_success(self):
        """Test execute_retrieval_statement successfully fetches units"""
        # Arrange
        property_id = 123
        units_data = [
            (1, 'Unit A', 123, datetime.now(), datetime.now()),
            (2, 'Unit B', 123, datetime.now(), datetime.now())
        ]
        self.mock_cursor.fetchall.return_value = units_data

        # Act
        result = UnitRetrievalService.execute_retrieval_statement(
            self.mock_connection, property_id
        )

        # Assert
        self.assertEqual(result, units_data)
        self.mock_cursor.execute.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_execute_retrieval_statement_database_error(self):
        """Test execute_retrieval_statement raises Error on database exception"""
        # Arrange
        property_id = 123
        self.mock_cursor.execute.side_effect = Exception('Database connection lost')

        # Act & Assert
        with self.assertRaises(Error) as context:
            UnitRetrievalService.execute_retrieval_statement(
                self.mock_connection, property_id
            )

    def test_format_unit_results_with_data(self):
        """Test format_unit_results correctly formats database rows"""
        # Arrange
        created_at = datetime(2024, 1, 1, 10, 0, 0)
        updated_at = datetime(2024, 1, 15, 14, 30, 0)
        units_data = [
            (10, 'Apt 1A', 5, created_at, updated_at),
            (20, 'Apt 1B', 5, created_at, updated_at)
        ]

        # Act
        result = UnitRetrievalService.format_unit_results(units_data)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['unit_id'], 10)
        self.assertEqual(result[0]['unit_number'], 'Apt 1A')
        self.assertEqual(result[0]['property_id'], 5)
        self.assertEqual(result[0]['created_at'], created_at)
        self.assertEqual(result[0]['updated_at'], updated_at)

    def test_format_unit_results_empty_list(self):
        """Test format_unit_results returns empty list for empty input"""
        # Arrange
        units_data = []

        # Act
        result = UnitRetrievalService.format_unit_results(units_data)

        # Assert
        self.assertEqual(result, [])

    def test_format_unit_results_preserves_all_fields(self):
        """Test that all required fields are included in formatted results"""
        # Arrange
        created_at = datetime(2024, 1, 1)
        updated_at = datetime(2024, 1, 2)
        units_data = [(1, 'Unit 5C', 100, created_at, updated_at)]

        # Act
        result = UnitRetrievalService.format_unit_results(units_data)

        # Assert
        self.assertEqual(len(result), 1)
        expected_keys = {'unit_id', 'unit_number', 'property_id', 'created_at', 'updated_at'}
        self.assertEqual(set(result[0].keys()), expected_keys)

    def test_obtain_connection_success(self):
        """Test obtain_connection successfully retrieves connection from pool"""
        # Act
        result = self.service.obtain_connection()

        # Assert
        self.assertEqual(result, self.mock_connection)
        self.mock_pool.pool.get_connection.assert_called_once()

    def test_obtain_connection_pool_error(self):
        """Test obtain_connection raises Error when pool fails"""
        # Arrange
        self.mock_pool.pool.get_connection.side_effect = Exception('Pool exhausted')

        # Act & Assert
        with self.assertRaises(Error):
            self.service.obtain_connection()

    def test_fetch_units_connection_closed_on_success(self):
        """Test that database connection is properly closed after successful fetch"""
        # Arrange
        property_id = 123
        user_id = 456
        property_data = (123, 456, 10, 'street', 'city', 'state', '12345', '123 Main St',
                        datetime.now(), datetime.now())
        self.mock_cursor.fetchone.return_value = property_data
        self.mock_cursor.fetchall.return_value = []

        # Act
        self.service.fetch_units_by_property_id(property_id, user_id)

        # Assert
        self.mock_connection.close.assert_called_once()

    def test_fetch_units_connection_closed_on_unauthorized(self):
        """Test that database connection is properly closed when user is unauthorized"""
        # Arrange
        property_id = 123
        user_id = 456
        self.mock_cursor.fetchone.return_value = None

        # Act
        self.service.fetch_units_by_property_id(property_id, user_id)

        # Assert
        self.mock_connection.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
