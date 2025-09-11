import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD
from common.logging.error.error_messages import INVALID_REQUEST


class UpdateStructureInformationRequest:
    def __init__(self, property_id, request):
        self.validate_update_structure_information_request(property_id, request)
        self.property_id = property_id
        self.structure_updates = request['structureUpdates']

    @staticmethod
    def validate_update_structure_information_request(property_id, request):
        """
        Validates the request to the put route to update property structures
        :param property_id: The internal id of a property in our system
        :param request: The request to the PUT route
        """
        logging.info(START_OF_METHOD)
        if 'structureUpdates' not in request:
            logging.error('The structureUpdates field is a required field')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['structureUpdates'], list):
            logging.error('The structureUpdates field must be an array')
            logging.error(INVALID_REQUEST)
        try:
            int(property_id)
        except Exception as e:
            logging.error('The property_id query parameter must be able to be converted to an int',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INVALID_REQUEST)
