import os
import logging.config

import mdc
from flask import Flask
from flask_cors import CORS
from waitress import serve
from backend.security.csrf import csrf
from backend.app.container import Container
from common.logging.error.error import Error
from backend.db.routes import home_pulse_db_routes
from common.logging.logging_cfg import logging_cfg
from backend.db.routes.home_pulse_db_routes import home_pulse_db_routes_blueprint
from backend.db.routes.property_routes import property_routes_blueprint
from backend.db.routes import property_routes
from backend.db.routes.profile_and_payment_routes import profile_and_payments_blueprint
from backend.db.routes import profile_and_payment_routes
from backend.payment.routes.stripe_payment_routes import stripe_payment_routes_blueprint
from backend.payment.routes import stripe_payment_routes
from backend.data_harvesting.routes.appliance_information_routes import appliance_information_routes_blueprint
from backend.data_harvesting.routes import appliance_information_routes
from backend.home_bot_model.routes.home_bot_routes import home_bot_routes_blueprint
from backend.home_bot_model.routes import home_bot_routes


def create_app():
    container = Container()
    flask_app = Flask(__name__)
    flask_app.container = container


    flask_app.register_blueprint(home_pulse_db_routes_blueprint)
    flask_app.register_blueprint(property_routes_blueprint)
    flask_app.register_blueprint(profile_and_payments_blueprint)
    flask_app.register_blueprint(stripe_payment_routes_blueprint)
    flask_app.register_blueprint(appliance_information_routes_blueprint)
    flask_app.register_blueprint(home_bot_routes_blueprint)
    flask_app.container.wire(modules=[home_pulse_db_routes,
                                      property_routes,
                                      profile_and_payment_routes,
                                      stripe_payment_routes,
                                      appliance_information_routes,
                                      home_bot_routes])
    CORS(flask_app)
    csrf.init_app(flask_app)

    logging.config.dictConfig(logging_cfg.cfg)
    return flask_app


app = create_app()
port = int(os.getenv('PORT'))


@app.errorhandler(Error)
@mdc.with_mdc(domain='home-pulse-ai', subdomain='/api/error-handler')
def handle_error(error, ctx):
    ctx.correlationId = error.correlation_id
    logging.error(error.message, extra={'http_status': error.status})
    return error.as_response()


@app.route('/api/healthcheck', methods=['GET'])
@csrf.exempt
def healthcheck():
    return {"status": "UP"}, 200


if __name__ == "__main__":
    env = os.getenv('ENV')
    app.logger.info("Starting Home Pulse app with Waitress...")
    if env == 'prod':
        app.run(host='0.0.0.0', port=port)
    else:
        serve(app, host='0.0.0.0', port=port)
