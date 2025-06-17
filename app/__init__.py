from flask import Flask
from app.extensions import db, ma, limiter, cache
from app.models import Customer, Mechanic, ServiceTicket, ServiceMechanic
from app.blueprints.user import user_bp
from app.blueprints.mechanic import mechanic_bp
from app.blueprints.service_ticket import service_ticket_bp
from app.blueprints.inventory import inventory_bp
from flask_swagger_ui import get_swaggerui_blueprint
import config

SWAGGER_URL = '/api/docs' #Sets endpoint for documentation
API_URL = '/static/swagger.yaml' #Grabs host url from swagger file

swagger_bp = get_swaggerui_blueprint(
    SWAGGER_URL, 
    API_URL, 
    config={
        'app_name': "Mechanic Shop API"
    }
)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    app.register_blueprint(user_bp, url_prefix='/customers')
    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)

    with app.app_context():
        db.create_all()

    return app
