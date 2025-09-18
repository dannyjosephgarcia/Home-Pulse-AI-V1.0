import logging
import pandas as pd
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR, INVALID_REQUEST, INVALID_BULK_CSV_FILE
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from backend.db.model.query.sql_statements import INSERT_PROPERTY_INFORMATION_BULK


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
        cnx = self.obtain_connection()
        bulk_properties_df = self.validate_contents_of_csv_file(
            content=bulk_insertion_request.content)
        data_to_upload = self.parse_csv_file_for_upload(
            bulk_properties_df=bulk_properties_df
        )
        insert_record_status = self.execute_bulk_properties_insertion(
            cnx=cnx,
            data_to_upload=data_to_upload)
        response = {'insertRecordStatus': insert_record_status}
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def validate_contents_of_csv_file(content):
        """
        Parses the contents of the file to ensure the user uploaded the correct information
        :param content: The content of the CSV file
        """
        logging.info(START_OF_METHOD)
        try:
            bulk_properties_df = pd.read_csv(content)
            logging.info(END_OF_METHOD)
            return bulk_properties_df
        except Exception as e:
            logging.error('There was an issue parsing the CSV file',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INVALID_BULK_CSV_FILE)

    @staticmethod
    def parse_csv_file_for_upload(bulk_properties_df):
        """
        Parses the dataframe generated from the CSV file to upload to the database
        :param bulk_properties_df: The bulk property file
        :return: python list
        """
        logging.info(START_OF_METHOD)
        data_to_upload = []
        for row in bulk_properties_df.itertuples(index=False):
            street = row.street
            city = row.city
            state = row.state
            postal_code = row.postal_code
            unit = row.unit
            # TODO: Finish this loop
            data_to_upload.append((street, city, state, postal_code, unit))
        return data_to_upload

    @staticmethod
    def execute_bulk_properties_insertion(cnx, data_to_upload):
        """
        Uploads the file to our appliances and structures database
        :param cnx: The MySQLConnectionPool
        :param data_to_upload: The data to upload to the route
        :return: python int
        """
        logging.info(START_OF_METHOD)
        insert_record_status = 200
        try:
            cursor = cnx.get_cursor()
            cursor.executemany(INSERT_PROPERTY_INFORMATION_BULK, data_to_upload)
            cnx.commit()
            cursor.close()
            logging.info(END_OF_METHOD)
            return insert_record_status
        except Exception as e:
            logging.error('There was an issue bulk uploading to the table',
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
