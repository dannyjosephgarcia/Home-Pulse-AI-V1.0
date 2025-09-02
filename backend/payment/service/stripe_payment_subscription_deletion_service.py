import stripe
import logging
import requests
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR, DELETION_ISSUE


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

    def retrieve_subscription_id_for_customer(self, stripe_customer_id):
        """
        Fetches the subscriptionId for a customer on the backend
        :param stripe_customer_id: The customerId on Stripe's end
        :return: python str
        """
        logging.info(START_OF_METHOD)
        try:
            response = requests.get(self.base_url + f'/v1/customers/{stripe_customer_id}',
                                    auth=self.secret_key)
            response.raise_for_status()
            response_json = response.json()
            subscription_id = response_json['subscriptions']['data'][0]['id']
            logging.info(END_OF_METHOD)
            return subscription_id
        except Exception as e:
            logging.error('There was an issue retrieving the subscriptionId for the customer',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(DELETION_ISSUE)

    def invoke_stripe_deletion_endpoint(self, subscription_id):
        """
        Calls the Stripe backend to halt the customer's subscription status
        :param subscription_id: The internal id of a customer subscription
        :return: python int
        """
        logging.info(START_OF_METHOD)
        try:
            payload = {'cancel_at_period_end': 'true'}
            response = requests.post(self.base_url + f'/v1/subscriptions/{subscription_id}',
                                     data=payload,
                                     auth=self.secret_key)
            response.raise_for_status()
            return 200
        except Exception as e:
            logging.error('There was an issue calling the Stripe endpoint',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(DELETION_ISSUE)