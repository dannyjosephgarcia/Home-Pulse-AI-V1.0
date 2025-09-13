import unittest
from backend.app.container import Container
from unittest.mock import patch


class TestCustomerCreationInsertionService(unittest.TestCase):
    def setUpClass(self):
        self.container = Container()
        self.service = self.container.customer_creation_insertion_service()

    def test_customer_creation_insertion_service_format_customer_creation_insertion_response(self):
        pass

