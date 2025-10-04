import unittest
from backend.db.model.customer_creation_request import CustomerCreationRequest
from common.logging.error.error import Error


class TestCustomerCreationRequest(unittest.TestCase):

    def test_valid_request_without_token(self):
        """Test creating a valid CustomerCreationRequest without token"""
        request = {
            'email': 'test@example.com',
            'password': 'SecurePass1'
        }

        obj = CustomerCreationRequest(request)

        self.assertEqual(obj.email, 'test@example.com')
        self.assertEqual(obj.password, 'SecurePass1')
        self.assertIsNone(obj.token)

    def test_valid_request_with_token(self):
        """Test creating a valid CustomerCreationRequest with token"""
        request = {
            'email': 'test@example.com',
            'password': 'SecurePass1',
            'token': '550e8400-e29b-41d4-a716-446655440000'
        }

        obj = CustomerCreationRequest(request)

        self.assertEqual(obj.email, 'test@example.com')
        self.assertEqual(obj.password, 'SecurePass1')
        self.assertEqual(obj.token, '550e8400-e29b-41d4-a716-446655440000')

    def test_missing_email_field(self):
        """Test that Error is raised when email field is missing"""
        request = {
            'password': 'SecurePass1'
        }

        with self.assertRaises(Error):
            CustomerCreationRequest(request)

    def test_missing_password_field(self):
        """Test that Error is raised when password field is missing"""
        request = {
            'email': 'test@example.com'
        }

        with self.assertRaises(Error):
            CustomerCreationRequest(request)

    def test_email_not_string(self):
        """Test that Error is raised when email is not a string"""
        request = {
            'email': 12345,
            'password': 'SecurePass1'
        }

        with self.assertRaises(Error):
            CustomerCreationRequest(request)

    def test_email_without_at_symbol(self):
        """Test that Error is raised when email is missing @ symbol"""
        request = {
            'email': 'testexample.com',
            'password': 'SecurePass1'
        }

        with self.assertRaises(Error):
            CustomerCreationRequest(request)

    def test_password_not_string(self):
        """Test that Error is raised when password is not a string"""
        request = {
            'email': 'test@example.com',
            'password': 12345
        }

        with self.assertRaises(Error):
            CustomerCreationRequest(request)

    def test_password_too_short(self):
        """Test that Error is raised when password is less than 8 characters"""
        request = {
            'email': 'test@example.com',
            'password': 'Short1'
        }

        with self.assertRaises(Error):
            CustomerCreationRequest(request)

    def test_password_without_uppercase(self):
        """Test that Error is raised when password has no uppercase character"""
        request = {
            'email': 'test@example.com',
            'password': 'securepass1'
        }

        with self.assertRaises(Error):
            CustomerCreationRequest(request)

    def test_password_without_number(self):
        """Test that Error is raised when password has no digit"""
        request = {
            'email': 'test@example.com',
            'password': 'SecurePass'
        }

        with self.assertRaises(Error):
            CustomerCreationRequest(request)

    def test_invalid_token_format(self):
        """Test that Error is raised when token is not a valid UUID"""
        request = {
            'email': 'test@example.com',
            'password': 'SecurePass1',
            'token': 'not-a-valid-uuid'
        }

        with self.assertRaises(Error):
            CustomerCreationRequest(request)

    def test_valid_password_edge_case(self):
        """Test valid password with exactly 8 characters"""
        request = {
            'email': 'test@example.com',
            'password': 'Secure12'
        }

        obj = CustomerCreationRequest(request)
        self.assertEqual(obj.password, 'Secure12')


if __name__ == '__main__':
    unittest.main()
