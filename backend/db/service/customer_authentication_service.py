import logging
import jwt
import datetime
import stripe
from flask_bcrypt import Bcrypt
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_PASSWORD, USER_NOT_FOUND, INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import (SELECT_CUSTOMER_FOR_AUTHENTICATION,
                                                   SELECT_CUSTOMER_EMAIL_FIRST_AND_LAST,
                                                   SELECT_IS_PAID_STATUS_FOR_CUSTOMER)

bcrypt = Bcrypt()


class CustomerAuthenticationService:
    def __init__(self, hp_ai_db_connection_pool, secret_key):
        self.pool = hp_ai_db_connection_pool.pool
        self.secret_key = secret_key

    def authenticate_user_for_login(self, email, password):
        """
        Wrapper method that authenticates a user by validating they exist in the db and their password is correct
        :param email
        :param password:
        :return:
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        user_results = self.fetch_user_email_and_password_for_authentication(
            cnx=cnx,
            email=email)
        valid_jwt_token = self.generate_valid_jwt_token(
            password=password,
            user_results=user_results)
        cnx.close()
        response = {"token": valid_jwt_token,
                    "user": {"id": user_results[0][0],
                             "email": user_results[0][1]}}
        logging.info(END_OF_METHOD)
        return response

    def authenticate_users_payment_status_post_payment_login(self, session_id):
        """
        Checks the is paid status in the database to issue a valid JWT Token
        :param session_id: The sessionId from the Stripe checkout session
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        session = stripe.checkout.Session.retrieve(session_id)
        user_id = session.metadata.get("userId")
        cnx = self.obtain_connection()
        is_paid_status_information = self.fetch_is_paid_status_for_customer(
            cnx=cnx,
            user_id=user_id)
        response = self.format_response_for_post_login(
            user_id=user_id,
            is_paid_status_information=is_paid_status_information)
        cnx.close()
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def fetch_user_email_and_password_for_authentication(cnx, email):
        """
        Fetches a user's email (if they exist) from the user table
        :param cnx: The connection for the MySQLConnectionPool
        :param email: The customer's email
        :return: python list
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_CUSTOMER_FOR_AUTHENTICATION, [email])
            user_results = cursor.fetchall()
            cursor.close()
            logging.info(END_OF_METHOD)
            return user_results
        except Exception as e:
            logging.error('An issue occurred retrieving customer info for authentication',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    def generate_valid_jwt_token_after_payment(self, cnx, user_id):
        """
        Function used ot generate a valid jwt token after a customer has paid
        :param cnx: The connection for the MySQLConnectionPool
        :param user_id: The internal identifier for a customer in our system
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        user_results = self.fetch_user_information_for_payment_update_token(
            cnx=cnx,
            user_id=user_id)
        user_email = user_results[0][0]
        first_name = user_results[0][1]
        last_name = user_results[0][2]
        payload = {
            'user_id': user_id,
            'email': user_email,
            'first_name': first_name,
            'last_name': last_name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        valid_jwt_token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        logging.info(END_OF_METHOD)
        return valid_jwt_token, user_email

    @staticmethod
    def fetch_user_information_for_payment_update_token(cnx, user_id):
        """
        Invoked in the update-payment-status route
        :param cnx: The connection for the MySQLConnectionPool
        :param user_id: The internal identifier for a customer in our system
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_CUSTOMER_EMAIL_FIRST_AND_LAST, [user_id])
            user_results = cursor.fetchall()
            cursor.close()
            logging.info(END_OF_METHOD)
            return user_results
        except Exception as e:
            logging.error('An issue occurred retrieving customer info for authentication',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def fetch_is_paid_status_for_customer(cnx, user_id):
        """
        Checks to see if a customer's payment successfully
        :param cnx:
        :param user_id:
        :return:
        """
        logging.info(START_OF_METHOD)
        cursor = cnx.cursor()
        cursor.execute(SELECT_IS_PAID_STATUS_FOR_CUSTOMER, [user_id])
        table = cursor.fetchall()
        cursor.close()
        if table:
            is_paid_status_information = {
                'is_paid': table[0][0],
                'email': table[0][1],
                'first_name': table[0][2],
                'last_name': table[0][3]
            }
        else:
            is_paid_status_information = {'is_paid': 0}
        logging.info(END_OF_METHOD)
        return is_paid_status_information

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    def generate_valid_jwt_token(self, password, user_results):
        """
        Generates a valid jwt token to send back to the frontend in the event a customer is authenticated
        :param password: The customer password
        :param user_results: The results from the user table
        :return: python str, a jwt token
        """
        logging.info(START_OF_METHOD)
        if not user_results:
            logging.error('The provided email is not valid')
            raise Error(USER_NOT_FOUND)
        user_id = user_results[0][0]
        user_email = user_results[0][1]
        user_hashed_password = user_results[0][2]
        first_name = user_results[0][3]
        last_name = user_results[0][4]
        if not bcrypt.check_password_hash(user_hashed_password, password):
            logging.error('The provided password is not valid')
            raise Error(INVALID_PASSWORD)
        payload = {
            'user_id': user_id,
            'email': user_email,
            'first_name': first_name,
            'last_name': last_name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        valid_jwt_token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        logging.info(END_OF_METHOD)
        return valid_jwt_token

    def format_response_for_post_login(self, user_id, is_paid_status_information):
        """
        Formats response for frontend by issuing a valid JWT token if customer has paid
        :param user_id: The internal identifier of a user in our system
        :param is_paid_status_information:
        :return:
        """
        logging.info(START_OF_METHOD)
        is_paid_status = is_paid_status_information['is_paid']
        if is_paid_status:
            email = is_paid_status_information['email']
            first_name = is_paid_status_information['first_name']
            last_name = is_paid_status_information['last_name']
            payload = {
                'user_id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            valid_jwt_token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            response = {'token': valid_jwt_token,
                        'is_paid': True,
                        'user': {
                            'id': user_id,
                            'email': email
                        }}
        else:
            response = {'is_paid': False}
        logging.info(END_OF_METHOD)
        return response
