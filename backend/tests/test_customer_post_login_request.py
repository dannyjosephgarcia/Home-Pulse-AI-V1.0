import unittest
from common.logging.error.error import Error
from copy import deepcopy
from backend.db.model.customer_post_login_request import CustomerPostLoginRequest
SESSION_ID = "xfypog123456"
HAPPY_POST_LOGIN_REQUEST = {
    'sessionId': SESSION_ID
}


class TestCustomerPostLoginRequest(unittest.TestCase):
    def test_customer_post_login_request_missing_session_id(self):
        with self.assertRaises(Error):
            CustomerPostLoginRequest({})

    def test_customer_post_login_request_wrong_session_id_type(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_POST_LOGIN_REQUEST)
            local_request['sessionId'] = 123
            CustomerPostLoginRequest(local_request)

    def test_customer_post_login_request_happy(self):
        request = CustomerPostLoginRequest(HAPPY_POST_LOGIN_REQUEST)
        self.assertEqual(SESSION_ID, request.session_id)


if __name__ == "__main__":
    unittest.main()
