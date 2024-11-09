from .auth import auth_routes
from .user import user_routes
from .predictor import predictor_routes
from .history import history_routes
# from sanic_openapi import openapi3_blueprint



def init_routes(app):
    # app.blueprint(openapi3_blueprint)
    app.blueprint(auth_routes)
    app.blueprint(user_routes)
    app.blueprint(predictor_routes)
    app.blueprint(history_routes)
