import logging
from common.logging.log_utils import START_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_REQUEST
import datetime


class UpdateForecastedDateRequest:
    def __init__(self, property_id, request):
        self.validate_update_forecasted_replacement_date_request(property_id, request)
        self.property_id = property_id
        self.appliance_type = request['applianceType']
        self.forecasted_replacement_date = datetime.datetime.strptime(request['forecastedReplacementDate'], '%Y-%m-%d')

    @staticmethod
    def validate_update_forecasted_replacement_date_request(property_id, request):
        """
        Validates the PUT request to update the forecasted replacement date of the model
        :param property_id: The internal id of a property in our system
        :param request: The request to the route
        :return:
        """
        logging.info(START_OF_METHOD)
        if 'applianceType' not in request:
            logging.error('The applianceType field is a required field')
            raise Error(INVALID_REQUEST)
        if 'forecastedReplacementDate' not in request:
            logging.error('The forecastedReplacementDate field is a required field')
            raise Error(INVALID_REQUEST)
        if not isinstance(property_id, int):
            logging.error('The property_id must be an integer')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['applianceType'], str):
            logging.error('The applianceType field is a required field')
            raise Error(INVALID_REQUEST)
        try:
            datetime.datetime.strptime(request['forecastedReplacementDate'], '%Y-%m-%d')
        except Exception as e:
            logging.error('The replacement date is not in the correct YYYY-mm-dd format')
            raise Error(INVALID_REQUEST)

