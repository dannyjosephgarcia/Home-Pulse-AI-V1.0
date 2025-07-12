import logging
import re
from common.logging.error.error_messages import INVALID_REQUEST
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error


class CustomerCreationRequest:
    def __init__(self, request):
        self._validate_customer_creation_request(request)
        self.email = request['email']
        self.password = request['password']

    @classmethod
    def _validate_customer_creation_request(cls, request):
        """
        Validates the request to insert a customer into the database to begin using the product
        :param request: The request to the route
        """
        logging.info(START_OF_METHOD)
        if 'email' not in request:
            logging.error('The email field is a required field')
            raise Error(INVALID_REQUEST)
        if 'password' not in request:
            logging.error('The password field is a required field')
            raise Error(INVALID_REQUEST)
        cls._validate_customer_email(request['email'])
        cls._validate_customer_password(request['password'])
        logging.info(END_OF_METHOD)

    @staticmethod
    def _validate_customer_email(email):
        """
        Validates that the email entered is correct
        :param email: The email the user is attempting to register with
        """
        if not isinstance(email, str):
            logging.error('The email entered is not a valid string')
            raise Error(INVALID_REQUEST)
        if '@' not in email:
            logging.error('The email provided is missing a valid domain')
            raise Error(INVALID_REQUEST)

    @staticmethod
    def _validate_customer_password(password):
        """
        Validates that the password entered meets minimum requirements
        :param password: The password provided by the user
        :return:
        """
        if not isinstance(password, str):
            logging.error('The password provided is not a valid string')
            raise Error(INVALID_REQUEST)
        if len(password) < 8:
            logging.error('The password provided must contain at least 8 characters')
            raise Error(INVALID_REQUEST)
        has_uppercase = re.search(r"[A-Z]", password)
        has_number = re.search(r"\d", password)
        if not has_uppercase:
            logging.error('The password provided must contain at least 1 uppercase character')
            raise Error(INVALID_REQUEST)
        if not has_number:
            logging.error('The password provided must contain at least 1 digit')
            raise Error(INVALID_REQUEST)