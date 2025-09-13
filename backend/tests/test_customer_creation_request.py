import unittest
from common.logging.error.error import Error
from copy import deepcopy
from backend.db.model.customer_creation_request import CustomerCreationRequest
EMAIL = "dg98@gmail.com"
PASSWORD = "HelloWorld123"
TOKEN = "265b1f5b-e82d-46a6-a4cb-55d652b125ed"
HAPPY_CUSTOMER_CREATION_REQUEST = {
    'email': EMAIL,
    'password': PASSWORD,
    'token': TOKEN
}


class TestCustomerCreationRequest(unittest.TestCase):
    def test_customer_creation_request_missing_email(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_CREATION_REQUEST)
            del local_request['email']
            CustomerCreationRequest(local_request)

    def test_customer_creation_request_missing_password(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_CREATION_REQUEST)
            del local_request['password']
            CustomerCreationRequest(local_request)

    def test_customer_creation_request_invalid_customer_email_type(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_CREATION_REQUEST)
            local_request['email'] = 123
            CustomerCreationRequest(local_request)

    def test_customer_creation_request_invalid_customer_email_string(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_CREATION_REQUEST)
            local_request['email'] = 'Hello'
            CustomerCreationRequest(local_request)

    def test_customer_creation_request_invalid_token(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_CREATION_REQUEST)
            local_request['token'] = '123'
            CustomerCreationRequest(local_request)

    def test_customer_creation_request_invalid_password_type(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_CREATION_REQUEST)
            local_request['password'] = 123
            CustomerCreationRequest(local_request)

    def test_customer_creation_request_invalid_password_short(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_CREATION_REQUEST)
            local_request['password'] = 'Hello'
            CustomerCreationRequest(local_request)

    def test_customer_creation_request_invalid_password_no_upper(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_CREATION_REQUEST)
            local_request['password'] = 'helloworld123'
            CustomerCreationRequest(local_request)

    def test_customer_creation_request_invalid_password_no_numbers(self):
        with self.assertRaises(Error):
            local_request = deepcopy(HAPPY_CUSTOMER_CREATION_REQUEST)
            local_request['password'] = 'helloooworldd'
            CustomerCreationRequest(local_request)

    def test_customer_creation_request_happy(self):
        request = CustomerCreationRequest(HAPPY_CUSTOMER_CREATION_REQUEST)
        self.assertEqual(EMAIL, request.email)
        self.assertEqual(PASSWORD, request.password)
        self.assertEqual(TOKEN, request.token)


if __name__ == "__main__":
    unittest.main()
