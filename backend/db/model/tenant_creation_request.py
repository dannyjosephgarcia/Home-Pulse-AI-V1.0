import logging
import datetime
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD
from common.logging.error.error_messages import INVALID_REQUEST


class TenantCreationRequest:
    def __init__(self, property_id, request):
        self.validate_tenant_creation_request(request)
        self.property_id = int(property_id)
        self.first_name = request['first_name']
        self.last_name = request['last_name']
        self.contract_start_date = request['contract_start_date']
        self.contract_end_date = request['contract_end_date']
        self.current_rent = request['current_rent']
        self.phone_number = request['phone_number']

    @staticmethod
    def validate_tenant_creation_request(request):
        """
        Validates the request to the POST route that inserts information into the tenant table
        :param request: The request to the route
        """
        logging.info(START_OF_METHOD)
        if 'first_name' not in request:
            logging.error('The first_name field is a required field')
            raise Error(INVALID_REQUEST)
        if 'last_name' not in request:
            logging.error('The last_name field is a required field')
            raise Error(INVALID_REQUEST)
        if 'contract_start_date' not in request:
            logging.error('The contract_start_date is a required field')
            raise Error(INVALID_REQUEST)
        if 'contract_end_date' not in request:
            logging.error('The contract end date is a required field')
            raise Error(INVALID_REQUEST)
        if 'current_rent' not in request:
            logging.error('The current rent field is a required field')
            raise Error(INVALID_REQUEST)
        if 'phone_number' not in request:
            logging.error('The phone number field is a required field')
            raise Error(INVALID_REQUEST)
        try:
            datetime.datetime.strptime(request['contract_start_date'], '%Y-%m-%d')
        except Exception as e:
            logging.error('The contract_start_date is not in the correct format',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INVALID_REQUEST)
