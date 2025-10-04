import unittest
from backend.db.model.update_tenant_information_request import UpdateTenantInformationRequest
from common.logging.error.error import Error


class TestUpdateTenantInformationRequest(unittest.TestCase):

    def test_valid_request_with_all_fields(self):
        """Test creating a valid UpdateTenantInformationRequest with all fields"""
        tenant_id = 1
        property_id = 123
        request = {
            'first_name': 'John',
            'last_name': 'Doe',
            'contract_start_date': '2024-01-01',
            'contract_end_date': '2024-12-31',
            'contract_status': 'active',
            'recommended_replacement_date': '2025-01-01',
            'monthly_rent': 1500.00,
            'phone_number': '555-1234'
        }

        obj = UpdateTenantInformationRequest(tenant_id, property_id, request)

        self.assertEqual(obj.tenant_id, tenant_id)
        self.assertEqual(obj.property_id, property_id)
        self.assertEqual(obj.first_name, 'John')
        self.assertEqual(obj.last_name, 'Doe')
        self.assertEqual(obj.contract_start_date, '2024-01-01')
        self.assertEqual(obj.contract_end_date, '2024-12-31')
        self.assertEqual(obj.contract_status, 'active')
        self.assertEqual(obj.recommended_replacement_date, '2025-01-01')
        self.assertEqual(obj.monthly_rent, 1500.00)
        self.assertEqual(obj.phone_number, '555-1234')

    def test_valid_request_with_partial_fields(self):
        """Test creating UpdateTenantInformationRequest with only some fields"""
        tenant_id = 2
        property_id = 456
        request = {
            'first_name': 'Jane',
            'monthly_rent': 2000.00
        }

        obj = UpdateTenantInformationRequest(tenant_id, property_id, request)

        self.assertEqual(obj.tenant_id, tenant_id)
        self.assertEqual(obj.property_id, property_id)
        self.assertEqual(obj.first_name, 'Jane')
        self.assertIsNone(obj.last_name)
        self.assertIsNone(obj.contract_start_date)
        self.assertIsNone(obj.contract_end_date)
        self.assertIsNone(obj.contract_status)
        self.assertIsNone(obj.recommended_replacement_date)
        self.assertEqual(obj.monthly_rent, 2000.00)
        self.assertIsNone(obj.phone_number)

    def test_empty_request(self):
        """Test creating UpdateTenantInformationRequest with empty request"""
        tenant_id = 3
        property_id = 789
        request = {}

        obj = UpdateTenantInformationRequest(tenant_id, property_id, request)

        self.assertEqual(obj.tenant_id, tenant_id)
        self.assertEqual(obj.property_id, property_id)
        self.assertIsNone(obj.first_name)
        self.assertIsNone(obj.last_name)
        self.assertIsNone(obj.contract_start_date)
        self.assertIsNone(obj.contract_end_date)
        self.assertIsNone(obj.contract_status)
        self.assertIsNone(obj.recommended_replacement_date)
        self.assertIsNone(obj.monthly_rent)
        self.assertIsNone(obj.phone_number)

    def test_id_not_integer(self):
        """Test that Error is raised when id is not an integer"""
        tenant_id = 1
        property_id = 123
        request = {
            'id': 'not_an_int'
        }

        with self.assertRaises(Error):
            UpdateTenantInformationRequest(tenant_id, property_id, request)

    def test_property_id_not_integer(self):
        """Test that Error is raised when property_id field is not an integer"""
        tenant_id = 1
        property_id = 123
        request = {
            'property_id': 'not_an_int'
        }

        with self.assertRaises(Error):
            UpdateTenantInformationRequest(tenant_id, property_id, request)

    def test_first_name_not_string(self):
        """Test that Error is raised when first_name is not a string"""
        tenant_id = 1
        property_id = 123
        request = {
            'first_name': 12345
        }

        with self.assertRaises(Error):
            UpdateTenantInformationRequest(tenant_id, property_id, request)

    def test_last_name_not_string(self):
        """Test that Error is raised when last_name is not a string"""
        tenant_id = 1
        property_id = 123
        request = {
            'last_name': 12345
        }

        with self.assertRaises(Error):
            UpdateTenantInformationRequest(tenant_id, property_id, request)

    def test_contract_start_date_not_string(self):
        """Test that Error is raised when contract_start_date is not a string"""
        tenant_id = 1
        property_id = 123
        request = {
            'contract_start_date': 12345
        }

        with self.assertRaises(Error):
            UpdateTenantInformationRequest(tenant_id, property_id, request)

    def test_contract_end_date_not_string(self):
        """Test that Error is raised when contract_end_date is not a string"""
        tenant_id = 1
        property_id = 123
        request = {
            'contract_end_date': 12345
        }

        with self.assertRaises(Error):
            UpdateTenantInformationRequest(tenant_id, property_id, request)

    def test_contract_status_not_string(self):
        """Test that Error is raised when contract_status is not a string"""
        tenant_id = 1
        property_id = 123
        request = {
            'contract_status': 12345
        }

        with self.assertRaises(Error):
            UpdateTenantInformationRequest(tenant_id, property_id, request)

    def test_recommended_replacement_date_not_string(self):
        """Test that Error is raised when recommended_replacement_date is not a string"""
        tenant_id = 1
        property_id = 123
        request = {
            'recommended_replacement_date': 12345
        }

        with self.assertRaises(Error):
            UpdateTenantInformationRequest(tenant_id, property_id, request)

    def test_monthly_rent_not_float(self):
        """Test that Error is raised when monthly_rent is not a float"""
        tenant_id = 1
        property_id = 123
        request = {
            'monthly_rent': 'not_a_float'
        }

        with self.assertRaises(Error):
            UpdateTenantInformationRequest(tenant_id, property_id, request)

    def test_phone_number_not_string(self):
        """Test that Error is raised when phone_number is not a string"""
        tenant_id = 1
        property_id = 123
        request = {
            'phone_number': 12345
        }

        with self.assertRaises(Error):
            UpdateTenantInformationRequest(tenant_id, property_id, request)


if __name__ == '__main__':
    unittest.main()
