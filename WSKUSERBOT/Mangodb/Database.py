from motor.motor_asyncio import AsyncIOMotorClient
import config

client = AsyncIOMotorClient(config.MONGO_URI)
db = client["wskuserbot"]

users_col = db["users"]
sessions_col = db["sessions"]
stats_col = db["stats"]


async def add_user_session(user_id: int, session: str, mode: int = 5):
    await sessions_col.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "session": session, "mode": mode, "active": True}},
        upsert=True
    )

async def get_user_session(user_id: int):
    return await sessions_col.find_one({"user_id": user_id, "active": True})

async def get_all_sessions():
    return await sessions_col.find({"active": True}).to_list(length=None)

async def update_user_mode(user_id: int, mode: int):
    await sessions_col.update_one(
        {"user_id": user_id},
        {"$set": {"mode": mode}}
    )

async def remove_user_session(user_id: int):
    await sessions_col.update_one(
        {"user_id": user_id},
        {"$set": {"active": False}}
    )

async def update_stats(user_id: int, won: bool, attempts: int):
    await stats_col.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "total_games": 1,
                "wins": 1 if won else 0,
                "total_attempts": attempts
            }
        },
        upsert=True
    )

async def get_stats(user_id: int):
    return await stats_col.find_one({"user_id": user_id})
