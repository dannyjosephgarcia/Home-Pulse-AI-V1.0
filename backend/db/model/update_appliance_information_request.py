import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD
from common.logging.error.error_messages import INVALID_REQUEST


class UpdateApplianceInformationRequest:
    def __init__(self, property_id, request):
        self.validate_update_appliance_information_request(property_id, request)
        self.property_id = property_id
        self.appliance_updates = request['applianceUpdates']

    @staticmethod
    def validate_update_appliance_information_request(property_id, request):
        """
        Validates the request to the PUT route to update a property appliance
        :param property_id: The id of a propert in our system
        :param request: The request to the PUT route
        """
        logging.info(START_OF_METHOD)
        if 'applianceUpdates' not in request:
            logging.error('The applianceUpdates field is a required field')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['applianceUpdates'], list):
            logging.error('The applianceUpdates field must be an array')
            logging.error(INVALID_REQUEST)
        try:
            int(property_id)
        except Exception as e:
            logging.error('The property_id query parameter must be able to be converted to an int',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INVALID_REQUEST)
