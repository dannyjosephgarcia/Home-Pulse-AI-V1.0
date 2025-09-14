import unittest
from backend.app.container import Container
from unittest.mock import patch
from backend.db.model.customer_creation_request import CustomerCreationRequest
from copy import deepcopy
from common.logging.error.error import Error

EMAIL = 'dg98@gmail.com'
PASSWORD = 'HelloWorld123'
TOKEN = 'b7968f6c-2ec4-4372-8b83-83efb92b8d76'
HAPPY_CUSTOMER_CREATION_INSERTION_REQUEST = {
    'email': EMAIL,
    'password': PASSWORD,
    'token': TOKEN
}


class TestCustomerCreationInsertionService(unittest.TestCase):
    def setUp(self):
        self.container = Container()
        self.service = self.container.customer_creation_insertion_service()

    def test_customer_creation_insertion_service_perform_password_hash(self):
        hashed_password = self.service.perform_password_hash(PASSWORD)
        self.assertIsInstance(hashed_password, str)

    def test_customer_creation_insertion_service_format_customer_creation_insertion_response(self):
        pass

    def test_customer_creation_insertion_service_validate_company_id_valid_company(self):
        cnx = self.service.obtain_connection()
        self.service._validate_company_id(cnx, 1)
        cnx.close()

    def test_customer_creation_insertion_service_validate_company_id_invalid_company_id(self):
        with self.assertRaises(Error):
            cnx = self.service.obtain_connection()
            self.service._validate_company_id(cnx, 456)

    def tearDown(self):
        cnx = self.service.obtain_connection()
        cursor = cnx.cursor()
        cursor.execute("""DELETE FROM home_pulse_ai.users WHERE email=%s;""", [EMAIL])
        cnx.commit()
        cursor.close()
        cnx.close()
