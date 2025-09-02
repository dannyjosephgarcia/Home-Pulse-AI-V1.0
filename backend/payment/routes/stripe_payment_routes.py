import mdc
import uuid
import logging
from backend.security.csrf import csrf
from backend.app.container import Container
from flask import Blueprint, request, jsonify
from dependency_injector.wiring import Provide, inject
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from backend.payment.model.stripe_payment_request import StripePaymentRequest
from backend.payment.model.update_customer_payment_status_request import UpdateCustomerPaymentStatusRequest


stripe_payment_routes_blueprint = Blueprint('stripe_payment_routes_blueprint', __name__)


@stripe_payment_routes_blueprint.route('/v1/payment/create-checkout-session', methods=['POST'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/payment')
@csrf.exempt
@inject
def receive_customer_payment(ctx,
                             stripe_payment_session_creation_service=
                             Provide[Container.stripe_payment_session_creation_service]):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)
    request_json = request.get_json()
    stripe_payment_request = StripePaymentRequest(request_json)
    response = stripe_payment_session_creation_service.create_checkout_session_for_customer(stripe_payment_request)
    logging.info(END_OF_METHOD)
    return jsonify(response)


@stripe_payment_routes_blueprint.route('/v1/payment/update-payment-status', methods=['POST'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/payment')
@csrf.exempt
@inject
def receive_payment_completion_webhook(ctx,
                                       update_payment_status_service=
                                       Provide[Container.update_payment_status_service]):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)
    event = update_payment_status_service.perform_webhook_verification(request)
    response = update_payment_status_service.update_payment_status_from_event(event)
    logging.info(END_OF_METHOD)
    return jsonify(response)


@stripe_payment_routes_blueprint.route('/v1/payment/cancel-subscription', methods=['DELETE'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/payment')
@csrf.exempt
@inject
def delete_customer_subscription(ctx,
                                 ):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)
    logging.info(END_OF_METHOD)
    return jsonify({})
