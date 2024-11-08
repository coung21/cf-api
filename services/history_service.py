from bson import ObjectId
import datetime

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
    
