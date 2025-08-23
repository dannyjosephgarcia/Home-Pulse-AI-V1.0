import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import UPDATE_APPLIANCE_INFORMATION


class LowesAppliancePriceAnalysisService:
    def __init__(self, hp_ai_db_connection_pool, lowes_client):
        self.pool = hp_ai_db_connection_pool.pool
        self.client = lowes_client

    def update_appliance_information_prices(self):
        """
        Wrapper method that updates the appliance information in the db
        :return: python dict, the response
        """
        logging.info(START_OF_METHOD)
        product_data = self.client.search_appliances(
            category='dishwasher')
        dishwasher_response = self.handle_product_data(
            product_data=product_data)
        cnx = self.obtain_connection()
        put_record_status = self.update_appliance_prices(cnx=cnx, response=dishwasher_response)
        cnx.close()
        self.client.close()
        logging.info(END_OF_METHOD)
        return put_record_status

    @staticmethod
    def update_appliance_prices(cnx, response):
        """
        Will need to generalize
        :param cnx: The MySQLConnectionPool object
        :param response:
        :return:
        """
        logging.info(START_OF_METHOD)
        put_record_status = 200
        try:
            cursor = cnx.cursor()
            cursor.execute(UPDATE_APPLIANCE_INFORMATION, [response['appliance_price'],
                                                          response['appliance_category']])
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
    def handle_product_data(product_data):
        """
        Helper method that extracts the price from the object returned after scrape
        :param product_data: The data returned from scraping
        :return:
        """
        logging.info(START_OF_METHOD)
        total_prices = 0.00
        for data in product_data:
            total_prices += float(data['price'])
        average_price = round(total_prices/len(product_data), 2)
        dishwasher_response = {
            'appliance_type': 'DISHWASHER',
            'appliance_price': average_price
        }
        logging.info(END_OF_METHOD)
        return dishwasher_response
