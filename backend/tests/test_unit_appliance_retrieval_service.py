import unittest
from unittest.mock import MagicMock, patch
from backend.db.service.unit_appliance_retrieval_service import UnitApplianceRetrievalService
from common.logging.error.error import Error
from datetime import datetime


class TestUnitApplianceRetrievalService(unittest.TestCase):
    """Test cases for UnitApplianceRetrievalService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_pool = MagicMock()
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_pool.pool.get_connection.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.service = UnitApplianceRetrievalService(self.mock_pool)

    def test_fetch_appliances_by_unit_id_success(self):
        """Test successfully fetching appliances for an authorized unit"""
        # Arrange
        unit_id = 100
        user_id = 456

        # Mock authorization check (returns unit data)
        authorization_result = (100,)
        self.mock_cursor.fetchone.return_value = authorization_result

        # Mock appliances retrieval (now 9 columns - removed created_at and updated_at)
        forecasted_date = datetime(2025, 6, 15, 0, 0, 0)
        appliances_data = [
            (1, 123, 100, 'refrigerator', 'LG', 'LFXS28968S', 3, 800.0, forecasted_date),
            (2, 123, 100, 'stove', 'GE', 'JB645RKSS', 5, 500.0, None),
            (3, 123, 100, 'dishwasher', 'Bosch', 'SHPM88Z75N', 2, 600.0, forecasted_date)
        ]

        # First call returns authorization, second call returns appliances
        self.mock_cursor.fetchone.side_effect = [authorization_result]
        self.mock_cursor.fetchall.return_value = appliances_data

        # Act
        result = self.service.fetch_appliances_by_unit_id(unit_id, user_id)

        # Assert
        self.assertEqual(len(result), 3)

        # Check refrigerator
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['property_id'], 123)
        self.assertEqual(result[0]['unit_id'], 100)
        self.assertEqual(result[0]['appliance_type'], 'refrigerator')
        self.assertEqual(result[0]['appliance_brand'], 'LG')
        self.assertEqual(result[0]['appliance_model'], 'LFXS28968S')
        self.assertEqual(result[0]['age_in_years'], 3)
        self.assertEqual(result[0]['estimated_replacement_cost'], 800.0)
        self.assertEqual(result[0]['forecasted_replacement_date'], '2025-06-15 00:00:00')

        # Check stove with None forecasted date
        self.assertEqual(result[1]['appliance_type'], 'stove')
        self.assertEqual(result[1]['forecasted_replacement_date'], 'TBD')

        # Check dishwasher
        self.assertEqual(result[2]['appliance_type'], 'dishwasher')

        self.mock_connection.close.assert_called_once()

    def test_fetch_appliances_unit_not_authorized(self):
        """Test returning empty list when unit doesn't belong to user's property"""
        # Arrange
        unit_id = 100
        user_id = 456

        # Mock authorization failure (returns None)
        self.mock_cursor.fetchone.return_value = None

        # Act
        result = self.service.fetch_appliances_by_unit_id(unit_id, user_id)

        # Assert
        self.assertEqual(result, [])
        self.mock_connection.close.assert_called_once()
        # Should not execute appliances query
        self.mock_cursor.fetchall.assert_not_called()

    def test_fetch_appliances_unit_has_no_appliances(self):
        """Test returning empty list when unit has no appliances"""
        # Arrange
        unit_id = 100
        user_id = 456

        # Mock authorization success
        authorization_result = (100,)
        self.mock_cursor.fetchone.return_value = authorization_result

        # Mock empty appliances result
        self.mock_cursor.fetchall.return_value = []

        # Act
        result = self.service.fetch_appliances_by_unit_id(unit_id, user_id)

        # Assert
        self.assertEqual(result, [])
        self.mock_connection.close.assert_called_once()

    def test_fetch_appliances_handles_null_values(self):
        """Test that null values in appliances are properly handled"""
        # Arrange
        unit_id = 100
        user_id = 456

        # Mock authorization
        self.mock_cursor.fetchone.return_value = (100,)

        # Mock appliance with null values (9 columns)
        appliances_data = [
            (1, 123, None, 'washer', None, None, 7, None, None)
        ]
        self.mock_cursor.fetchall.return_value = appliances_data

        # Act
        result = self.service.fetch_appliances_by_unit_id(unit_id, user_id)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['unit_id'], None)
        self.assertEqual(result[0]['appliance_brand'], None)
        self.assertEqual(result[0]['appliance_model'], None)
        self.assertEqual(result[0]['estimated_replacement_cost'], None)
        self.assertEqual(result[0]['forecasted_replacement_date'], 'TBD')

    def test_verify_unit_authorization_success(self):
        """Test verify_unit_authorization with valid authorization"""
        # Arrange
        unit_id = 100
        user_id = 456
        authorization_result = (100,)
        self.mock_cursor.fetchone.return_value = authorization_result

        # Act
        result = UnitApplianceRetrievalService.verify_unit_authorization(
            self.mock_connection, unit_id, user_id
        )

        # Assert
        self.assertTrue(result)
        self.mock_cursor.close.assert_called_once()

    def test_verify_unit_authorization_unauthorized(self):
        """Test verify_unit_authorization returns False when not authorized"""
        # Arrange
        unit_id = 100
        user_id = 456
        self.mock_cursor.fetchone.return_value = None

        # Act
        result = UnitApplianceRetrievalService.verify_unit_authorization(
            self.mock_connection, unit_id, user_id
        )

        # Assert
        self.assertFalse(result)
        self.mock_cursor.close.assert_called_once()

    def test_verify_unit_authorization_database_error(self):
        """Test verify_unit_authorization raises Error on database exception"""
        # Arrange
        unit_id = 100
        user_id = 456
        self.mock_cursor.execute.side_effect = Exception('Database error')

        # Act & Assert
        with self.assertRaises(Error):
            UnitApplianceRetrievalService.verify_unit_authorization(
                self.mock_connection, unit_id, user_id
            )

    def test_execute_retrieval_statement_success(self):
        """Test execute_retrieval_statement successfully fetches appliances"""
        # Arrange
        unit_id = 100
        appliances_data = [
            (1, 123, 100, 'refrigerator', 'Samsung', 'RF28', 3, 850.0, None)
        ]
        self.mock_cursor.fetchall.return_value = appliances_data

        # Act
        result = UnitApplianceRetrievalService.execute_retrieval_statement(
            self.mock_connection, unit_id
        )

        # Assert
        self.assertEqual(result, appliances_data)
        self.mock_cursor.execute.assert_called_once()
        self.mock_cursor.close.assert_called_once()

    def test_execute_retrieval_statement_database_error(self):
        """Test execute_retrieval_statement raises Error on database exception"""
        # Arrange
        unit_id = 100
        self.mock_cursor.execute.side_effect = Exception('Connection timeout')

        # Act & Assert
        with self.assertRaises(Error):
            UnitApplianceRetrievalService.execute_retrieval_statement(
                self.mock_connection, unit_id
            )

    def test_format_appliance_results_with_data(self):
        """Test format_appliance_results correctly formats database rows"""
        # Arrange
        forecasted_date = datetime(2025, 12, 31, 23, 59, 59)
        appliances_data = [
            (10, 5, 100, 'dryer', 'Whirlpool', 'WED5000DW', 4, 450.0, forecasted_date)
        ]

        # Act
        result = UnitApplianceRetrievalService.format_appliance_results(appliances_data)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 10)
        self.assertEqual(result[0]['property_id'], 5)
        self.assertEqual(result[0]['unit_id'], 100)
        self.assertEqual(result[0]['appliance_type'], 'dryer')
        self.assertEqual(result[0]['appliance_brand'], 'Whirlpool')
        self.assertEqual(result[0]['appliance_model'], 'WED5000DW')
        self.assertEqual(result[0]['age_in_years'], 4)
        self.assertEqual(result[0]['estimated_replacement_cost'], 450.0)
        self.assertEqual(result[0]['forecasted_replacement_date'], '2025-12-31 23:59:59')

    def test_format_appliance_results_empty_list(self):
        """Test format_appliance_results returns empty list for empty input"""
        # Arrange
        appliances_data = []

        # Act
        result = UnitApplianceRetrievalService.format_appliance_results(appliances_data)

        # Assert
        self.assertEqual(result, [])

    def test_format_appliance_results_multiple_appliances(self):
        """Test formatting multiple appliances correctly"""
        # Arrange
        appliances_data = [
            (1, 5, 100, 'stove', 'GE', 'Model1', 3, 500.0, None),
            (2, 5, 100, 'refrigerator', 'LG', 'Model2', 5, 800.0, None),
            (3, 5, 100, 'washer', 'Samsung', 'Model3', 2, 600.0, None)
        ]

        # Act
        result = UnitApplianceRetrievalService.format_appliance_results(appliances_data)

        # Assert
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['appliance_type'], 'stove')
        self.assertEqual(result[1]['appliance_type'], 'refrigerator')
        self.assertEqual(result[2]['appliance_type'], 'washer')

    def test_format_appliance_results_preserves_all_fields(self):
        """Test that all required fields are included in formatted results"""
        # Arrange
        appliances_data = [
            (1, 5, 100, 'ac_unit', 'Carrier', 'Model', 10, 3000.0, None)
        ]

        # Act
        result = UnitApplianceRetrievalService.format_appliance_results(appliances_data)

        # Assert
        self.assertEqual(len(result), 1)
        expected_keys = {
            'id', 'property_id', 'unit_id', 'appliance_type', 'appliance_brand',
            'appliance_model', 'age_in_years', 'estimated_replacement_cost',
            'forecasted_replacement_date'
        }
        self.assertEqual(set(result[0].keys()), expected_keys)

    def test_format_appliance_results_forecasted_date_formatting(self):
        """Test that forecasted_replacement_date is properly formatted"""
        # Arrange
        forecasted_date = datetime(2026, 3, 15, 12, 30, 45)
        appliances_data = [
            (1, 5, 100, 'water_heater', 'Rheem', 'XE50', 8, 700.0, forecasted_date)
        ]

        # Act
        result = UnitApplianceRetrievalService.format_appliance_results(appliances_data)

        # Assert
        self.assertEqual(result[0]['forecasted_replacement_date'], '2026-03-15 12:30:45')

    def test_format_appliance_results_tbd_for_null_date(self):
        """Test that null forecasted_replacement_date becomes 'TBD'"""
        # Arrange
        appliances_data = [
            (1, 5, 100, 'microwave', 'Panasonic', 'NN-SN966S', 3, 200.0, None)
        ]

        # Act
        result = UnitApplianceRetrievalService.format_appliance_results(appliances_data)

        # Assert
        self.assertEqual(result[0]['forecasted_replacement_date'], 'TBD')

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

    def test_fetch_appliances_connection_closed_on_success(self):
        """Test that database connection is properly closed after successful fetch"""
        # Arrange
        unit_id = 100
        user_id = 456
        self.mock_cursor.fetchone.return_value = (100,)
        self.mock_cursor.fetchall.return_value = []

        # Act
        self.service.fetch_appliances_by_unit_id(unit_id, user_id)

        # Assert
        self.mock_connection.close.assert_called_once()

    def test_fetch_appliances_connection_closed_on_unauthorized(self):
        """Test that database connection is properly closed when user is unauthorized"""
        # Arrange
        unit_id = 100
        user_id = 456
        self.mock_cursor.fetchone.return_value = None

        # Act
        self.service.fetch_appliances_by_unit_id(unit_id, user_id)

        # Assert
        self.mock_connection.close.assert_called_once()

    def test_format_appliance_results_handles_integer_conversion(self):
        """Test that unit_id handles None correctly when converting to int"""
        # Arrange
        # unit_id is None in the data
        appliances_data = [
            (5, 10, None, 'dishwasher', 'KitchenAid', 'KDTM354DSS', 4, 650.0, None)
        ]

        # Act
        result = UnitApplianceRetrievalService.format_appliance_results(appliances_data)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]['unit_id'])

    def test_format_appliance_results_handles_float_conversion(self):
        """Test that estimated_replacement_cost handles None correctly when converting to float"""
        # Arrange
        appliances_data = [
            (1, 5, 100, 'furnace', 'Trane', 'XV80', 12, None, None)
        ]

        # Act
        result = UnitApplianceRetrievalService.format_appliance_results(appliances_data)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]['estimated_replacement_cost'])


if __name__ == '__main__':
    unittest.main()
