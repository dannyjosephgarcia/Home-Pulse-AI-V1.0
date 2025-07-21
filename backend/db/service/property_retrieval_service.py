import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import (SELECT_PROPERTY_BY_PROPERTY_ID, SELECT_APPLIANCES_BY_PROPERTY_ID,
                                                   SELECT_PROPERTIES_BY_USER_ID, SELECT_STRUCTURES_BY_PROPERTY_ID)


class PropertyRetrievalService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def fetch_property_information(self, user_id=None, property_id=None, retrieval_type='ALL'):
        """
        Retrieves all properties associated with a single user
        :param user_id: python int, The internal id of a customer
        :param property_id: python int or None, The internal id of a property
        :param retrieval_type: python str, the type of retrieval to be executed
        :return:
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        results = self.execute_retrieval_statement(
            cnx=cnx,
            user_id=user_id,
            property_id=property_id,
            retrieval_type=retrieval_type)
        formatted_results = self.format_property_results()

        logging.info(END_OF_METHOD)

    @staticmethod
    def execute_retrieval_statement(cnx, user_id, property_id, retrieval_type):
        """
        Function actually executes the SELECT statement responsible for fetching the correct items
        :param cnx: MySQLConnectionPool connection
        :param user_id: The id of an internal user
        :param property_id: The id of a property in our system
        :param retrieval_type: The type of retrieval being performed
        :return: python list
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            if retrieval_type == 'ALL':
                cursor.execute(SELECT_PROPERTIES_BY_USER_ID, [user_id])
            elif retrieval_type == 'SINGLE':
                cursor.execute(SELECT_PROPERTY_BY_PROPERTY_ID, [property_id])
            elif retrieval_type == 'APPLIANCES':
                cursor.execute(SELECT_APPLIANCES_BY_PROPERTY_ID, [property_id])
            elif retrieval_type == 'STRUCTURES':
                cursor.execute(SELECT_STRUCTURES_BY_PROPERTY_ID, [property_id])
            result = cursor.fetchall()
            cursor.close()
            logging.info(END_OF_METHOD)
            return result
        except Exception as e:
            logging.error('An issue occurred fetching properties from the database',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def format_property_results(results, retrieval_type):
        """
        Formats the results from the properties table depending on the frontend view being populated
        :param results: The results from the database
        :param retrieval_type: The type of retrieval that was executed
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        formatted_results = {}
        if retrieval_type == 'ALL':
            pass
        elif retrieval_type == 'SINGLE':
            property_id = int(results[0][0])
            user_id = int(results[0][1])
            postal_code = results[0][2]
            age = int(results[0][3])
            address = results[0][4]
            created_at = results[0][5]
            formatted_results.update({
                'id': property_id,
                'user_id': user_id,
                'postal_code': postal_code,
                'age': age,
                'address': address,
                'created_at': created_at
            })
        elif retrieval_type == 'APPLIANCES':
            property_id = results[0][0]
        elif retrieval_type == 'STRUCTURES':
            pass
        logging.info(END_OF_METHOD)
        return formatted_results

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)
