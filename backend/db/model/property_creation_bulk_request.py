import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD
from common.logging.error.error_messages import INVALID_REQUEST
import io


class PropertyCreationBulkRequest:
    def __init__(self, files):
        self.validate_bulk_property_creation_request(files)
        self.csv_file = files.get('file')
        self.raw_bytes = self.csv_file.read()
        self.text = self.raw_bytes.decode('utf-8')
        self.content = io.StringIO(self.text)

    @staticmethod
    def validate_bulk_property_creation_request(files):
        """
        Validates that the file present is a csv file
        :param files: The request to the bulk-csv-upload route
        """
        logging.info(START_OF_METHOD)
        try:
            files['file']
        except Exception as e:
            logging.error('There was an issue passing the CSV file to the route',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INVALID_REQUEST)
