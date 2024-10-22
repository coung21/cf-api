from sanic import Blueprint
from sanic.response import json
from services.auth_service import register_user, login_user

auth_routes = Blueprint("auth", url_prefix="/auth")


@auth_routes.route("/register", methods=["POST"])
async def register(request):
    user_data = request.json
    result = await register_user(request.app.ctx.db, user_data)
    return json(result, status=result.get("status", 200))


@auth_routes.route("/login", methods=["POST"])
async def login(request):
    user_data = request.json
    result = await login_user(request.app.ctx.db, user_data)
    return json(result, status=result.get("status", 200))
