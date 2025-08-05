import logging
import stripe
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR


class StripePaymentSessionCreationService:
    def __init__(self, secret_key, success_url, cancel_url):
        self.secret_key = secret_key
        self.success_url = success_url
        self.cancel_url = cancel_url

    def create_checkout_session_for_customer(self, stripe_payment_request):
        """
        Generates a payment URL for stripe
        :param stripe_payment_request: The StripePaymentRequest model object.
        :return: python dict, the response for the route
        """
        logging.info(START_OF_METHOD)
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=[stripe_payment_request.payment_type],
                mode=stripe_payment_request.mode,
                line_items=[{
                    "price": stripe_payment_request.price,  # your actual Stripe Price ID
                    "quantity": 1,
                }],
                success_url=self.success_url,
                cancel_url=self.cancel_url
            )
            response = {"url": session.url}
            logging.info(END_OF_METHOD)
            return response
        except Exception as e:
            logging.error('There was an error generating the checkout link',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            return Error(INTERNAL_SERVICE_ERROR)
