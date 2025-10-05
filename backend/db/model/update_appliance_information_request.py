import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD
from common.logging.error.error_messages import INVALID_REQUEST


class UpdateApplianceInformationRequest:
    def __init__(self, property_id, request):
        self.validate_update_appliance_information_request(property_id, request)
        self.property_id = property_id
        self.appliance_updates = request['applianceUpdates']

    @classmethod
    def validate_update_appliance_information_request(cls, property_id, request):
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
            raise Error(INVALID_REQUEST)
        try:
            int(property_id)
        except Exception as e:
            logging.error('The property_id query parameter must be able to be converted to an int',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INVALID_REQUEST)

        for appliance_update in request['applianceUpdates']:
            cls._validate_appliance_update(appliance_update)

    @staticmethod
    def _validate_appliance_update(appliance_update):
        """
        Validates individual appliance update objects
        :param appliance_update: python dict, a single appliance update object
        """
        if 'applianceBrand' in appliance_update:
            brand = appliance_update['applianceBrand']
            if brand is not None:
                if not isinstance(brand, str):
                    logging.error('The applianceBrand field must be a string')
                    raise Error(INVALID_REQUEST)
                if not brand.strip():
                    logging.error('The applianceBrand field cannot be empty or whitespace-only')
                    raise Error(INVALID_REQUEST)
                if len(brand) > 100:
                    logging.error('The applianceBrand field cannot exceed 100 characters')
                    raise Error(INVALID_REQUEST)

        if 'applianceModel' in appliance_update:
            model = appliance_update['applianceModel']
            if model is not None:
                if not isinstance(model, str):
                    logging.error('The applianceModel field must be a string')
                    raise Error(INVALID_REQUEST)
                if not model.strip():
                    logging.error('The applianceModel field cannot be empty or whitespace-only')
                    raise Error(INVALID_REQUEST)
                if len(model) > 100:
                    logging.error('The applianceModel field cannot exceed 100 characters')
                    raise Error(INVALID_REQUEST)
