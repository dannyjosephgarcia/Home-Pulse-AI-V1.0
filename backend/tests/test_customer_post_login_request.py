import unittest
from backend.db.model.customer_post_login_request import CustomerPostLoginRequest
from common.logging.error.error import Error


class TestCustomerPostLoginRequest(unittest.TestCase):

    def test_valid_request(self):
        """Test creating a valid CustomerPostLoginRequest"""
        request = {
            'sessionId': 'session_abc123xyz'
        }

        obj = CustomerPostLoginRequest(request)

        self.assertEqual(obj.session_id, 'session_abc123xyz')

    def test_missing_session_id_field(self):
        """Test that Error is raised when sessionId field is missing"""
        request = {}

        with self.assertRaises(Error):
            CustomerPostLoginRequest(request)

    def test_session_id_not_string(self):
        """Test that Error is raised when sessionId is not a string"""
        request = {
            'sessionId': 12345
        }

        with self.assertRaises(Error):
            CustomerPostLoginRequest(request)

    def test_empty_session_id_string(self):
        """Test that empty sessionId string is accepted"""
        request = {
            'sessionId': ''
        }

        obj = CustomerPostLoginRequest(request)
        self.assertEqual(obj.session_id, '')

    def test_session_id_with_special_characters(self):
        """Test that sessionId with special characters is accepted"""
        request = {
            'sessionId': 'session-123_abc!@#'
        }

        obj = CustomerPostLoginRequest(request)
        self.assertEqual(obj.session_id, 'session-123_abc!@#')


if __name__ == '__main__':
    unittest.main()
