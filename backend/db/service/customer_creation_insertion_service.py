import logging
from flask_bcrypt import Bcrypt
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from backend.db.model.query.sql_statements import INSERT_CUSTOMER_INTO_USER_TABLE, SELECT_CUSTOMER_FROM_USER_TABLE
from backend.payment.model.stripe_payment_request import StripePaymentRequest

bcrypt = Bcrypt()


class CustomerCreationInsertionService:
    def __init__(self, hp_ai_db_connection_pool, stripe_payment_session_creation_service):
        self.hp_ai_db_connection_pool = hp_ai_db_connection_pool.pool
        self.stripe_payment_session_creation_service = stripe_payment_session_creation_service

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
        table_response = self.fetch_user_for_table_response(
            email=customer_creation_request.email)
        stripe_checkout_session_response = self.format_stripe_checkout_session_request(
            table_response=table_response)
        response = self.format_customer_creation_insertion_response(
            table_response=table_response,
            stripe_checkout_session_response=stripe_checkout_session_response)
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

    def fetch_user_for_table_response(self, email):
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
                'email': table[0][1],
                'password': table[0][2],
                'stripeCustomerId': table[0][3],
                'isPaid': table[0][4],
                'createdAt': table[0][5],
                'firstName': table[0][6],
                'lastName': table[0][7]
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

    def format_stripe_checkout_session_request(self, table_response):
        """
        Creates an instance of the StripePaymentRequest object
        :param table_response: The response from the table after insertion
        :return: StripePaymentRequest
        """
        logging.info(START_OF_METHOD)
        user_id = table_response['id']
        stripe_checkout_session_response = (
            self.stripe_payment_session_creation_service.create_checkout_session_for_customer(
                user_id=user_id))
        logging.info(END_OF_METHOD)
        return stripe_checkout_session_response

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
    def format_customer_creation_insertion_response(table_response, stripe_checkout_session_response):
        """
        Formats the response for the customer creation route
        :param stripe_checkout_session_response: The response containing the URL for stripe customers
        :param table_response: Contains information retrieved from the db
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        response = {
            'userId': table_response['id'],
            'insertRecordResponse': table_response,
            'customerCheckoutSession': stripe_checkout_session_response['url']
        }
        logging.info(END_OF_METHOD)
        return response
