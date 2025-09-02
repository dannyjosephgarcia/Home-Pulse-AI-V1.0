import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR, DELETION_ISSUE
from backend.db.model.query.sql_statements import SELECT_STRIPE_CUSTOMER_ID, UPDATE_SUBSCRIPTION_STATUS_FOR_DELETION


class CustomerSubscriptionDeletionService:
    def __init__(self, hp_ai_db_connection_pool, stripe_payment_subscription_deletion_service):
        self.pool = hp_ai_db_connection_pool.pool
        self.stripe_deletion_service = stripe_payment_subscription_deletion_service

    def delete_customer_subscription_from_system(self, user_id):
        """

        :param user_id:
        :return:
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        stripe_customer_id = self.fetch_stripe_customer_id_for_deletion(
            cnx=cnx,
            user_id=user_id)
        deletion_status = self.stripe_deletion_service.delete_subscription_for_customer(
            stripe_customer_id=stripe_customer_id)
        put_record_status = self.update_subscription_status_for_customer(
            cnx=cnx,
            user_id=user_id)
        response = {'deletionStatus': deletion_status,
                    'putRecordStatus': put_record_status}
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def update_subscription_status_for_customer(cnx, user_id):
        """
        Updates the customer's status in our system
        :param cnx: The MySQLConnectionPool
        :param user_id: The internal id of a customer in our system
        :return:
        """
        logging.info(START_OF_METHOD)
        put_record_status = 200
        try:
            cursor = cnx.cursor()
            cursor.execute(UPDATE_SUBSCRIPTION_STATUS_FOR_DELETION, [user_id])
            cnx.commit()
            cursor.close()
            logging.info(END_OF_METHOD)
            return put_record_status
        except Exception as e:
            logging.error('There was an issue updating the customer subscription in our table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            return 500

    @staticmethod
    def fetch_stripe_customer_id_for_deletion(cnx, user_id):
        """
        Fetches the Stripe customerId to retrieve the subscriptionId
        :param cnx: The MySQLConnectionPool
        :param user_id: The UUID of a user in our system
        :return:
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_STRIPE_CUSTOMER_ID, [user_id])
            table = cursor.fetchall()
            stripe_customer_id = table[0][0]
            logging.info(END_OF_METHOD)
            return stripe_customer_id
        except Exception as e:
            logging.error('There was an issue retrieving the stripe customer id',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(DELETION_ISSUE)

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)