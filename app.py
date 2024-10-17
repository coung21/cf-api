from sanic import Sanic
from sanic.response import json
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.hash import bcrypt
import jwt
import datetime
from bson import ObjectId

app = Sanic("CoffeeLeaf")

# MongoDB connection
MONGO_URI = "mongodb://localhost:9191"
DB_NAME = "coffee_leaf"

SECRET_KEY = "X1m#CQUq*97PLcLB"  

@app.listener('before_server_start')
async def setup_db(app, loop):
    app.ctx.mongo_client = AsyncIOMotorClient(MONGO_URI, io_loop=loop)
    app.ctx.db = app.ctx.mongo_client[DB_NAME]  

@app.listener('after_server_stop')
async def close_db(app, loop):
    app.ctx.mongo_client.close()

# Helper function to generate JWT token
def generate_jwt(user):
    payload = {
        "user_id": str(user['_id']),
        "username": user['username'],
        "phone": user['phone'], 
        "exp": datetime.utcnow() + datetime.timedelta(hours=1)  # 1 hour expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
# Add this route to your existing Sanic app

@app.route("/test", methods=["GET"])
async def test_route(request):
    return json({"message": "test success"})
# Route: User registration (sign-up)
@app.route("/register", methods=["POST"])
async def register(request):
    user_data = request.json
    username = user_data.get("username")
    phone = user_data.get("phone")
    password = user_data.get("password")

    # Check if the user already exists based on phone number
    if await request.app.ctx.db.users.find_one({"phone": phone}):
        return json({"error": "Phone number already exists"}, status=400)

    # Hash the password
    password_hash = bcrypt.hash(password)

    # Create new user document
    user = {
        "username": username,
        "phone": phone,
        "password_hash": password_hash,
        "created_at": datetime.utcnow()
    }
    
    # Insert the user into the MongoDB collection
    result = await request.app.ctx.db.users.insert_one(user)

    # Respond with a success message
    return json({"message": "User registered successfully", "user_id": str(result.inserted_id)})

# Route: User login (sign-in)
@app.route("/login", methods=["POST"])
async def login(request):
    user_data = request.json
    phone = user_data.get("phone")
    password = user_data.get("password")

    # Find the user by phone number
    user = await request.app.ctx.db.users.find_one({"phone": phone})
    if not user:
        return json({"error": "Invalid phone number or password"}, status=400)

    # Verify the password
    if not bcrypt.verify(password, user['password_hash']):
        return json({"error": "Invalid phone number or password"}, status=400)

    # Generate JWT token
    token = generate_jwt(user)

    # Respond with the token
    return json({"message": "Login successful", "token": token})

@app.route("/users", methods=["GET"])
async def get_all_users(request):
    users = []
    async for user in request.app.ctx.db.users.find():
        users.append({
            "id": str(user["_id"]),
            "username": user["username"],
            "phone": user["phone"],
            # Convert created_at to string (ISO format)
            "created_at": user["created_at"].isoformat() if "created_at" in user else None
        })
    return json({"users": users})

# Route: Get a single user by ID
@app.route("/users/<user_id>", methods=["GET"])
async def get_user_by_id(request, user_id):
    try:
        user = await request.app.ctx.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return json({"error": "User not found"}, status=404)
        
        user_data = {
            "id": str(user["_id"]),
            "username": user["username"],
            "phone": user["phone"],
            "created_at": user["created_at"]
        }
        return json(user_data)
    
    except Exception as e:
        return json({"error": "Invalid user ID"}, status=400)

# Protected Route: Example of a protected route using JWT authentication
@app.route("/protected", methods=["GET"])
async def protected_route(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return json({"error": "Token missing"}, status=401)
    
    try:
        # Extract the token
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return json({"error": "Token expired"}, status=401)
    except jwt.InvalidTokenError:
        return json({"error": "Invalid token"}, status=401)

    # If token is valid, return protected data
    return json({"message": "This is a protected route", "user": payload})

# Run the app
if __name__ == "__main__":
    app.run(host="localhost", port=8000)
