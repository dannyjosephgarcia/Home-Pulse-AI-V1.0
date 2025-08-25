import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import UPDATE_APPLIANCE_INFORMATION


class LowesAppliancePriceAnalysisService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def update_appliance_information_prices(self, average_prices):
        """
        Wrapper method that updates the appliance information in the db
        :return: python dict, the response
        """
        logging.info(START_OF_METHOD)
        update_statements = self.create_update_statements(
            average_prices=average_prices)
        cnx = self.obtain_connection()
        put_record_status = self.update_appliance_prices(
            cnx=cnx,
            update_statements=update_statements)
        cnx.close()
        logging.info(END_OF_METHOD)
        return put_record_status

    @staticmethod
    def update_appliance_prices(cnx, update_statements):
        """
        Will need to generalize
        :param cnx: The MySQLConnectionPool object
        :param update_statements
        :return:
        """
        logging.info(START_OF_METHOD)
        put_record_status = 200
        try:
            cursor = cnx.cursor()
            cursor.executemany(UPDATE_APPLIANCE_INFORMATION, update_statements)
            cnx.commit()
            cursor.close()
            logging.info(END_OF_METHOD)
            return put_record_status
        except Exception as e:
            logging.error('An issue occurred uploading information to the database',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            put_record_status = 500
            return put_record_status

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def create_update_statements(average_prices):
        """
        Helper method that extracts the price from the object returned after scrape
        :param average_prices: The data returned from scraping
        :return:
        """
        logging.info(START_OF_METHOD)
        update_statement_values = []
        for appliance_name, average_price in average_prices.items():
            if float(average_price) > 0.00:
                update_statement_values.append((average_price, appliance_name))
        return update_statement_values
