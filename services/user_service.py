from bson import ObjectId


async def get_all_users(db):
    users = []
    async for user in db.users.find():
        users.append({
            "id": str(user["_id"]),
            "username": user["username"],
            "phone": user["phone"],
            "created_at": user.get("created_at").isoformat() if "created_at" in user else None
        })
    return users


async def get_user_by_id(db, user_id):
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return {
                "id": str(user["_id"]),
                "username": user["username"],
                "phone": user["phone"],
                "created_at": user.get("created_at").isoformat()
            }
        else:
            return None
    except Exception:
        return None


async def find_user_by_phone(db, phone):
    return await db.users.find_one({"phone": phone})