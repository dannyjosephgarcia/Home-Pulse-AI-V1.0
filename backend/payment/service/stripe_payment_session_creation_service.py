import logging
import stripe
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR


class StripePaymentSessionCreationService:
    def __init__(self, secret_key, success_url, cancel_url, price, mode, payment_type):
        self.secret_key = secret_key
        self.success_url = success_url
        self.cancel_url = cancel_url
        self.price = price
        self.mode = mode
        self.payment_type = payment_type

    def create_checkout_session_for_customer(self, user_id):
        """
        Generates a payment URL for stripe
        :param user_id: The internal identifier for our user
        :return: python dict, the response for the route
        """
        logging.info(START_OF_METHOD)
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=[self.payment_type],
                mode=self.mode,
                line_items=[{
                    "price": self.price,
                    "quantity": 1,
                }],
                success_url=self.success_url,
                cancel_url=self.cancel_url,
                metadata={"userId": user_id}
            )
            response = {"url": session.url}
            logging.info(END_OF_METHOD)
            return response
        except Exception as e:
            logging.error('There was an error generating the checkout link',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)
