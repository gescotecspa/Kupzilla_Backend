
from .promotions_api import promotion_api_blueprint

def init_api(app):
    app.register_blueprint(promotion_api_blueprint, url_prefix='/api')