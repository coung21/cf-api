from .predictor import predictor_routes


def init_routes(app):
    app.blueprint(predictor_routes)
