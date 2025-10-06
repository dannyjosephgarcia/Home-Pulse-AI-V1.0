import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_REQUEST
from common.helpers.model_helpers import validate_subfield_types


class Appliances:
    def __init__(self, appliances):
        # Parse nested structure from frontend: {"stove": {"age": 5, "brand": "LG", "model": "XYZ"}}
        # Also support legacy flat format for backwards compatibility: {"stove": 5}
        self.stove = self._parse_appliance_age(appliances, 'stove')
        self.dishwasher = self._parse_appliance_age(appliances, 'dishwasher')
        self.dryer = self._parse_appliance_age(appliances, 'dryer')
        self.refrigerator = self._parse_appliance_age(appliances, 'refrigerator')
        self.washer = self._parse_appliance_age(appliances, 'washer')
        self.ac_unit = self._parse_appliance_age(appliances, 'a/c unit')

        # Extract brand and model from nested objects
        self.stove_brand = self._parse_appliance_brand(appliances, 'stove')
        self.stove_model = self._parse_appliance_model(appliances, 'stove')
        self.dishwasher_brand = self._parse_appliance_brand(appliances, 'dishwasher')
        self.dishwasher_model = self._parse_appliance_model(appliances, 'dishwasher')
        self.dryer_brand = self._parse_appliance_brand(appliances, 'dryer')
        self.dryer_model = self._parse_appliance_model(appliances, 'dryer')
        self.refrigerator_brand = self._parse_appliance_brand(appliances, 'refrigerator')
        self.refrigerator_model = self._parse_appliance_model(appliances, 'refrigerator')
        self.washer_brand = self._parse_appliance_brand(appliances, 'washer')
        self.washer_model = self._parse_appliance_model(appliances, 'washer')
        self.ac_unit_brand = self._parse_appliance_brand(appliances, 'a/c unit')
        self.ac_unit_model = self._parse_appliance_model(appliances, 'a/c unit')

    @staticmethod
    def _parse_appliance_age(appliances, appliance_name):
        """
        Parses appliance age from nested or flat format
        :param appliances: python dict, the appliances data
        :param appliance_name: str, the appliance name
        :return: int or None, the age value or None if not provided
        """
        if appliance_name not in appliances:
            return None

        value = appliances[appliance_name]

        # Handle nested format: {"age": 5, "brand": "LG"}
        if isinstance(value, dict):
            age = value.get('age')
            if age is None:
                return None
            if not isinstance(age, int):
                logging.error(f'The age for {appliance_name} must be an integer')
                raise Error(INVALID_REQUEST)
            return age

        # Handle flat format (legacy): 5
        if isinstance(value, int):
            return value

        logging.error(f'Invalid format for {appliance_name}. Expected int or dict with age field')
        raise Error(INVALID_REQUEST)

    @staticmethod
    def _parse_appliance_brand(appliances, appliance_name):
        """
        Extracts brand from nested appliance object
        :param appliances: python dict, the appliances data
        :param appliance_name: str, the appliance name
        :return: str or None, the brand value or None if not provided
        """
        if appliance_name not in appliances:
            return None

        value = appliances[appliance_name]

        # Only nested format contains brand
        if isinstance(value, dict):
            brand = value.get('brand')
            if brand is not None:
                return Appliances._validate_and_get_optional_string(
                    value, 'brand', f'{appliance_name} brand'
                )

        return None

    @staticmethod
    def _parse_appliance_model(appliances, appliance_name):
        """
        Extracts model from nested appliance object
        :param appliances: python dict, the appliances data
        :param appliance_name: str, the appliance name
        :return: str or None, the model value or None if not provided
        """
        if appliance_name not in appliances:
            return None

        value = appliances[appliance_name]

        # Only nested format contains model
        if isinstance(value, dict):
            model = value.get('model')
            if model is not None:
                return Appliances._validate_and_get_optional_string(
                    value, 'model', f'{appliance_name} model'
                )

        return None

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
        # Parse structure ages - all are optional now
        self.roof = self._parse_structure_age(structures, 'roof')
        self.driveway = self._parse_structure_age(structures, 'driveway')
        self.water_heater = self._parse_structure_age(structures, 'water heater')
        self.furnace = self._parse_structure_age(structures, 'furnace')

    @staticmethod
    def _parse_structure_age(structures, structure_name):
        """
        Parses structure age from structures dict
        :param structures: python dict, the structures data
        :param structure_name: str, the structure name
        :return: int or None, the age value or None if not provided
        """
        if structure_name not in structures:
            return None

        value = structures[structure_name]

        if not isinstance(value, int):
            logging.error(f'The age for {structure_name} must be an integer')
            raise Error(INVALID_REQUEST)

        return value


class PropertyCreationRequest:
    def __init__(self, user_id, request):
        self._validate_property_creation_request(request)
        self.user_id = user_id
        self.street = request['street']
        self.city = request['city']
        self.state = request['state']
        self.zip = request['zip']
        self.home_age = request['homeAge']
        # Appliances and structures are now optional - default to empty dict
        self.appliances = Appliances(request.get('appliances', {}))
        self.structures = Structures(request.get('structures', {}))
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

        # Appliances and structures are now optional - default to empty dict if not provided
        appliances = request.get('appliances', {})
        structures = request.get('structures', {})

        cls._validate_appliances(appliances)
        cls._validate_structures(structures)

    @staticmethod
    def _validate_appliances(appliances):
        """
        Validates that the appliances being entered are valid
        Appliances are now optional - only validates appliances that are present
        Supports both nested format {"stove": {"age": 5, "brand": "LG"}} and flat format {"stove": 5}
        :param appliances: python dict, the dictionary of appliance information
        :return:
        """
        if not isinstance(appliances, dict):
            logging.error('The appliances field must be a dictionary')
            raise Error(INVALID_REQUEST)

        # All appliances are now optional - only validate what's provided
        valid_appliances = ['stove', 'dishwasher', 'dryer', 'refrigerator', 'washer', 'a/c unit']

        for appliance_name, value in appliances.items():
            # Validate appliance name is recognized
            if appliance_name not in valid_appliances:
                logging.error(f'Unknown appliance type: {appliance_name}')
                raise Error(INVALID_REQUEST)

            # Validate value format
            if isinstance(value, dict):
                # Nested format: {"age": 5, "brand": "LG", "model": "XYZ"}
                if 'age' not in value:
                    logging.error(f'Missing age field for {appliance_name}')
                    raise Error(INVALID_REQUEST)
                if not isinstance(value['age'], int):
                    logging.error(f'Age for {appliance_name} must be an integer')
                    raise Error(INVALID_REQUEST)
                # Brand and model are optional, validated in _parse_appliance_brand/model if present
            elif isinstance(value, int):
                # Flat format (legacy): just an integer age
                pass
            else:
                logging.error(f'Invalid format for {appliance_name}. Expected int or dict with age field')
                raise Error(INVALID_REQUEST)

    @staticmethod
    def _validate_structures(structures):
        """
        Validates that the structures being entered are valid
        Structures are now optional - only validates structures that are present
        A/C Unit has been moved to appliances
        :param structures: python dict, the dictionary of structure information
        :return:
        """
        if not isinstance(structures, dict):
            logging.error('The structures field must be a dictionary')
            raise Error(INVALID_REQUEST)

        # All structures are now optional - only validate what's provided
        # A/C Unit is no longer a structure (moved to appliances)
        valid_structures = ['roof', 'driveway', 'water heater', 'furnace']

        for structure_name, value in structures.items():
            # Validate structure name is recognized
            if structure_name not in valid_structures:
                logging.error(f'Unknown structure type: {structure_name}')
                raise Error(INVALID_REQUEST)

            # Validate value is an integer
            if not isinstance(value, int):
                logging.error(f'Age for {structure_name} must be an integer')
                raise Error(INVALID_REQUEST)

    @staticmethod
    def construct_property_address(street, city, state):
        """
        Constructs the address field for storage
        :return:
        """
        address = street + ', ' + city + ', ' + state
        return address
