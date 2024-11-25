from sanic import Blueprint
from sanic.response import json
from services.history_service import get_histories_by_user_id, get_history_by_id, get_histories_map
from utils.jwt_utils import protected
from sanic_ext import openapi
from datetime import datetime

history_routes = Blueprint("histories", url_prefix="/histories")

@history_routes.route("/<user_id>", methods=["GET"])
@openapi.summary("Get histories by user id")
@openapi.tag("History")
@openapi.parameter("user_id", str, "User id")
@openapi.response(200, {
    "application/json": {
        "id": str,
        "image_url": str,
        "result": int,
        "confidence": float,
        "created_at": datetime
    }
})
# @protected
async def get_histories(request, user_id):
    histories = await get_histories_by_user_id(request.app.ctx.db, user_id)
    return json(histories)


@history_routes.route("/<history_id>/detail", methods=["GET"])
@openapi.summary("Get history by id")
@openapi.tag("History")
@openapi.parameter("history_id", str, "History id")
@openapi.response(200, {
    "application/json": {
        "id": str,
        "image_url": str,
        "result": {
            "idx": int,
            "name": str,
            "disease": str,
            "cause": str,
            "solution": str
            },
        "confidence": float,
        "created_at": datetime
    }
})
# @protected
async def get_history(request, history_id):
    history = await get_history_by_id(request.app.ctx.db, history_id)
    if history:
        return json(history)
    else:
        return json({"error": "History not found"}, status=404)
    
    

@history_routes.route("/map", methods=["GET"])
@openapi.summary("Get histories map")
@openapi.tag("History")
@openapi.response(200, {
    "application/json": {
        "id": str,
        "result": int,
        "croods": {
            "lat": float,
            "long": float
        },
        "created_at": datetime
    }
})
async def histories_map(request):
    histories = await get_histories_map(request.app.ctx.db)
    return json(histories)