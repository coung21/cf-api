from .auth import auth_routes
from .user import user_routes


def init_routes(app):
    app.blueprint(auth_routes)
    app.blueprint(user_routes)
