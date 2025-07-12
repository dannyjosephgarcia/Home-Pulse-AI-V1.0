import logging
import uuid
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from flask import jsonify, request, Blueprint
from dependency_injector.wiring import inject, Provide
from backend.app.container import Container
import mdc
from backend.security.csrf import csrf

home_pulse_db_routes_blueprint = Blueprint('home_pulse_db_routes_blueprint', __name__)


@home_pulse_db_routes_blueprint.route('/v1/fetch_houses', methods=['POST'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/fetch_houses')
@csrf.exempt
@inject
def insert_customer_into_user_table(ctx):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)