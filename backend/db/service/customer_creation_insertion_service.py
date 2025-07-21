import logging
from flask_bcrypt import Bcrypt
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from backend.db.model.query.sql_statements import INSERT_CUSTOMER_INTO_USER_TABLE, SELECT_CUSTOMER_FROM_USER_TABLE

bcrypt = Bcrypt()


class CustomerCreationInsertionService:
    def __init__(self, hp_ai_db_connection_pool):
        self.hp_ai_db_connection_pool = hp_ai_db_connection_pool.pool

    def insert_new_customer_into_user_table(self, customer_creation_request):
        """
        Inserts a customer into the user table to grant access to the product
        :param customer_creation_request: The CustomerCreationRequest model object
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        hashed_password = self.perform_password_hash(
            password=customer_creation_request.password)
        insert_record_status = self.execute_insertion_statement_for_user_table(
            email=customer_creation_request.email,
            hashed_password=hashed_password)
        insert_record_response = self.fetch_user_for_insertion_response(
            email=customer_creation_request.email)
        response = self.format_customer_creation_insertion_response(
            insert_record_status=insert_record_status,
            insert_record_response=insert_record_response)
        logging.info(END_OF_METHOD,
                     extra={'information': {'insertRecordStatus': insert_record_status}})
        return response

    def execute_insertion_statement_for_user_table(self, email, hashed_password):
        """
        Inserts all relevant customer information into the user table
        :param email: The email of the customer
        :param hashed_password: The password hash of the customer
        :return: python int, the status of the insert
        """
        logging.info(START_OF_METHOD)
        insert_record_status = 200
        try:
            cnx = self.hp_ai_db_connection_pool.get_connection()
            cursor = cnx.cursor()
            cursor.execute(INSERT_CUSTOMER_INTO_USER_TABLE, [email, hashed_password, 'abc123', 0])
            cnx.commit()
            cursor.close()
            cnx.close()
        except Exception as e:
            logging.error('An error occurred inserting a customer into the user table',
                          extra={'information': {'error': str(e)}},
                          exc_info=True)
            insert_record_status = 500
        logging.info(END_OF_METHOD)
        return insert_record_status

    def fetch_user_for_insertion_response(self, email):
        """
        Fetches the user just inserted into the table for the response to the insertion route
        :param email: The email of the customer inserted
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        try:
            cnx = self.hp_ai_db_connection_pool.get_connection()
            cursor = cnx.cursor()
            cursor.execute(SELECT_CUSTOMER_FROM_USER_TABLE, [email])
            table = cursor.fetchall()
            response = {
                'id': table[0][0],
                'username': table[0][1],
                'password': table[0][2],
                'stripeCustomerId': table[0][3],
                'isPaid': table[0][4],
                'createdAt': table[0][5]
            }
            cursor.close()
            cnx.close()
            logging.info(END_OF_METHOD)
            return response
        except Exception as e:
            logging.error('There was an issue retrieving the customer from the table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            return {}

    @staticmethod
    def perform_password_hash(password):
        """
        Hashes the password provided by the customer
        :param password: The password to hash
        :return: python str, a hashed version of the password
        """
        logging.info(START_OF_METHOD)
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        logging.info(END_OF_METHOD)
        return hashed_password

    @staticmethod
    def format_customer_creation_insertion_response(insert_record_status, insert_record_response):
        """
        Formats the response for the customer creation route
        :param insert_record_status: python int, the status of insertion
        :param insert_record_response: python dict, the response from the user table
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        response = {
            'insertRecordStatus': insert_record_status,
            'insertRecordResponse': insert_record_response
        }
        logging.info(END_OF_METHOD)
        return response