from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.auth_service import register_user, login_user


auth_router = APIRouter()

class User(BaseModel):
    username: str
    password: str
    phone: str
    
@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: Request, user: User):
    db = request.app.db
    
    user_data = user.dict()
    result = await register_user(db, user_data)
    if "error" in result:
        raise HTTPException(status_code=result["status"], detail=result["error"])
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)


# login with phone number
class Login(BaseModel):
    phone: str
    password: str

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: Request, user: Login):
    db = request.app.db
    
    user_data = user.dict()
    result = await login_user(db, user_data)
    if "error" in result:
        raise HTTPException(status_code=result["status"], detail=result["error"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)