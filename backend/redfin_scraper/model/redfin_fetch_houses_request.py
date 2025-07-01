import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_REQUEST


class RedfinFetchHousesRequest:
    def __init__(self, request):
        """
        Model object that stores request information for the /v1/fetch_houses route
        :param request: python dict, the request to the Flask route
        """
        self._validate_request(request=request)
        self.postal_code = request['postalCode']

    @classmethod
    def _validate_request(cls, request):
        """
        Validates the fields of the request
        :param request: python dict, the request to the Flask route
        """
        logging.info(START_OF_METHOD)
        if 'postalCode' not in request:
            logging.error('The postalCode field is a required field')
            raise Error(INVALID_REQUEST)
        cls._validate_field_types(request=request)

    @staticmethod
    def _validate_field_types(request):
        """
        Validates the field types of the fields of the request
        :param request: python dict, the request to the Flask route
        """
        if not request['postalCode'].isdigit():
            logging.error('The postalCode field must be an integer')
            raise Error(INVALID_REQUEST)
