import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_REQUEST
from common.helpers.model_helpers import validate_subfield_types


class Appliances:
    def __init__(self, appliances):
        self.stove = int(appliances['stove'])
        self.dishwasher = int(appliances['dishwasher'])
        self.dryer = int(appliances['dryer'])
        self.refrigerator = int(appliances['refrigerator'])
        self.washer = int(appliances['washer'])


class Structures:
    def __init__(self, structures):
        self.roof = int(structures['roof'])
        self.driveway = int(structures['driveway'])
        self.water_heater = int(structures['water heater'])
        self.furnace = int(structures['furnace'])
        self.ac_unit = int(structures['a/c unit'])


class PropertyCreationRequest:
    def __init__(self, user_id, request):
        self._validate_property_creation_request(request)
        self.user_id = user_id
        self.street = request['street']
        self.city = request['city']
        self.state = request['state']
        self.zip = request['zip']
        self.home_age = request['homeAge']
        self.appliances = Appliances(request['appliances'])
        self.structures = Structures(request['structures'])
        self.home_address = self.construct_property_address(self.street, self.city, self.state, self.zip)

    @classmethod
    def _validate_property_creation_request(cls, request):
        """
        Validates the request to the /customers/properties route
        :param request: python dict, the request to the route
        :return:
        """
        logging.info(START_OF_METHOD)
        if 'street' not in request:
            logging.error('The street field is a required field')
            raise Error(INVALID_REQUEST)
        if 'city' not in request:
            logging.error('The city field is a required field')
            raise Error(INVALID_REQUEST)
        if 'state' not in request:
            logging.error('The state field is a required field')
            raise Error(INVALID_REQUEST)
        if 'zip' not in request:
            logging.error('The zip field is a required field')
            raise Error(INVALID_REQUEST)
        if 'homeAge' not in request:
            logging.error('The homeAge field is a required field')
            raise Error(INVALID_REQUEST)
        if 'appliances' not in request:
            logging.error('The appliances field is a required field')
            raise Error(INVALID_REQUEST)
        if 'structures' not in request:
            logging.error('The structures field is a required field')
            raise Error(INVALID_REQUEST)
        cls._validate_appliances(request['appliances'])
        cls._validate_structures(request['structures'])

    @staticmethod
    def _validate_appliances(appliances):
        """
        Validates that the appliances being entered are valid
        :param appliances: python dict, the dictionary of appliance information
        :return:
        """
        appliance_fields = ['stove', 'dishwasher', 'dryer', 'refrigerator', 'washer']
        for field in appliance_fields:
            if not validate_subfield_types(appliances, field, int):
                logging.error('An appliance age is not of the correct datatype')
                raise Error(INVALID_REQUEST)

    @staticmethod
    def _validate_structures(structures):
        """
        Validates that the appliances being entered are valid
        :param structures: python dict, the dictionary of appliance information
        :return:
        """
        structure_fields = ['roof', 'driveway', 'water heater', 'furnace', 'a/c unit']
        for field in structure_fields:
            if not validate_subfield_types(structures, field, int):
                logging.error('A structure age is not of the correct datatype')
                raise Error(INVALID_REQUEST)

    @staticmethod
    def construct_property_address(street, city, state):
        """
        Constructs the address field for storage
        :return:
        """
        address = street + ', ' + city + ', ' + state
        return address
