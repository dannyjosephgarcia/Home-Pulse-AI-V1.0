import mdc
import uuid
import logging
from backend.security.csrf import csrf
from backend.app.container import Container
from flask import jsonify, request, Blueprint
from dependency_injector.wiring import inject, Provide
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD


appliance_information_routes_blueprint = Blueprint('appliance_information_routes_blueprint', __name__)


@appliance_information_routes_blueprint.route('/v1/appliances/update-prices', methods=['PUT'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/appliances')
@csrf.exempt
@inject
def insert_property_information_into_table(ctx,
                                           lowes_appliance_price_analysis_service=
                                           Provide[Container.lowes_appliance_price_analysis_service]):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)
    put_record_status = lowes_appliance_price_analysis_service.update_appliance_information_prices()
    response = {
        'putRecordStatus': put_record_status
    }
    return jsonify(response)
