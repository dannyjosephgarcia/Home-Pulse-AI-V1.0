import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD
from common.logging.error.error_messages import INVALID_REQUEST


class CustomerAuthenticationRequest:
    def __init__(self, request):
        self._validate_customer_login_request(request)
        self.email = request['email']
        self.password = request['password']

    @staticmethod
    def _validate_customer_login_request(request):
        logging.info(START_OF_METHOD)
        if 'email' not in request:
            logging.error('The email field is a required field')
            raise Error(INVALID_REQUEST)
        if 'password' not in request:
            logging.error('The password field is a required field')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['email'], str):
            logging.error('The email field must be a string')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['password'], str):
            logging.error('The password field must be a password')
            raise Error(INVALID_REQUEST)
