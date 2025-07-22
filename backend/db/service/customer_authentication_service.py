import logging
import jwt
import datetime
from flask_bcrypt import Bcrypt
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_PASSWORD, USER_NOT_FOUND, INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import SELECT_CUSTOMER_FOR_AUTHENTICATION

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
        if not bcrypt.check_password_hash(user_hashed_password, password):
            logging.error('The provided password is not valid')
            raise Error(INVALID_PASSWORD)
        payload = {
            'user_id': user_id,
            'email': user_email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        valid_jwt_token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        logging.info(END_OF_METHOD)
        return valid_jwt_token
