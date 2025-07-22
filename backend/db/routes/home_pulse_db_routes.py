import mdc
import uuid
import logging
from backend.security.csrf import csrf
from backend.app.container import Container
from flask import jsonify, request, Blueprint
from dependency_injector.wiring import inject, Provide
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from backend.db.model.customer_creation_request import CustomerCreationRequest
from backend.db.model.customer_authentication_request import CustomerAuthenticationRequest

home_pulse_db_routes_blueprint = Blueprint('home_pulse_db_routes_blueprint', __name__)


@home_pulse_db_routes_blueprint.route('/v1/customers/signup', methods=['POST'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/customers')
@csrf.exempt
@inject
def authenticate_customer_for_signup(ctx,
                                     customer_creation_insertion_service=
                                     Provide[Container.customer_creation_insertion_service]):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)
    customer_creation_request = CustomerCreationRequest(request.get_json())
    response = customer_creation_insertion_service.insert_new_customer_into_user_table(customer_creation_request)
    logging.info(END_OF_METHOD)
    return jsonify(response)


@home_pulse_db_routes_blueprint.route('/v1/customers/login', methods=['POST'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/customers')
@csrf.exempt
@inject
def authenticate_customer_for_login(ctx,
                                    customer_authentication_service=
                                    Provide[Container.customer_authentication_service]):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)
    customer_authentication_request = CustomerAuthenticationRequest(request.get_json())
    response = customer_authentication_service.authenticate_user_for_login(customer_authentication_request.email,
                                                                           customer_authentication_request.password)
    logging.info(END_OF_METHOD)
    return jsonify(response)
