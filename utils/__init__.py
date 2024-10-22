import jwt
from functools import wraps
from sanic.response import json
from config import SECRET_KEY
import datetime


def generate_jwt_token(user):
    payload = {
        "user_id": str(user['_id']),
        "username": user['username'],
        "phone": user['phone'],
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}

# JWT-protected decorator


def protected(f):
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return json({"error": "Token missing"}, status=401)

        token = auth_header.split(" ")[1]
        decoded = decode_jwt_token(token)
        if "error" in decoded:
            return json(decoded, status=401)

        return await f(request, *args, **kwargs)

    return decorated_function
