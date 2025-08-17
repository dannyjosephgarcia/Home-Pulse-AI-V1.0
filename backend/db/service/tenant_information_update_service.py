import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR


class TenantInformationUpdateService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def update_tenant_information(self, update_tenant_information_request):
        """
        Updates the information for a property in our database
        :param update_tenant_information_request:
        :return:
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        dynamic_update_statement, values = self._construct_dynamic_tenant_information_update_statement(
            update_tenant_information_request=update_tenant_information_request)
        put_record_status = self.execute_tenant_information_update_statement(
            cnx=cnx,
            dynamic_update_statement=dynamic_update_statement,
            values=values)
        response = self.format_update_tenant_information_response(
            put_record_status=put_record_status)
        cnx.close()
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def execute_tenant_information_update_statement(cnx, dynamic_update_statement, values):
        """
        Dynamically updates the information about a tenant
        :param cnx: The MySQLConnectionPool object
        :param dynamic_update_statement: python str, a variable query string constructed earlier
        :param values: The values that are to be updated
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        put_record_status = 200
        try:
            cursor = cnx.cursor()
            cursor.execute(dynamic_update_statement, values)
            cnx.commit()
            cursor.close()
            logging.info(END_OF_METHOD)
            return put_record_status
        except Exception as e:
            logging.error('An error occurred updating the tenant information in the tenants table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            put_record_status = 500
            return put_record_status

    @staticmethod
    def _construct_dynamic_tenant_information_update_statement(update_tenant_information_request):
        """
        Constructs an update statement based on the items passed to the UpdateTenantInformationRequest object
        :param update_tenant_information_request: The UpdateTenantInformationRequest model object
        :return: python str
        """
        logging.info(START_OF_METHOD)
        updates = {}
        for key, value in update_tenant_information_request.__dict__.items():
            if value is not None and key != 'tenant_id':
                updates[key] = value
        try:
            fields = []
            values = []
            for col, val in updates.items():
                fields.append(f"{col}=%s")
                values.append(val)
            dynamic_update_statement = f"UPDATE home_pulse_ai.tenants SET {', '.join(fields)} WHERE id=%s;"
            values.append(update_tenant_information_request.tenant_id)
            logging.info(END_OF_METHOD)
            return dynamic_update_statement, values
        except Exception as e:
            logging.error('An issue occurred attempting to construct the update query string',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def format_update_tenant_information_response(put_record_status):
        """
        Returns the response code for updating a row in the db
        :param put_record_status: The status of updating a row in the db
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        response = {
            'put_record_status': put_record_status
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