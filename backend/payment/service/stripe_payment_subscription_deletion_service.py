import stripe
import logging
from common.logging.error.error import Error
from common.logging.error.error_messages import DELETION_ISSUE
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD


class StripePaymentSubscriptionDeletionService:
    def __init__(self, base_url, secret_key):
        self.base_url = base_url
        self.secret_key = secret_key

    def delete_subscription_for_customer(self, stripe_customer_id):
        """
        Deletes a customer's subscription from the table
        :param stripe_customer_id: The customerId on Stripe's end
        :return: python int
        """
        logging.info(START_OF_METHOD)
        subscription_id = self.retrieve_subscription_id_for_customer(
            stripe_customer_id=stripe_customer_id)
        deletion_status = self.invoke_stripe_deletion_endpoint(
            subscription_id=subscription_id)
        logging.info(END_OF_METHOD)
        return deletion_status

    @staticmethod
    def retrieve_subscription_id_for_customer(stripe_customer_id):
        """
        Fetches the subscriptionId for a customer on the backend
        :param stripe_customer_id: The customerId on Stripe's end
        :return: python str
        """
        logging.info(START_OF_METHOD)
        try:
            subscription = stripe.Subscription.list(customer=stripe_customer_id)
            subscription_id = subscription.data[0].id
            logging.info(END_OF_METHOD)
            return subscription_id
        except Exception as e:
            logging.error('There was an issue retrieving the subscriptionId for the customer',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(DELETION_ISSUE)

    @staticmethod
    def invoke_stripe_deletion_endpoint(subscription_id):
        """
        Calls the Stripe backend to halt the customer's subscription status
        :param subscription_id: The internal id of a customer subscription
        :return: python int
        """
        logging.info(START_OF_METHOD)
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            if subscription.cancel_at_period_end:
                return 200
            else:
                raise Exception
        except Exception as e:
            logging.error('There was an issue calling the Stripe endpoint',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(DELETION_ISSUE)
