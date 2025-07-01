from dependency_injector.wiring import inject
from flask import Blueprint
from backend.security.csrf import csrf
from backend.common.logging.log_utils import START_OF_METHOD
import logging


housing_market_bluprint = Blueprint('housing_market_blueprint', __name__)


@housing_market_bluprint.route('/v1/fetch_houses', methods=['GET'])
@inject
@csrf.exempt
def fetch_market_houses(ctx):
    logging.info(START_OF_METHOD)
    return "Hello World"