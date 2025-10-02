import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from datetime import datetime, date
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import SELECT_PROPERTY_INFORMATION_BY_USER_FOR_MANAGEMENT_TAB


class PropertyNeedsAttentionRetrievalService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def fetch_properties_that_need_attention(self, user_id):
        """
        Wrapper function that queries for properties that need attention based upon appliance/structure replacement date
        :param user_id: The internal identifier of a user in our system
        :return: python dict, the response
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        result = self.execute_retrieve_outdated_components_statement(
            cnx=cnx,
            user_id=user_id)
        response = self.format_outdated_components_response(result)
        cnx.close()
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def execute_retrieve_outdated_components_statement(cnx, user_id):
        """
        Executes the SELECT statement to retrieve all properties associated with a user for parsing
        :param cnx: The MySQLConnectionPool connection
        :param user_id: The internal identifier of a user in our system
        :return: python list
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_PROPERTY_INFORMATION_BY_USER_FOR_MANAGEMENT_TAB, [user_id, user_id])
            result = cursor.fetchall()
            cursor.close()
            logging.info(END_OF_METHOD)
            return result
        except Exception as e:
            logging.error('There was an issue retrieving out-of-date components for the management tabe',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @classmethod
    def format_outdated_components_response(cls, result):
        """
        Formats the result for the frontend dashboard page
        :param result: The items returned from the appliances and structures table
        :return: python dict, the response of the route
        """
        logging.info(START_OF_METHOD)
        response = {'properties': [],
                    'managementItems': [],
                    'components': []}
        property_addresses = set()
        if not result:
            return response
        for i in range(len(result)):
            component_id = result[i][0]
            property_id = result[i][1]
            component_name = result[i][2]
            component_age = result[i][3]
            component_cost = float(result[i][4])
            forecasted_replacement_date = result[i][5]
            property_address = result[i][6]
            status = 'coming_due'
            days_difference = cls.compute_days_difference(forecasted_replacement_date=forecasted_replacement_date)
            if days_difference >= 0:
                status = 'overdue'
            item = {
                'id': component_id,
                'name': component_name,
                'status': status,
                'property_id': property_id,
                'property_address': property_address,
                'forecasted_replacement_date': forecasted_replacement_date,
                'days_difference': days_difference
            }
            component = {
                'id': component_id,
                'name': component_name,
                'age': component_age,
                'forecasted_replacement_date': forecasted_replacement_date,
                'cost': component_cost
            }
            response['managementItems'].append(item)
            response['components'].append(component)
            if property_address not in property_addresses:
                response['properties'].append({
                    'id': property_id,
                    'address': property_address
                })
                property_addresses.add(property_address)
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def compute_days_difference(forecasted_replacement_date):
        """
        Computes the difference between the current date and the forecasted date
        :param forecasted_replacement_date: The forecasted replacement date of the component
        :return: python int
        """
        logging.info(START_OF_METHOD)
        today = date.today()
        dt_date = forecasted_replacement_date.date()
        diff_days = (today - dt_date).days
        logging.info(END_OF_METHOD)
        return diff_days

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)
