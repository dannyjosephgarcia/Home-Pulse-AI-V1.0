import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from backend.redfin_scraper.client.redfin_client import RedfinClient
from backend.redfin_scraper.model.redfin_fetch_houses_request import RedfinFetchHousesRequest


class RedfinHousingDataExtractionService:
    def __init__(self, redfin_client: RedfinClient):
        self.redfin_client = redfin_client

    def execute_redfin_housing_data_retrieval(self, data_extraction_request: RedfinFetchHousesRequest):
        """
        Retrieves the
        :param data_extraction_request:
        :return: python int, the HTTP Status code
        """
        logging.info(START_OF_METHOD)
        location_suggestions, status_code = self.redfin_client.fetch_location_suggestions(
            postal_code=data_extraction_request.postal_code)
        response = self.format_redfin_housing_data_response(
            status_code=status_code)
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def format_redfin_housing_data_response(status_code):
        """
        The status code of the request
        :param status_code: The HTTP Status Code to be returned to the front end
        :return: python int
        """
        logging.info(START_OF_METHOD)
        response = {'fetchHousingDataStatus': status_code}
        logging.info(END_OF_METHOD)
        return response
