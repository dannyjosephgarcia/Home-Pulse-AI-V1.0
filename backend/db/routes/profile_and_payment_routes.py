import mdc
import uuid
import logging
from backend.security.csrf import csrf
from backend.app.container import Container
from flask import jsonify, request, Blueprint
from dependency_injector.wiring import inject, Provide
from common.decorators.token_required import token_required
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from backend.db.model.customer_profile_update_request import CustomerProfileUpdateRequest


profile_and_payments_blueprint = Blueprint('profile_and_payments_blueprint', __name__)


@profile_and_payments_blueprint.route('/v1/customers/profile', methods=['PUT'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/customers')
@csrf.exempt
@token_required
@inject
def insert_property_information_into_table(ctx,
                                           customer_profile_update_service=
                                           Provide[Container.customer_profile_update_service]):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)
    user_id = request.user_id
    customer_profile_update_request = CustomerProfileUpdateRequest(request.get_json())
    refreshed_token = customer_profile_update_service.update_user_first_and_last_name(
        user_id, customer_profile_update_request.first_name, customer_profile_update_request.last_name)
    return jsonify(refreshed_token)


@profile_and_payments_blueprint.route('/v1/customers/<user_id>/retrieve-subscription-information', methods=['GET'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/customers')
@csrf.exempt
@token_required
@inject
def fetch_subscription_information_for_customer(ctx,
                                                user_id,
                                                customer_subscription_retrieval_service=
                                                Provide[Container.customer_subscription_retrieval_service]):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)
    response = customer_subscription_retrieval_service.fetch_subscription_information_for_customer(user_id)
    return jsonify(response)
