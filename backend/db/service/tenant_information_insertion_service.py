import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import INSERT_TENANT_INFORMATION_INTO_TENANTS_TABLE


class TenantInformationInsertionService:
    def __init__(self, hp_ai_db_connection_pool, tenant_information_retrieval_service):
        self.pool = hp_ai_db_connection_pool.pool
        self.tenant_information_retrieval_service = tenant_information_retrieval_service

    def insert_tenant_information(self, tenant_creation_request):
        """
        Fetches the information about a tenant from a tenant table
        :param tenant_creation_request: The TenantCreationRequest model object
        :return: python dict, the response for the route
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        insert_record_status = self.execute_tenant_insertion_statement(
            cnx=cnx,
            tenant_creation_request=tenant_creation_request)
        insert_record_results = self.tenant_information_retrieval_service.execute_tenant_retrieval_statement(
            cnx=cnx,
            property_id=tenant_creation_request.property_id)
        formatted_results = self.tenant_information_retrieval_service.format_tenant_information_results(
            results=insert_record_results)
        cnx.close()
        logging.info(END_OF_METHOD,
                     extra={'information': {'insertRecordStatus': insert_record_status}})
        return formatted_results

    @staticmethod
    def execute_tenant_insertion_statement(cnx, tenant_creation_request):
        """
        Retrieves the information for a tenant of a property
        :param cnx: The connection pool object
        :param tenant_creation_request: The TenantCreationRequest model object
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(INSERT_TENANT_INFORMATION_INTO_TENANTS_TABLE, [tenant_creation_request.property_id,
                                                                          tenant_creation_request.first_name,
                                                                          tenant_creation_request.last_name,
                                                                          tenant_creation_request.contract_start_date,
                                                                          tenant_creation_request.contract_end_date,
                                                                          tenant_creation_request.current_rent,
                                                                          tenant_creation_request.phone_number])
            cnx.commit()
            cursor.close()
            logging.info(END_OF_METHOD)
            return 200
        except Exception as e:
            logging.error('There was an issue retrieving information from the tenants table',
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
