import mdc
from dependency_injector.wiring import inject
from flask import Blueprint, jsonify, request
from security.csrf import csrf
from backend.redfin_scraper.model.redfin_fetch_houses_request import RedfinFetchHousesRequest
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
import logging


housing_market_bluprint = Blueprint('housing_market_blueprint', __name__)


@housing_market_bluprint.route('/v1/fetch_houses', methods=['GET'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/fetch_houses')
@inject
@csrf.exempt
def fetch_market_houses(ctx):
    ctx.correlationId = request.headers.get('correlation-id', '1234')
    logging.info(START_OF_METHOD)
    fetch_houses_request = RedfinFetchHousesRequest(dict(request.args))
    response = {'postalCode': fetch_houses_request.postal_code}
    logging.info(END_OF_METHOD)
    return jsonify(response)
