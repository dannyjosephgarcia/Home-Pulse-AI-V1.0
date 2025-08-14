import mdc
import uuid
import logging
from backend.security.csrf import csrf
from backend.app.container import Container
from flask import jsonify, request, Blueprint
from dependency_injector.wiring import inject, Provide
from common.decorators.token_required import token_required
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD


property_routes_blueprint = Blueprint('property_routes_blueprint', __name__)


@property_routes_blueprint.route('/v1/properties', methods=['POST'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def insert_property_information_into_table(ctx,
                                           property_creation_insertion_service=
                                           Provide[Container.property_creation_insertion_service]):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)
    user_id = request.user_id
    request_json = request.get_json()
    property_creation_requests = property_creation_insertion_service.construct_property_creation_requests(user_id,
                                                                                                          request_json)
    response = property_creation_insertion_service.insert_properties_into_db(user_id, property_creation_requests)
    return jsonify(response)


@property_routes_blueprint.route('/v1/properties', methods=['GET'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def fetch_property_information_for_property_details(ctx,
                                                    property_retrieval_service=
                                                    Provide[Container.property_retrieval_service]):
    logging.info(START_OF_METHOD)
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    user_id = request.user_id
    response = property_retrieval_service.fetch_property_information(user_id=user_id, retrieval_type='ALL')
    logging.info(END_OF_METHOD)
    return jsonify(response)


@property_routes_blueprint.route('/v1/properties/<property_id>', methods=['GET'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def fetch_single_property_for_property_details(ctx,
                                               property_id,
                                               property_retrieval_service=
                                               Provide[Container.property_retrieval_service]):
    logging.info(START_OF_METHOD)
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    response = property_retrieval_service.fetch_property_information(property_id=property_id, retrieval_type='SINGLE')
    logging.info(END_OF_METHOD)
    return jsonify(response)


@property_routes_blueprint.route('/v1/properties/<property_id>/appliances', methods=['GET'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def fetch_appliance_information_for_property_details(ctx,
                                                     property_id,
                                                     property_retrieval_service=
                                                     Provide[Container.property_retrieval_service]):
    logging.info(START_OF_METHOD)
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    response = property_retrieval_service.fetch_property_information(property_id=property_id,
                                                                     retrieval_type='APPLIANCES')
    logging.info(END_OF_METHOD)
    return jsonify(response)


@property_routes_blueprint.route('/v1/properties/<property_id>/structures', methods=['GET'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def fetch_structures_information_for_property_details(ctx,
                                                      property_id,
                                                      property_retrieval_service=
                                                      Provide[Container.property_retrieval_service]):
    logging.info(START_OF_METHOD)
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    response = property_retrieval_service.fetch_property_information(property_id=property_id,
                                                                     retrieval_type='STRUCTURES')
    logging.info(END_OF_METHOD)
    return jsonify(response)


@property_routes_blueprint.route('/v1/properties/<property_id>/tenants', methods=['GET'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def fetch_tenant_information_for_dashboard(ctx,
                                           property_id,
                                           tenant_information_retrieval_service=
                                           Provide[Container.tenant_information_retrieval_service]):
    logging.info(START_OF_METHOD)
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    response = tenant_information_retrieval_service.fetch_tenant_information(property_id=property_id)
    logging.info(END_OF_METHOD)
    return jsonify(response)

# Need to add a PUT route as well


@property_routes_blueprint.route('/v1/properties/<user_id>/addresses', methods=['GET'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def fetch_address_information_for_properties(ctx,
                                             user_id,
                                             property_retrieval_service=Provide[Container.property_retrieval_service]):
    logging.info(START_OF_METHOD)
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    response = property_retrieval_service.fetch_property_information(user_id=user_id,
                                                                     retrieval_type='ADDRESSES')
    logging.info(END_OF_METHOD)
    return jsonify(response)
