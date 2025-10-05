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
        self.stove_brand = self._validate_and_get_optional_string(appliances, 'stoveBrand', 'stove brand')
        self.stove_model = self._validate_and_get_optional_string(appliances, 'stoveModel', 'stove model')
        self.dishwasher_brand = self._validate_and_get_optional_string(appliances, 'dishwasherBrand', 'dishwasher brand')
        self.dishwasher_model = self._validate_and_get_optional_string(appliances, 'dishwasherModel', 'dishwasher model')
        self.dryer_brand = self._validate_and_get_optional_string(appliances, 'dryerBrand', 'dryer brand')
        self.dryer_model = self._validate_and_get_optional_string(appliances, 'dryerModel', 'dryer model')
        self.refrigerator_brand = self._validate_and_get_optional_string(appliances, 'refrigeratorBrand', 'refrigerator brand')
        self.refrigerator_model = self._validate_and_get_optional_string(appliances, 'refrigeratorModel', 'refrigerator model')
        self.washer_brand = self._validate_and_get_optional_string(appliances, 'washerBrand', 'washer brand')
        self.washer_model = self._validate_and_get_optional_string(appliances, 'washerModel', 'washer model')

    @staticmethod
    def _validate_and_get_optional_string(data, field_name, field_display_name, max_length=100):
        """
        Validates optional string fields for appliance brand and model
        :param data: python dict, the appliances data
        :param field_name: str, the field name to extract
        :param field_display_name: str, the human-readable field name for error messages
        :param max_length: int, maximum allowed length for the string (default 100)
        :return: str or None, the validated value or None if not provided
        """
        value = data.get(field_name)

        # If not provided, return None (field is optional)
        if value is None:
            return None

        # If provided, must be a string
        if not isinstance(value, str):
            logging.error(f'The {field_display_name} field must be a string')
            raise Error(INVALID_REQUEST)

        # If provided, must not be empty or whitespace-only
        if not value.strip():
            logging.error(f'The {field_display_name} field cannot be empty or whitespace-only')
            raise Error(INVALID_REQUEST)

        # If provided, must not exceed maximum length
        if len(value) > max_length:
            logging.error(f'The {field_display_name} field cannot exceed {max_length} characters')
            raise Error(INVALID_REQUEST)

        return value


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
        self.home_address = self.construct_property_address(self.street, self.city, self.state)

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
