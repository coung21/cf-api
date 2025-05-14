import jwt
import datetime
from functools import wraps
from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from config import SECRET_KEY

# Tạo JWT
def generate_jwt_token(user: dict) -> str:
    payload = {
        "user_id": str(user["_id"]),
        "username": user["username"],
        "phone": user["phone"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# Giải mã JWT
def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Middleware bảo vệ route bằng JWT
async def protected(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token missing")

    token = auth_header.split(" ")[1]
    return decode_jwt_token(token)
