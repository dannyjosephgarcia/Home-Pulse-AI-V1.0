import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR, INVALID_CUSTOMER
from backend.db.model.query.sql_statements import SELECT_SUBSCRIPTION_INFORMATION


class CustomerSubscriptionRetrievalService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def fetch_subscription_information_for_customer(self, user_id):
        """
        Fetches the subscription information for a customer
        :param user_id: The internal id of a customer in our system
        :return: python dict, the response for the route
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        table = self.execute_retrieve_statement_for_subscription(
            cnx=cnx,
            user_id=user_id)
        response = self.format_subscription_table_response(
            table=table)
        cnx.close()
        logging.info(END_OF_METHOD)
        return response


    @staticmethod
    def execute_retrieve_statement_for_subscription(cnx, user_id):
        """
        Performs the query against the subscriptions table
        :param cnx:
        :param user_id:
        :return:
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_SUBSCRIPTION_INFORMATION, [user_id])
            table = cursor.fetchall()
            if not table:
                logging.error('No subscription information available for this customer')
                raise Error(INVALID_CUSTOMER)
            logging.info(END_OF_METHOD)
            return table
        except Exception as e:
            logging.error('There was an issue querying the subscription table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def format_subscription_table_response(table):
        """
        Formats the response from the subscriptions table
        :param table: The object returned from the query
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        response = {
            'status': table[0][0],
            'subscription_id': table[0][1],
            'subscription_end': table[0][2]
        }
        return response

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)