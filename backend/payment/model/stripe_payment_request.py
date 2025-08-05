import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_REQUEST


class StripePaymentRequest:
    def __init__(self, request):
        self._validate_stripe_payment_request(request)
        self.user_id = request['userId']
        self.price = request['price']
        self.mode = request['mode']
        self.payment_type = request['paymentType']

    @staticmethod
    def _validate_stripe_payment_request(request):
        """
        Validates the request to the stripe payment session creation route
        :param request: The request body
        """
        logging.info(START_OF_METHOD)
        if 'userId' not in request:
            logging.error('The userId field is a required field')
            raise Error(INVALID_REQUEST)
        if 'price' not in request:
            logging.error('The price field is a required field')
            raise Error(INVALID_REQUEST)
        if 'mode' not in request:
            logging.error('The mode field is a required field')
            raise Error(INVALID_REQUEST)
        if 'paymentType' not in request:
            logging.error('The paymentType is a required field')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['userId'], str):
            logging.error('The userId field needs to be a string')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['price'], str):
            logging.error('The price field needs to be a string')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['mode'], str):
            logging.error('The mode field needs to be a string')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['paymentType'], str):
            logging.error('The paymentType field needs to be a string')
            raise Error(INVALID_REQUEST)
        logging.info(END_OF_METHOD)
