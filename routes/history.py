from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from services.history_service import get_histories_by_user_id

history_router = APIRouter()

@history_router.get("/{user_id}", response_model=list)
async def get_histories(request: Request, user_id: str):
    print(f"Fetching histories for user_id: {user_id}")
    db = request.app.db
    histories = await get_histories_by_user_id(db, user_id)
    if histories is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Histories not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=histories)