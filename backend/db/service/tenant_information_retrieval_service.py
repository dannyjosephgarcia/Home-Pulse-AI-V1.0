import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import SELECT_TENANT_INFORMATION_BY_PROPERTY_ID


class TenantInformationRetrievalService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def fetch_tenant_information(self, property_id):
        """
        Fetches the information about a tenant from a tenant table
        :param property_id: The ID of a property
        :return:
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        results = self.execute_tenant_retrieval_statement(
            cnx=cnx,
            property_id=property_id)
        formatted_results = self.format_tenant_information_results(
            results=results)
        cnx.close()
        logging.info(END_OF_METHOD)
        return formatted_results

    @staticmethod
    def execute_tenant_retrieval_statement(cnx, property_id):
        """
        Retrieves the information for a tenant of a property
        :param cnx: The connection pool object
        :param property_id: The ID of a property
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_TENANT_INFORMATION_BY_PROPERTY_ID, [property_id])
            result = cursor.fetchall()
            cursor.close()
            logging.info(END_OF_METHOD)
            return result
        except Exception as e:
            logging.error('There was an issue retrieving information from the tenants table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def format_tenant_information_results(results):
        """
        Formats the results from the tenant information table
        :param results: The results pulled from the tenants table
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        if not results:
            return [{}]
        tenant_id = results[0][0]
        property_id = results[0][1]
        first_name = results[0][2]
        last_name = results[0][3]
        contract_start_date = datetime.strftime(results[0][4], '%Y-%m-%d')
        contract_end_date = datetime.strftime(results[0][5], '%Y-%m-%d')
        contract_status = results[0][6]
        recommended_replacement_date = datetime.strftime(results[0][7], '%Y-%m-%d')
        monthly_rent = float(results[0][8])
        relative_contract_duration = relativedelta(results[0][5], results[0][4])
        contract_duration_months = relative_contract_duration.years * 12 + relative_contract_duration.months
        formatted_results = [{
            'id': tenant_id,
            'property_id': property_id,
            'first_name': first_name,
            'last_name': last_name,
            'contract_start_date': contract_start_date,
            'contract_end_date': contract_end_date,
            'is_current': True if contract_status == 'active' else False,
            'current_rent': monthly_rent,
            'recommended_replacement_dates': recommended_replacement_date,
            'contract_duration_months': contract_duration_months
        }]
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
