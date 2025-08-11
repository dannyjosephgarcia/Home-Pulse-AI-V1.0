import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_REQUEST


class CustomerPostLoginRequest:
    def __init__(self, request):
        self._valid_post_login_request(request)
        self.session_id = request['sessionId']

    @staticmethod
    def _valid_post_login_request(request):
        """
        Validates the request to /v1/customer/post-login
        :param request: The request to the route
        """
        logging.info(START_OF_METHOD)
        if 'sessionId' not in request:
            logging.error('The sessionId field is a required field')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['sessionId'], str):
            logging.info('The sessionId field must be a string')
            raise Error(INVALID_REQUEST)
        logging.info(END_OF_METHOD)
