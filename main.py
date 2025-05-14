from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import cloudinary
from config import MONGO_URI, DB_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_CLOUD_NAME
from routes.predictor import predictor_router
from routes.auth import auth_router
from routes.history import history_router
app = FastAPI(title="CoffeeLeafAPI")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hoặc chỉ định domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    app.mongo_client = AsyncIOMotorClient(MONGO_URI)
    app.db = app.mongo_client[DB_NAME]
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )

@app.on_event("shutdown")
async def shutdown_event():
    app.mongo_client.close()

@app.get("/ping")
async def ping():
    return {"message": "pong"}

# Include routes
app.include_router(predictor_router, prefix="/predictor")
app.include_router(auth_router, prefix="/auth")
app.include_router(history_router, prefix="/history")