import mdc
import uuid
import logging
from backend.security.csrf import csrf
from backend.app.container import Container
from flask import Blueprint, jsonify, request
from dependency_injector.wiring import inject, Provide
from common.decorators.token_required import token_required
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from backend.home_bot_model.models.ask_home_bot_lifecycle_request import AskHomeBotLifeCycleRequest

home_bot_routes_blueprint = Blueprint('home_bot_routes_blueprint', __name__)


@home_bot_routes_blueprint.route('/v1/home-bot/ask-lifecycle-question', methods=['POST'])
@mdc.with_mdc(domain='home-pulse', subdomain='/v1/home-bot')
@csrf.exempt
@token_required
@inject
def ask_home_bot_appliance_lifecycle_query(ctx,
                                           home_bot_ai_service=
                                           Provide[Container.home_bot_ai_service]):
    ctx.correlationId = request.headers.get('correlation-id', uuid.uuid4().__str__())
    logging.info(START_OF_METHOD)
    ask_home_bot_request = AskHomeBotLifeCycleRequest(request.get_json())
    answer = home_bot_ai_service.generate_lifecycle_query_answer(ask_home_bot_request)
    response = {'answer': answer}
    logging.info(END_OF_METHOD)
    return jsonify(response)
