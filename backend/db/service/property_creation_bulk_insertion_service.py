import logging
import pandas as pd
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR, INVALID_REQUEST, INVALID_BULK_CSV_FILE
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD


class PropertyCreationBulkInsertionService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def bulk_upload_properties_into_db(self, bulk_insertion_request):
        """
        Uploads the contents of the CSV file into our database
        :param bulk_insertion_request: The model object responsible for storing our data
        :return: python dict, the response for the route
        """
        logging.info(START_OF_METHOD)
        self.validate_contents_of_csv_file(csv_file=bulk_insertion_request.csv_file)

        logging.info(END_OF_METHOD)

    @staticmethod
    def validate_contents_of_csv_file(csv_file):
        """
        Parses the contents of the file to ensure the user uploaded the correct information
        :param csv_file: The csv file sent to the route from the frontend
        """
        logging.info(START_OF_METHOD)
        bulk_properties_df = pd.read_csv(csv_file)
