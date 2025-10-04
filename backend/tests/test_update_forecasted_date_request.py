import unittest
import datetime
from backend.db.model.update_forecasted_date_request import UpdateForecastedDateRequest
from common.logging.error.error import Error


class TestUpdateForecastedDateRequest(unittest.TestCase):

    def test_valid_request(self):
        """Test creating a valid UpdateForecastedDateRequest"""
        property_id = 123
        request = {
            'applianceType': 'refrigerator',
            'forecastedReplacementDate': '2025-06-15'
        }

        obj = UpdateForecastedDateRequest(property_id, request)

        self.assertEqual(obj.property_id, property_id)
        self.assertEqual(obj.appliance_type, 'refrigerator')
        self.assertEqual(obj.forecasted_replacement_date, datetime.datetime(2025, 6, 15))

    def test_missing_appliance_type_field(self):
        """Test that Error is raised when applianceType field is missing"""
        property_id = 123
        request = {
            'forecastedReplacementDate': '2025-06-15'
        }

        with self.assertRaises(Error):
            UpdateForecastedDateRequest(property_id, request)

    def test_missing_forecasted_replacement_date_field(self):
        """Test that Error is raised when forecastedReplacementDate field is missing"""
        property_id = 123
        request = {
            'applianceType': 'refrigerator'
        }

        with self.assertRaises(Error):
            UpdateForecastedDateRequest(property_id, request)

    def test_property_id_not_integer(self):
        """Test that Error is raised when property_id is not an integer"""
        property_id = "not_an_int"
        request = {
            'applianceType': 'refrigerator',
            'forecastedReplacementDate': '2025-06-15'
        }

        with self.assertRaises(Error):
            UpdateForecastedDateRequest(property_id, request)

    def test_appliance_type_not_string(self):
        """Test that Error is raised when applianceType is not a string"""
        property_id = 123
        request = {
            'applianceType': 12345,
            'forecastedReplacementDate': '2025-06-15'
        }

        with self.assertRaises(Error):
            UpdateForecastedDateRequest(property_id, request)

    def test_invalid_date_format(self):
        """Test that Error is raised when date format is invalid"""
        property_id = 123
        request = {
            'applianceType': 'refrigerator',
            'forecastedReplacementDate': '06/15/2025'
        }

        with self.assertRaises(Error):
            UpdateForecastedDateRequest(property_id, request)

    def test_invalid_date_format_month_day_swapped(self):
        """Test that Error is raised when date format has wrong order"""
        property_id = 123
        request = {
            'applianceType': 'washer',
            'forecastedReplacementDate': '15-06-2025'
        }

        with self.assertRaises(Error):
            UpdateForecastedDateRequest(property_id, request)

    def test_date_parsing_edge_case(self):
        """Test date parsing with edge case dates"""
        property_id = 456
        request = {
            'applianceType': 'dryer',
            'forecastedReplacementDate': '2024-12-31'
        }

        obj = UpdateForecastedDateRequest(property_id, request)
        self.assertEqual(obj.forecasted_replacement_date, datetime.datetime(2024, 12, 31))

    def test_leap_year_date(self):
        """Test date parsing with leap year date"""
        property_id = 789
        request = {
            'applianceType': 'stove',
            'forecastedReplacementDate': '2024-02-29'
        }

        obj = UpdateForecastedDateRequest(property_id, request)
        self.assertEqual(obj.forecasted_replacement_date, datetime.datetime(2024, 2, 29))


if __name__ == '__main__':
    unittest.main()
