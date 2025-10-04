import unittest
from backend.db.model.tenant_creation_request import TenantCreationRequest
from common.logging.error.error import Error


class TestTenantCreationRequest(unittest.TestCase):

    def test_valid_request(self):
        """Test creating a valid TenantCreationRequest"""
        property_id = 123
        request = {
            'first_name': 'John',
            'last_name': 'Doe',
            'contract_start_date': '2024-01-01',
            'contract_end_date': '2024-12-31',
            'current_rent': 1500.00,
            'phone_number': '555-1234'
        }

        obj = TenantCreationRequest(property_id, request)

        self.assertEqual(obj.property_id, 123)
        self.assertEqual(obj.first_name, 'John')
        self.assertEqual(obj.last_name, 'Doe')
        self.assertEqual(obj.contract_start_date, '2024-01-01')
        self.assertEqual(obj.contract_end_date, '2024-12-31')
        self.assertEqual(obj.current_rent, 1500.00)
        self.assertEqual(obj.phone_number, '555-1234')

    def test_missing_first_name_field(self):
        """Test that Error is raised when first_name field is missing"""
        property_id = 123
        request = {
            'last_name': 'Doe',
            'contract_start_date': '2024-01-01',
            'contract_end_date': '2024-12-31',
            'current_rent': 1500.00,
            'phone_number': '555-1234'
        }

        with self.assertRaises(Error):
            TenantCreationRequest(property_id, request)

    def test_missing_last_name_field(self):
        """Test that Error is raised when last_name field is missing"""
        property_id = 123
        request = {
            'first_name': 'John',
            'contract_start_date': '2024-01-01',
            'contract_end_date': '2024-12-31',
            'current_rent': 1500.00,
            'phone_number': '555-1234'
        }

        with self.assertRaises(Error):
            TenantCreationRequest(property_id, request)

    def test_missing_contract_start_date_field(self):
        """Test that Error is raised when contract_start_date field is missing"""
        property_id = 123
        request = {
            'first_name': 'John',
            'last_name': 'Doe',
            'contract_end_date': '2024-12-31',
            'current_rent': 1500.00,
            'phone_number': '555-1234'
        }

        with self.assertRaises(Error):
            TenantCreationRequest(property_id, request)

    def test_missing_contract_end_date_field(self):
        """Test that Error is raised when contract_end_date field is missing"""
        property_id = 123
        request = {
            'first_name': 'John',
            'last_name': 'Doe',
            'contract_start_date': '2024-01-01',
            'current_rent': 1500.00,
            'phone_number': '555-1234'
        }

        with self.assertRaises(Error):
            TenantCreationRequest(property_id, request)

    def test_missing_current_rent_field(self):
        """Test that Error is raised when current_rent field is missing"""
        property_id = 123
        request = {
            'first_name': 'John',
            'last_name': 'Doe',
            'contract_start_date': '2024-01-01',
            'contract_end_date': '2024-12-31',
            'phone_number': '555-1234'
        }

        with self.assertRaises(Error):
            TenantCreationRequest(property_id, request)

    def test_missing_phone_number_field(self):
        """Test that Error is raised when phone_number field is missing"""
        property_id = 123
        request = {
            'first_name': 'John',
            'last_name': 'Doe',
            'contract_start_date': '2024-01-01',
            'contract_end_date': '2024-12-31',
            'current_rent': 1500.00
        }

        with self.assertRaises(Error):
            TenantCreationRequest(property_id, request)

    def test_invalid_contract_start_date_format(self):
        """Test that Error is raised when contract_start_date has invalid format"""
        property_id = 123
        request = {
            'first_name': 'John',
            'last_name': 'Doe',
            'contract_start_date': '01/01/2024',
            'contract_end_date': '2024-12-31',
            'current_rent': 1500.00,
            'phone_number': '555-1234'
        }

        with self.assertRaises(Error):
            TenantCreationRequest(property_id, request)

    def test_property_id_conversion_to_int(self):
        """Test that property_id is converted to int"""
        property_id = '456'
        request = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'contract_start_date': '2024-06-01',
            'contract_end_date': '2025-05-31',
            'current_rent': 2000.00,
            'phone_number': '555-5678'
        }

        obj = TenantCreationRequest(property_id, request)
        self.assertEqual(obj.property_id, 456)
        self.assertIsInstance(obj.property_id, int)


if __name__ == '__main__':
    unittest.main()
