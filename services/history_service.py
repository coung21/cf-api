import datetime
import json
from bson import ObjectId

async def add_history(db, history_data):
    history = {
        "user_id": history_data["user_id"],
        "image_url": history_data["image_url"],
        "result": history_data["result"],
        "created_at": datetime.datetime.now()
    }
    
    try:
        result = await db["histories"].insert_one(history)
        return None
    except Exception as e:
        print("Error occurred:", e)
        return e
    

async def get_histories_by_user_id(db, user_id):
    try:
        histories = []
        async for history in db["histories"].find({"user_id": user_id}):
            histories.append({
                "id": str(history["_id"]),
                "image_url": history["image_url"],
                "result": history["result"],
                "confidence": history["confidence"],
                "created_at": history.get("created_at").isoformat()
            })
        return histories
    except Exception as e:
        print("Error occurred:", e)
        return None
    
async def get_history_by_id(db, history_id):
    try:
        # Load data from data.json
        with open('data.json', 'r', encoding='utf-8') as f:
            data_dict = json.load(f)  # Changed 'data' to 'pred'
        history = await db["histories"].find_one({"_id": ObjectId(history_id)})
        if history:
            return {
                "id": str(history["_id"]),
                "image_url": history["image_url"],
                "confidence": history["confidence"],
                "result": next((item for item in data_dict if item['idx'] == history["result"]), None),
                "created_at": history.get("created_at").isoformat()
            }
        else:
            return None
    except Exception as e:
        print("Error occurred:", e)
        return None