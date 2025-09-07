import mdc
import uuid
import logging
from backend.security.csrf import csrf
from backend.app.container import Container
from flask import jsonify, request, Blueprint
from dependency_injector.wiring import inject, Provide
from common.decorators.token_required import token_required
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from backend.db.model.update_tenant_information_request import UpdateTenantInformationRequest
from backend.db.model.tenant_creation_request import TenantCreationRequest
from backend.db.model.property_image_insertion_request import PropertyImageInsertionRequest
from backend.db.model.update_forecasted_date_request import UpdateForecastedDateRequest

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


@property_routes_blueprint.route('/v1/properties/<property_id>/appliances/forecasted-date', methods=['PUT'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def update_forecasted_replacement_date_from_model(ctx,
                                                  property_id,
                                                  forecasted_replacement_date_update_service=
                                                  Provide[Container.forecasted_replacement_date_update_service]):
    logging.info(START_OF_METHOD)
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    update_forecasted_date_request = UpdateForecastedDateRequest(int(property_id), request.get_json())
    response = forecasted_replacement_date_update_service.update_forecasted_replacement_date(
        update_forecasted_date_request.property_id, update_forecasted_date_request.appliance_type,
        update_forecasted_date_request.forecasted_replacement_date)
    logging.info(END_OF_METHOD)
    return jsonify(response)


@property_routes_blueprint.route('/v1/properties/<property_id>/tenants/<tenant_id>', methods=['PUT'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def update_tenant_information_for_dashboard(ctx,
                                            property_id,
                                            tenant_id,
                                            tenant_information_update_service=
                                            Provide[Container.tenant_information_update_service]):
    logging.info(START_OF_METHOD)
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    update_tenant_information_request = UpdateTenantInformationRequest(tenant_id, property_id, request.get_json())
    response = tenant_information_update_service.update_tenant_information(update_tenant_information_request)
    logging.info(END_OF_METHOD)
    return jsonify(response)


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


@property_routes_blueprint.route('/v1/properties/<property_id>/tenants', methods=['POST'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def insert_tenant_information_into_tenant_table(ctx,
                                                property_id,
                                                tenant_information_insertion_service=
                                                Provide[Container.tenant_information_insertion_service]):
    logging.info(START_OF_METHOD)
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    tenant_creation_request = TenantCreationRequest(property_id, request.get_json())
    response = tenant_information_insertion_service.insert_tenant_information(tenant_creation_request)
    logging.info(END_OF_METHOD)
    return jsonify(response)


@property_routes_blueprint.route('/v1/properties/<property_id>/customers/<customer_id>/image', methods=['GET'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def fetch_property_image_url(ctx,
                             property_id,
                             customer_id,
                             property_image_retrieval_service=
                             Provide[Container.property_image_retrieval_service]):
    logging.info(START_OF_METHOD)
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    response = property_image_retrieval_service.fetch_and_sign_property_image_url(customer_id, property_id)
    logging.info(END_OF_METHOD)
    return jsonify(response)


@property_routes_blueprint.route('/v1/properties/<property_id>/customers/<customer_id>/image', methods=['POST'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/properties')
@csrf.exempt
@token_required
@inject
def insert_property_image_and_(ctx,
                               property_id,
                               customer_id,
                               property_image_insertion_service=
                               Provide[Container.property_image_insertion_service]):
    logging.info(START_OF_METHOD)
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    property_image_request = PropertyImageInsertionRequest(request.get_json())
    response = property_image_insertion_service.insert_and_sign_property_image_url(customer_id,
                                                                                   property_id,
                                                                                   property_image_request.file_name)
    logging.info(END_OF_METHOD)
    return jsonify(response)
