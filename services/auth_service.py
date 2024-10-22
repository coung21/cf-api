from passlib.hash import bcrypt
from services.user_service import find_user_by_phone
from utils.jwt_utils import generate_jwt_token
import datetime


async def register_user(db, user_data):
    username = user_data.get("username")
    phone = user_data.get("phone")
    password = user_data.get("password")

    # Check if user exists
    existing_user = await find_user_by_phone(db, phone)
    if existing_user:
        return {"error": "Phone number already exists", "status": 400}

    # Hash the password
    password_hash = bcrypt.hash(password)

    # Insert user into the database
    user = {
        "username": username,
        "phone": phone,
        "password_hash": password_hash,
        "created_at": datetime.datetime.now(datetime.UTC)
    }

    result = await db.users.insert_one(user)
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}


async def login_user(db, user_data):
    phone = user_data.get("phone")
    password = user_data.get("password")

    # Find user by phone
    user = await find_user_by_phone(db, phone)
    if not user or not bcrypt.verify(password, user['password_hash']):
        return {"error": "Invalid phone number or password", "status": 400}

    # Generate JWT token
    token = generate_jwt_token(user)
    return {"message": "Login successful", "token": token}
