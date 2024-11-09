from sanic import Blueprint
from sanic.response import json
from services.history_service import get_histories_by_user_id, get_history_by_id
from utils.jwt_utils import protected

history_routes = Blueprint("histories", url_prefix="/histories")

@history_routes.route("/<user_id>", methods=["GET"])
@protected
async def get_histories(request, user_id):
    print("user_id", user_id)
    histories = await get_histories_by_user_id(request.app.ctx.db, user_id)
    return json(histories)

@history_routes.route("/<history_id>/detail", methods=["GET"])
@protected
async def get_history(request, history_id):
    history = await get_history_by_id(request.app.ctx.db, history_id)
    if history:
        return json(history)
    else:
        return json({"error": "History not found"}, status=404)