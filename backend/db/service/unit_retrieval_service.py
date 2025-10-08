import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import GET_UNITS_BY_PROPERTY_ID, SELECT_PROPERTY_BY_PROPERTY_ID


class UnitRetrievalService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def fetch_units_by_property_id(self, property_id, user_id):
        """
        Retrieves all units associated with a specific property
        Verifies that the property belongs to the requesting user
        :param property_id: python int, The internal id of a property
        :param user_id: python int, The internal id of the user making the request
        :return: python list of dicts
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()

        # First verify the property exists and belongs to the user
        property_data = self.verify_property_ownership(cnx, property_id, user_id)

        if not property_data:
            cnx.close()
            logging.warning(f'Property {property_id} not found or does not belong to user {user_id}')
            return []

        # Fetch units for the property
        results = self.execute_retrieval_statement(cnx, property_id)
        formatted_results = self.format_unit_results(results)

        cnx.close()
        logging.info(END_OF_METHOD)
        return formatted_results

    @staticmethod
    def verify_property_ownership(cnx, property_id, user_id):
        """
        Verifies that a property belongs to a specific user
        :param cnx: MySQLConnectionPool connection
        :param property_id: The id of a property
        :param user_id: The id of the user
        :return: property data if owned by user, None otherwise
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_PROPERTY_BY_PROPERTY_ID, [property_id])
            result = cursor.fetchone()
            cursor.close()

            if not result:
                logging.warning(f'Property {property_id} not found')
                return None

            # Check if property belongs to user (user_id is at index 1)
            property_user_id = int(result[1])
            if property_user_id != user_id:
                logging.warning(f'Property {property_id} does not belong to user {user_id}')
                return None

            logging.info(END_OF_METHOD)
            return result
        except Exception as e:
            logging.error('An issue occurred verifying property ownership',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def execute_retrieval_statement(cnx, property_id):
        """
        Executes the SELECT statement to fetch units for a property
        :param cnx: MySQLConnectionPool connection
        :param property_id: The id of a property in our system
        :return: python list
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(GET_UNITS_BY_PROPERTY_ID, [property_id])
            result = cursor.fetchall()
            cursor.close()
            logging.info(END_OF_METHOD)
            return result
        except Exception as e:
            logging.error('An issue occurred fetching units from the database',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def format_unit_results(results):
        """
        Formats the results from the units table
        :param results: The results from the database
        :return: python list of dicts
        """
        logging.info(START_OF_METHOD)
        formatted_results = []

        if not results:
            return formatted_results

        for row in results:
            unit_id = int(row[0])
            unit_number = row[1]
            property_id = int(row[2])
            created_at = row[3]
            updated_at = row[4]

            data = {
                'unit_id': unit_id,
                'unit_number': unit_number,
                'property_id': property_id,
                'created_at': created_at,
                'updated_at': updated_at
            }
            formatted_results.append(data)

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
