from .predictor import predictor_router


def init_routes(app):
    app.blueprint(predictor_router)
