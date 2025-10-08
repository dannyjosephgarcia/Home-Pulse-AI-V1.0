import logging
from datetime import datetime
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import GET_APPLIANCES_BY_UNIT_ID, VERIFY_UNIT_OWNERSHIP


class UnitApplianceRetrievalService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def fetch_appliances_by_unit_id(self, unit_id, user_id):
        """
        Retrieves all appliances associated with a specific unit
        Verifies that the unit belongs to a property owned by the requesting user
        :param unit_id: python int, The internal id of a unit
        :param user_id: python int, The internal id of the user making the request
        :return: python list of dicts
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()

        # First verify the unit belongs to a property owned by the user
        is_authorized = self.verify_unit_authorization(cnx, unit_id, user_id)

        if not is_authorized:
            cnx.close()
            logging.warning(f'Unit {unit_id} not found or does not belong to user {user_id}')
            return []

        # Fetch appliances for the unit
        results = self.execute_retrieval_statement(cnx, unit_id)
        formatted_results = self.format_appliance_results(results)

        cnx.close()
        logging.info(END_OF_METHOD)
        return formatted_results

    @staticmethod
    def verify_unit_authorization(cnx, unit_id, user_id):
        """
        Verifies that a unit belongs to a property owned by a specific user
        :param cnx: MySQLConnectionPool connection
        :param unit_id: The id of a unit
        :param user_id: The id of the user
        :return: boolean indicating if user is authorized
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(VERIFY_UNIT_OWNERSHIP, [unit_id, user_id])
            result = cursor.fetchone()
            cursor.close()

            if not result:
                logging.warning(f'Unit {unit_id} not found or does not belong to user {user_id}')
                return False

            logging.info(END_OF_METHOD)
            return True
        except Exception as e:
            logging.error('An issue occurred verifying unit authorization',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def execute_retrieval_statement(cnx, unit_id):
        """
        Executes the SELECT statement to fetch appliances for a unit
        :param cnx: MySQLConnectionPool connection
        :param unit_id: The id of a unit in our system
        :return: python list
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(GET_APPLIANCES_BY_UNIT_ID, [unit_id])
            result = cursor.fetchall()
            cursor.close()
            logging.info(END_OF_METHOD)
            return result
        except Exception as e:
            logging.error('An issue occurred fetching appliances from the database',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def format_appliance_results(results):
        """
        Formats the results from the appliances table
        :param results: The results from the database
        :return: python list of dicts
        """
        logging.info(START_OF_METHOD)
        formatted_results = []

        if not results:
            return formatted_results

        for row in results:
            appliance_id = int(row[0])
            property_id = int(row[1])
            unit_id = int(row[2]) if row[2] is not None else None
            appliance_type = row[3]
            appliance_brand = row[4]
            appliance_model = row[5]
            age_in_years = int(row[6])
            estimated_replacement_cost = float(row[7]) if row[7] is not None else None

            # Handle forecasted_replacement_date
            if row[8]:
                forecasted_replacement_date = datetime.strftime(row[8], '%Y-%m-%d %H:%M:%S')
            else:
                forecasted_replacement_date = 'TBD'

            data = {
                'id': appliance_id,
                'property_id': property_id,
                'unit_id': unit_id,
                'appliance_type': appliance_type,
                'appliance_brand': appliance_brand,
                'appliance_model': appliance_model,
                'age_in_years': age_in_years,
                'estimated_replacement_cost': estimated_replacement_cost,
                'forecasted_replacement_date': forecasted_replacement_date
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
