import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import UPDATE_FIRST_AND_LAST_OF_CUSTOMER, SELECT_CUSTOMER_FIRST_AND_LAST


class CustomerProfileUpdateService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def update_user_first_and_last_name(self, user_id, first_name, last_name):
        """
        Updates the user's first and last name in the database
        :param user_id: The internal id of a user
        :param first_name: The first name of the customer
        :param last_name: The last name of the customer
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        put_record_status = self.execute_update_statement_for_profile_names(
            cnx=cnx,
            user_id=user_id,
            first_name=first_name,
            last_name=last_name)
        response = self.fetch_updated_profile_for_response(
            cnx=cnx,
            user_id=user_id,
            put_record_status=put_record_status)
        cnx.close()
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def execute_update_statement_for_profile_names(cnx, user_id, first_name, last_name):
        """
        :param cnx: The MySQLConnectionPool object
        :param user_id: The internal identifier of a customer in our system
        :param first_name: The first name of a customer
        :param last_name: The last name of a customer
        :return: python int
        """
        logging.info(START_OF_METHOD)
        put_record_status = 200
        try:
            cursor = cnx.cursor()
            cursor.execute(UPDATE_FIRST_AND_LAST_OF_CUSTOMER, [first_name, last_name, user_id])
            cnx.commit()
            cursor.close()
            logging.info(END_OF_METHOD)
            return put_record_status
        except Exception as e:
            logging.error('An issue occurred updating the first and last name of a customer in our system',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def fetch_updated_profile_for_response(cnx, user_id, put_record_status):
        """
        Fetches the user to format the response
        :param cnx: The MySQLConnectionPool object
        :param user_id: The internal id of a customer in our system
        :param put_record_status: The status of updating a customer in our system
        :return:
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_CUSTOMER_FIRST_AND_LAST, [user_id])
            result = cursor.fetchall()
            response = {
                'firstName': result[0][0],
                'lastName': result[0][1],
                'userId': user_id,
                'putRecordStatus': put_record_status
            }
            logging.info(END_OF_METHOD)
            return response
        except Exception as e:
            logging.error('Could not fetch the profile update response',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)



    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)
