import time
import logging
from zoneinfo import ZoneInfo
from datetime import datetime
from flask_bcrypt import Bcrypt
from common.logging.error.error import Error
from dateutil.relativedelta import relativedelta
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR, INVALID_INVITATION
from backend.db.model.query.sql_statements import (INSERT_SUBSCRIPTION_INFORMATION,
                                                   UPDATE_INVITATION_INFORMATION,
                                                   SELECT_COMPANY_STATUS,
                                                   INSERT_CUSTOMER_INTO_USER_TABLE,
                                                   SELECT_CUSTOMER_FROM_USER_TABLE,
                                                   SELECT_INVITATION_INFORMATION)

bcrypt = Bcrypt()


class CustomerCreationInsertionService:
    def __init__(self, hp_ai_db_connection_pool, stripe_payment_session_creation_service):
        self.pool = hp_ai_db_connection_pool.pool
        self.stripe_payment_session_creation_service = stripe_payment_session_creation_service

    def insert_new_customer_into_user_table(self, customer_creation_request):
        """
        Inserts a customer into the user table to grant access to the product
        :param customer_creation_request: The CustomerCreationRequest model object
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        hashed_password = self.perform_password_hash(
            password=customer_creation_request.password)
        if customer_creation_request.token:
            invitation_information = self.fetch_invitation_information(
                cnx=cnx,
                email=customer_creation_request.email,
                token=customer_creation_request.token)
            company_id = invitation_information['company_id']
            insert_record_status = self.execute_insertion_statement_for_user_table(
                cnx=cnx,
                email=customer_creation_request.email,
                hashed_password=hashed_password,
                company_id=company_id)
            put_record_status = self.execute_update_statement_for_invitation_table(
                cnx=cnx,
                email=customer_creation_request.email)
            table_response = self.fetch_user_for_table_response(
                cnx=cnx,
                email=customer_creation_request.email)
            stripe_checkout_session_response = {'url': 'licensed_user'}
            insert_subscription_status = 201
        else:
            insert_record_status = self.execute_insertion_statement_for_user_table(
                cnx=cnx,
                email=customer_creation_request.email,
                hashed_password=hashed_password)
            table_response = self.fetch_user_for_table_response(
                cnx=cnx,
                email=customer_creation_request.email)
            insert_subscription_status = self.execute_insertion_statement_for_subscription_table(
                cnx=cnx,
                table_response=table_response)
            put_record_status = 201
            stripe_checkout_session_response = self.format_stripe_checkout_session_request(
                table_response=table_response)
        cnx.close()
        response = self.format_customer_creation_insertion_response(
            table_response=table_response,
            stripe_checkout_session_response=stripe_checkout_session_response)
        logging.info(END_OF_METHOD,
                     extra={'information': {'insertRecordStatus': insert_record_status,
                                            'putRecordStatus': put_record_status,
                                            'insertSubscriptionStatus': insert_subscription_status}})
        return response

    @classmethod
    def execute_insertion_statement_for_user_table(cls, cnx, email, hashed_password, company_id=None):
        """
        Inserts all relevant customer information into the user table
        :param cnx: The MySQLConnectionPool object
        :param email: The email of the customer
        :param hashed_password: The password hash of the customer
        :param company_id: The identifier of the company for which an invitation was sent
        :return: python int, the status of the insert
        """
        logging.info(START_OF_METHOD)
        insert_record_status = 200
        if company_id:
            cls._validate_company_id(
                cnx=cnx,
                company_id=company_id)
        try:
            cursor = cnx.cursor()
            cursor.execute(INSERT_CUSTOMER_INTO_USER_TABLE, [email, hashed_password, 'abc123', 0, company_id])
            cnx.commit()
            cursor.close()
        except Exception as e:
            logging.error('An error occurred inserting a customer into the user table',
                          extra={'information': {'error': str(e)}},
                          exc_info=True)
            insert_record_status = 500
        logging.info(END_OF_METHOD)
        return insert_record_status

    @staticmethod
    def execute_insertion_statement_for_subscription_table(cnx, table_response):
        """
        Inserts the regular SaaS user into the subscription table
        :param cnx: The MySQLConnectionPool
        :param table_response: The internal id for a customer in our system
        :return: python int
        """
        logging.info(START_OF_METHOD)
        insert_subscription_status = 200
        user_id = table_response['id']
        end_date = datetime.strftime(datetime.now(tz=ZoneInfo('America/Chicago')) + relativedelta(months=1),
                                     '%Y-%m-%d %H:%M:%S')
        try:
            cursor = cnx.cursor()
            cursor.execute(INSERT_SUBSCRIPTION_INFORMATION, [user_id, 'past_due', end_date])
            cnx.commit()
            cursor.close()
            logging.info(END_OF_METHOD)
            return insert_subscription_status
        except Exception as e:
            logging.error('An issue occurred inserting the user into the subscriptions table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            return 500

    @staticmethod
    def execute_update_statement_for_invitation_table(cnx, email):
        """
        Updates the activated_at column now that the user has signed up
        :param cnx: The MySQLConnectionPool
        :param email: The customer email
        :return: python int
        """
        logging.info(START_OF_METHOD)
        put_record_status = 200
        try:
            current_time = datetime.strftime(datetime.now(tz=ZoneInfo('America/Chicago')), '%Y-%m-%d %H:%M:%S')
            cursor = cnx.cursor()
            cursor.execute(UPDATE_INVITATION_INFORMATION, [current_time, email])
            cnx.commit()
            logging.info(END_OF_METHOD)
            return put_record_status
        except Exception as e:
            logging.error('An error occurred updating the invitations table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            return 500

    @classmethod
    def fetch_invitation_information(cls, cnx, email, token):
        """
        Validates that the customer signing up has a valid invitation
        :param cnx: The MySQLConnectionPool connection
        :param email: The customer email being used to sign up
        :param token: The UUID token extracted from the invite URL
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_INVITATION_INFORMATION, [token])
            table = cursor.fetchall()
            cursor.close()
            invitation_information = cls.format_invitation_table_response(
                email=email,
                table=table)
            logging.info(END_OF_METHOD)
            return invitation_information
        except Exception as e:
            logging.error('An error occurred fetching the invitation information',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def format_invitation_table_response(email, table):
        """
        Parses the information returned from the invitation table
        :param email: The email the user is signing up with
        :param table: The response from the invitation table
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        if not table:
            logging.error('The token included in the request is invalid')
            raise Error(INVALID_INVITATION)
        company_id = table[0][0]
        table_email = table[0][1]
        status = table[0][2]
        expires_at = table[0][3]
        if status != 'pending' or int(expires_at.timestamp()) < time.time():
            logging.error('This user does not qualify for an invitation sign up')
            raise Error(INVALID_INVITATION)
        if email != table_email:
            logging.error('The profile email does not match the invitation email')
            raise Error(INVALID_INVITATION)
        invitation_information = {
            'company_id': company_id,
            'email': email,
            'status': status
        }
        logging.info(END_OF_METHOD)
        return invitation_information

    @staticmethod
    def _validate_company_id(cnx, company_id):
        """
        Validates that the licensing company is active
        :param cnx: The MySQLConnectionPool object
        :param company_id: The internal identifier of a company
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_COMPANY_STATUS, [company_id])
            table = cursor.fetchall()
            cursor.close()
            if not table:
                logging.error('The company_id assigned to this customer no longer has an active license')
                raise Error(INVALID_INVITATION)
            if not bool(int(table[0][0])):
                logging.error('The company_id assigned to this customer no longer has an active license')
                raise Error(INVALID_INVITATION)
        except Exception as e:
            logging.error('An error occurred fetching company information for this user',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})

    @staticmethod
    def fetch_user_for_table_response(cnx, email):
        """
        Fetches the user just inserted into the table for the response to the insertion route
        :param cnx: The MySQLConnectionPool object
        :param email: The email of the customer inserted
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        try:
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

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

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
