import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_REQUEST


class UpdateCustomerPaymentStatusRequest:
    def __init__(self, request):
        self._validate_update_payment_status_request(request)
        self.session_id = request['sessionId']

    @staticmethod
    def _validate_update_payment_status_request(request):
        """
        Validates the request to the /v1/payment/update-payment-status route
        :param request: python dict
        """
        logging.info(START_OF_METHOD)
        if 'sessionId' not in request:
            logging.error('The sessionId field is a required field')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['sessionId'], str):
            logging.error('The sessionId field must be a string')
            raise Error(INVALID_REQUEST)
