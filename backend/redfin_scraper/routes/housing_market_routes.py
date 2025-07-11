import mdc
import uuid
from dependency_injector.wiring import inject, Provide
from flask import Blueprint, jsonify, request
from backend.app.container import Container
from backend.security.csrf import csrf
from backend.redfin_scraper.model.redfin_fetch_houses_request import RedfinFetchHousesRequest
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
import logging


housing_market_bluprint = Blueprint('housing_market_blueprint', __name__)


@housing_market_bluprint.route('/v1/fetch_houses', methods=['GET'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/fetch_houses')
@csrf.exempt
@inject
def fetch_market_houses(ctx, redfin_housing_data_extraction_service=
                        Provide[Container.redfin_housing_data_extraction_service]):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)
    request_json = dict(request.args)
    fetch_houses_request = RedfinFetchHousesRequest(request_json)
    # response = redfin_housing_data_extraction_service.execute_redfin_housing_data_retrieval(fetch_houses_request)
    response = {'postalCode': fetch_houses_request.postal_code}
    logging.info(END_OF_METHOD)
    return jsonify(response)
