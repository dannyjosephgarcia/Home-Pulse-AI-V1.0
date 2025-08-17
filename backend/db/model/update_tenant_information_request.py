import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD
from common.logging.error.error_messages import INVALID_REQUEST


class UpdateTenantInformationRequest:
    def __init__(self, tenant_id, property_id, request):
        self._validate_update_tenant_information_request(request)
        self.tenant_id = tenant_id
        self.property_id = property_id
        self.first_name = request.get('first_name')
        self.last_name = request.get('last_name')
        self.contract_start_date = request.get('contract_start_date')
        self.contract_end_date = request.get('contract_end_date')
        self.contract_status = request.get('contract_status')
        self.recommended_replacement_date = request.get('recommended_replacement_date')
        self.monthly_rent = request.get('monthly_rent')
        self.phone_number = request.get('phone_number')

    @staticmethod
    def _validate_update_tenant_information_request(request):
        """
        Validates the data types for the update request
        :param request: The request to the PUT route for tenant information
        """
        logging.info(START_OF_METHOD)
        if 'id' in request:
            if not isinstance(request['id'], int):
                logging.error('The id field must be an integer')
                raise Error(INVALID_REQUEST)
        if 'property_id' in request:
            if not isinstance(request['property_id'], int):
                logging.error('The property_id field must be a string')
                raise Error(INVALID_REQUEST)
        if 'first_name' in request:
            if not isinstance(request['first_name'], str):
                logging.error('The first_name field must be a string')
                raise Error(INVALID_REQUEST)
        if 'last_name' in request:
            if not isinstance(request['last_name'], str):
                logging.error('The last_name field must be a string')
                raise Error(INVALID_REQUEST)
        if 'contract_start_date' in request:
            if not isinstance(request['contract_start_date'], str):
                logging.error('The contract_start_date field must be a string')
                raise Error(INVALID_REQUEST)
        if 'contract_end_date' in request:
            if not isinstance(request['contract_end_date'], str):
                logging.error('The id field must be a string')
                raise Error(INVALID_REQUEST)
        if 'contract_status' in request:
            if not isinstance(request['contract_status'], str):
                logging.error('The contract_status field must be a string')
                raise Error(INVALID_REQUEST)
        if 'recommended_replacement_date' in request:
            if not isinstance(request['recommended_replacement_date'], str):
                logging.error('The recommended_replacement_date field must be a string')
                raise Error(INVALID_REQUEST)
        if 'monthly_rent' in request:
            if not isinstance(request['monthly_rent'], float):
                logging.error('The monthly_rent field must be a string')
                raise Error(INVALID_REQUEST)
        if 'phone_number' in request:
            if not isinstance(request['phone_number'], str):
                logging.error('The phone_number field must be a string')
                raise Error(INVALID_REQUEST)