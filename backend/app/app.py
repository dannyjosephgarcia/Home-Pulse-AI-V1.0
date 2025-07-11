import os
import logging.config
from flask import Flask
from flask_cors import CORS
from waitress import serve
from backend.security.csrf import csrf
from backend.app.container import Container
from common.logging.logging_cfg import logging_cfg
from backend.redfin_scraper.routes import housing_market_routes
from backend.redfin_scraper.routes.housing_market_routes import housing_market_bluprint


def create_app():
    container = Container()
    flask_app = Flask(__name__)
    flask_app.container = container

    CORS(flask_app)

    flask_app.register_blueprint(housing_market_bluprint)
    flask_app.container.wire(modules=[housing_market_routes])
    csrf.init_app(flask_app)

    logging.config.dictConfig(logging_cfg.cfg)
    return flask_app


app = create_app()


@app.route('/api/healthcheck', methods=['GET'])
@csrf.exempt
def healthcheck():
    return {"status": "UP"}, 200


if __name__ == "__main__":
    env = os.getenv('ENV')
    app.logger.info("Starting Home Pulse app with Waitress...")
    if env == 'prod':
        app.run(host='0.0.0.0', port=5000)
    else:
        serve(app, host='0.0.0.0', port=5000)
