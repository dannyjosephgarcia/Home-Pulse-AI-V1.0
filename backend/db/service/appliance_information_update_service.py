import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
import datetime
from backend.db.model.query.sql_statements import UPDATE_APPLIANCE_INFORMATION_BULK


class ApplianceInformationUpdateService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def update_appliance_information(self, update_appliance_information_request):
        """
        Wrapper method that updates the appliances in our db
        :param update_appliance_information_request: The model object storing the data to the PUT route
        :return: python dict, the response
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        put_record_status = self.execute_update_statement_for_appliance_table(
            cnx=cnx,
            property_id=update_appliance_information_request.property_id,
            appliance_updates=update_appliance_information_request.appliance_updates)
        response = {'putRecordStatus': put_record_status}
        logging.info(END_OF_METHOD)
        return response

    @classmethod
    def execute_update_statement_for_appliance_table(cls, cnx, property_id, appliance_updates):
        """
        Updates appliance information within the appliance table
        :param cnx: The MySQLConnectionPool Object
        :param property_id: The internal identifier of a property in our system
        :param appliance_updates: python list, a list of updates
        :return: python int
        """
        logging.info(START_OF_METHOD)
        put_record_status = 200
        try:
            update_execute_many_data = cls.construct_execute_many_data_object(
                property_id=property_id,
                appliance_updates=appliance_updates)
            cursor = cnx.cursor()
            cursor.executemany(UPDATE_APPLIANCE_INFORMATION_BULK, update_execute_many_data)
            cnx.commit()
            cursor.close()
            logging.info(END_OF_METHOD)
            return put_record_status
        except Exception as e:
            logging.error('There was an issue updating the appliances in the appliance table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            return 500

    @staticmethod
    def construct_execute_many_data_object(property_id, appliance_updates):
        """
        Creates the list of data being requested to be updated
        :param property_id: The internal id of a property in our system
        :param appliance_updates: The request appliance updates
        :return: python list
        """
        logging.info(START_OF_METHOD)
        items = []
        for appliance in appliance_updates:
            appliance_type = appliance['appliance_type']
            age_in_years = appliance['age_in_years']
            estimated_replacement_cost = appliance['estimated_replacement_cost']
            forecasted_replacement_date = datetime.datetime.strptime(appliance['forecasted_replacement_date'],
                                                                     '%Y-%m-%d %H:%M:%S')
            # Extract optional brand and model fields (use None as default)
            appliance_brand = appliance.get('applianceBrand')
            appliance_model = appliance.get('applianceModel')

            # Data tuple matches the UPDATE statement parameter order:
            # age_in_years, estimated_replacement_cost, forecasted_replacement_date, appliance_brand, appliance_model, property_id, appliance_type
            data = (age_in_years, estimated_replacement_cost, forecasted_replacement_date, appliance_brand, appliance_model, property_id, appliance_type)
            items.append(data)
        return items

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)
