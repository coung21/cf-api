from sanic import Blueprint
from sanic.response import json
from sanic_ext import openapi
from services.auth_service import register_user, login_user

auth_routes = Blueprint("auth", url_prefix="/auth")


@auth_routes.route("/register", methods=["POST"])
@openapi.summary("Register a new user")
@openapi.tag("Auth")
@openapi.body(
    {
        "application/json": {
            "phone": str,
            "password": str,
            "username": str,
        }
    },
 description="Register a new user with phone, password, and username"   
)
@openapi.response(
    200,
   {"application/json": {
       "message": str, 
        "user_id": str
   }}
)
async def register(request):
    user_data = request.json
    result = await register_user(request.app.ctx.db, user_data)
    return json(result, status=result.get("status", 200))


@auth_routes.route("/login", methods=["POST"])
@openapi.summary("Login a user")
@openapi.tag("Auth")
@openapi.body(
    {
        "application/json": {
            "phone": str,
            "password": str,
        }
    },
 description="Login a user with phone and password"   
)
@openapi.response(
    200,
   {"application/json": {
       "message": str, 
        "token": str
   }}
)
async def login(request):
    user_data = request.json
    result = await login_user(request.app.ctx.db, user_data)
    return json(result, status=result.get("status", 200))
