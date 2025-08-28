import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD
from common.logging.error.error_messages import INVALID_REQUEST


class PropertyImageInsertionRequest:
    def __init__(self, request):
        self._validate_property_image_insertion_request(request)
        self.file_name = request['fileName']

    @staticmethod
    def _validate_property_image_insertion_request(request):
        """
        Validates the request to the property image insertion route
        :param request: The request body
        """
        logging.info(START_OF_METHOD)
        if 'fileName' not in request:
            logging.error('A fileName needs to be passed')
            raise Error(INVALID_REQUEST)
