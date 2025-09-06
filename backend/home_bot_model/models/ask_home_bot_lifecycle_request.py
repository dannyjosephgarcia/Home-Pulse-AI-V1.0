import logging
from common.logging.log_utils import START_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INVALID_REQUEST


class AskHomeBotLifeCycleRequest:
    def __init__(self, request):
        self.validate_home_bot_lifecycle_request(request)
        self.question = request['question']
        self.appliance_age = request['applianceAge']

    @staticmethod
    def validate_home_bot_lifecycle_request(request):
        """
        Validates the question sent to the /ask-lifecycle endpoint
        :param request: The request to the route
        """
        logging.info(START_OF_METHOD)
        if 'question' not in request:
            logging.error('The question field is a required field')
            raise Error(INVALID_REQUEST)
        if 'applianceAge' not in request:
            logging.error('The applianceAge field is a required field')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['question'], str):
            logging.error('The question field must be a string')
            raise Error(INVALID_REQUEST)
        if not isinstance(request['applianceAge'], int):
            raise Error(INVALID_REQUEST)
