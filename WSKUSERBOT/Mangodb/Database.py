from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
import config

client = AsyncIOMotorClient(config.MONGO_URI)
db = client["wskuserbot"]

users_col = db["users"]
sessions_col = db["sessions"]
stats_col = db["stats"]
blacklist_col = db["blacklist"]


async def add_user_session(user_id: int, session: str, mode: int = 5, delay: int = 3) -> None:
    await sessions_col.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "session": session, "mode": mode, "delay": delay, "active": True}},
        upsert=True
    )

async def get_user_session(user_id: int) -> Optional[dict]:
    return await sessions_col.find_one({"user_id": user_id, "active": True})

async def get_all_sessions() -> list:
    return await sessions_col.find({"active": True}).to_list(length=None)

async def update_user_mode(user_id: int, mode: int) -> None:
    await sessions_col.update_one(
        {"user_id": user_id},
        {"$set": {"mode": mode}}
    )

async def update_user_delay(user_id: int, delay: int) -> None:
    await sessions_col.update_one(
        {"user_id": user_id},
        {"$set": {"delay": delay}}
    )

async def remove_user_session(user_id: int) -> None:
    await sessions_col.update_one(
        {"user_id": user_id},
        {"$set": {"active": False}}
    )

async def update_stats(user_id: int, won: bool, attempts: int, group_id: Optional[int] = None, correct_word: Optional[str] = None) -> None:
    current = await stats_col.find_one({"user_id": user_id})
    prev_streak = current.get("streak", 0) if current else 0
    streak = (prev_streak + 1) if won else 0
    max_streak = streak
    if current:
        max_streak = max(current.get("max_streak", 0), streak)

    inc_data = {
        "total_games": 1,
        "wins": 1 if won else 0,
        "total_attempts": attempts,
    }
    set_data = {
        "streak": streak,
        "max_streak": max_streak,
    }

    if won and attempts == 1:
        inc_data["one_attempt_wins"] = 1

    if correct_word:
        set_data["last_word"] = correct_word
    if group_id:
        set_data["last_group"] = group_id

    await stats_col.update_one(
        {"user_id": user_id},
        {"$inc": inc_data, "$set": set_data},
        upsert=True
    )

async def get_stats(user_id: int) -> Optional[dict]:
    return await stats_col.find_one({"user_id": user_id})

async def get_top_players(limit: int = 10) -> list:
    cursor = stats_col.find().sort([("wins", -1)]).limit(limit)
    return await cursor.to_list(length=limit)

async def reset_user_stats(user_id: int) -> None:
    await stats_col.delete_one({"user_id": user_id})

async def add_blacklist_word(user_id: int, word: str) -> None:
    word = word.lower().strip()
    await blacklist_col.update_one(
        {"user_id": user_id},
        {"$addToSet": {"words": word}},
        upsert=True
    )

async def remove_blacklist_word(user_id: int, word: str) -> None:
    word = word.lower().strip()
    await blacklist_col.update_one(
        {"user_id": user_id},
        {"$pull": {"words": word}}
    )

async def get_blacklist(user_id: int) -> list:
    doc = await blacklist_col.find_one({"user_id": user_id})
    return doc.get("words", []) if doc else []
