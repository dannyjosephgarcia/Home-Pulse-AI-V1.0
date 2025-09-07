import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import UPDATE_FORECASTED_REPLACEMENT_DATE


class ForecastedReplacementDateUpdateService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def update_forecasted_replacement_date(self, property_id, appliance_type, forecasted_replacement_date):
        """
        Wrapper method that updates db table
        :param property_id: The internal id of a property in our system
        :param appliance_type: The appliance in the property to be updated
        :param forecasted_replacement_date: The date of replacement
        :return: python dict, response
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        put_record_status = self.execute_forecasted_date_update_statement(
            cnx=cnx,
            property_id=property_id,
            appliance_type=appliance_type,
            forecasted_replacement_date=forecasted_replacement_date)
        response = {'putRecordStatus': put_record_status}
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def execute_forecasted_date_update_statement(cnx, property_id, appliance_type, forecasted_replacement_date):
        """
        Performs the actual UPDATE statement
        :param cnx: The MySQLConnectionPool object
        :param property_id: The internal id of a property in our system
        :param appliance_type: The type of appliance being updated
        :param forecasted_replacement_date: The date being updated in our database
        :return: python int, the status of the update
        """
        logging.info(START_OF_METHOD)
        put_record_status = 200
        try:
            cursor = cnx.cursor()
            cursor.execute(UPDATE_FORECASTED_REPLACEMENT_DATE, 
                           [forecasted_replacement_date, property_id, appliance_type])
            cnx.commit()
            cursor.close()
            logging.info(END_OF_METHOD)
            return put_record_status
        except Exception as e:
            logging.error('An issue occurred updating the forecasted replacement date',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            return 500


    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)