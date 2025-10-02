import unittest
from copy import deepcopy
from common.logging.error.error import Error
from backend.db.model.customer_authentication_request import CustomerAuthenticationRequest
EMAIL = 'dg88@gmail.com'
PASSWORD = "HelloWorld123"
HAPPY_CUSTOMER_AUTHENTICATION_REQUEST = {
    'email': EMAIL,
    'password': PASSWORD
}


class TestCustomerAuthenticationRequest(unittest.TestCase):
    def test_customer_authentication_request_missing_email(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_AUTHENTICATION_REQUEST)
            del local_request['email']
            CustomerAuthenticationRequest(local_request)

    def test_customer_authentication_request_missing_password(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_AUTHENTICATION_REQUEST)
            del local_request['password']
            CustomerAuthenticationRequest(local_request)

    def test_customer_authentication_request_wrong_email_type(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_AUTHENTICATION_REQUEST)
            local_request['email'] = 123
            CustomerAuthenticationRequest(local_request)

    def test_customer_authentication_request_wrong_password_type(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_AUTHENTICATION_REQUEST)
            local_request['password'] = 123
            CustomerAuthenticationRequest(local_request)

    def test_customer_authentication_request_happy(self):
        request = CustomerAuthenticationRequest(HAPPY_CUSTOMER_AUTHENTICATION_REQUEST)
        self.assertEqual(EMAIL, request.email)
        self.assertEqual(PASSWORD, request.password)


if __name__ == "__main__":
    unittest.main()
