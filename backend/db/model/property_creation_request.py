import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_REQUEST
from common.helpers.model_helpers import validate_subfield_types


class Appliances:
    def __init__(self, appliances):
        self.stove = int(appliances['Stove'])
        self.dishwasher = int(appliances['Dishwasher'])
        self.dryer = int(appliances['Dryer'])
        self.refrigerator = int(appliances['Refrigerator'])
        self.washer = int(appliances['Washer'])


class Structures:
    def __init__(self, structures):
        self.roof = int(structures['Roof'])
        self.driveway = int(structures['Driveway'])
        self.water_heater = int(structures['Water Heater'])
        self.furnace = int(structures['Furnace'])
        self.ac_unit = int(structures['A/C Unit'])


class PropertyCreationRequest:
    def __init__(self, user_id, request):
        self._validate_property_creation_request(request)
        self.user_id = user_id
        self.postal_code = request['postalCode']
        self.home_age = request['homeAge']
        self.home_address = request['homeAddress']
        self.appliances = Appliances(request['appliances'])
        self.structures = Structures(request['structures'])

    @classmethod
    def _validate_property_creation_request(cls, request):
        """
        Validates the request to the /customers/properties route
        :param request: python dict, the request to the route
        :return:
        """
        logging.info(START_OF_METHOD)
        if 'postalCode' not in request:
            logging.error('The postalCode field is a required field')
            raise Error(INVALID_REQUEST)
        if 'homeAge' not in request:
            logging.error('The homeAge field is a required field')
            raise Error(INVALID_REQUEST)
        if 'homeAddress' not in request:
            logging.error('The homeAddress field is required field')
            raise Error
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
        appliance_fields = ['Stove', 'Dishwasher', 'Dryer', 'Refrigerator', 'Washer']
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
        structure_fields = ['Roof', 'Driveway', 'Water Heater', 'Furnace', 'A/C Unit']
        for field in structure_fields:
            if not validate_subfield_types(structures, field, int):
                logging.error('A structure age is not of the correct datatype')
                raise Error(INVALID_REQUEST)
