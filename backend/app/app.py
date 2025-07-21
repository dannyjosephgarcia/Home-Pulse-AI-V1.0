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
from backend.redfin_scraper.routes import housing_market_routes
from backend.redfin_scraper.routes.housing_market_routes import housing_market_bluprint
from backend.db.routes.home_pulse_db_routes import home_pulse_db_routes_blueprint


def create_app():
    container = Container()
    flask_app = Flask(__name__)
    flask_app.container = container

    CORS(flask_app)

    flask_app.register_blueprint(housing_market_bluprint)
    flask_app.register_blueprint(home_pulse_db_routes_blueprint)
    flask_app.container.wire(modules=[housing_market_routes, home_pulse_db_routes])
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
