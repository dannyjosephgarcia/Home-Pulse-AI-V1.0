import unittest
from backend.db.model.customer_authentication_request import CustomerAuthenticationRequest
from common.logging.error.error import Error


class TestCustomerAuthenticationRequest(unittest.TestCase):

    def test_valid_request(self):
        """Test creating a valid CustomerAuthenticationRequest"""
        request = {
            'email': 'test@example.com',
            'password': 'SecurePass123'
        }

        obj = CustomerAuthenticationRequest(request)

        self.assertEqual(obj.email, 'test@example.com')
        self.assertEqual(obj.password, 'SecurePass123')

    def test_missing_email_field(self):
        """Test that Error is raised when email field is missing"""
        request = {
            'password': 'SecurePass123'
        }

        with self.assertRaises(Error):
            CustomerAuthenticationRequest(request)

    def test_missing_password_field(self):
        """Test that Error is raised when password field is missing"""
        request = {
            'email': 'test@example.com'
        }

        with self.assertRaises(Error):
            CustomerAuthenticationRequest(request)

    def test_email_not_string(self):
        """Test that Error is raised when email is not a string"""
        request = {
            'email': 12345,
            'password': 'SecurePass123'
        }

        with self.assertRaises(Error):
            CustomerAuthenticationRequest(request)

    def test_password_not_string(self):
        """Test that Error is raised when password is not a string"""
        request = {
            'email': 'test@example.com',
            'password': 12345
        }

        with self.assertRaises(Error):
            CustomerAuthenticationRequest(request)

    def test_empty_email_string(self):
        """Test that empty email string is accepted (validation not enforced for empty)"""
        request = {
            'email': '',
            'password': 'SecurePass123'
        }

        obj = CustomerAuthenticationRequest(request)
        self.assertEqual(obj.email, '')

    def test_empty_password_string(self):
        """Test that empty password string is accepted (validation not enforced for empty)"""
        request = {
            'email': 'test@example.com',
            'password': ''
        }

        obj = CustomerAuthenticationRequest(request)
        self.assertEqual(obj.password, '')


if __name__ == '__main__':
    unittest.main()
