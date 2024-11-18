from sanic import Blueprint
from sanic.response import json
from services.user_service import get_all_users, get_user_by_id
from utils.jwt_utils import protected
from sanic_ext import openapi
from datetime import datetime

user_routes = Blueprint("users", url_prefix="/users")


@user_routes.route("/", methods=["GET"])
@openapi.summary("Get all users")
@openapi.tag("User")
@openapi.response(
    200,
    {"application/json": {
        "users": [{
            "id": str,
            "username": str,
            "phone": str,
            "created_at": datetime
        }]
    }}
)
# @protected
async def get_users(request):
    users = await get_all_users(request.app.ctx.db)
    return json({"users": users})



@user_routes.route("/<user_id>", methods=["GET"])
@openapi.summary("Get a user by ID")
@openapi.tag("User")
@openapi.response(
    200,
    {"application/json": {
        "id": str,
        "username": str,
        "phone": str,
        "created_at": datetime
    }}
)
# @protected
async def get_user(request, user_id):
    user = await get_user_by_id(request.app.ctx.db, user_id)
    if user:
        return json(user)
    else:
        return json({"error": "User not found"}, status=404)
