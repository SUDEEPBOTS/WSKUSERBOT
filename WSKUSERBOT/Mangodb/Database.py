# Copyright (c) 2025 @SUDEEPBOTS <HellfireDevs>
# Location: delhi,noida
#
# All rights reserved.
#
# This code is the intellectual SUDEEPBOTS.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Contact for permissions:
# Email: sudeepgithub@gmail.com

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
import config

client = AsyncIOMotorClient(config.MONGO_URI)
db = client["wskuserbot"]

users_col = db["users"]
sessions_col = db["sessions"]
stats_col = db["stats"]
blacklist_col = db["blacklist"]
leaderboard_col = db["leaderboard"]  # Global ranking system (ref #3)


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


# ═══════════════════════════════════════════════
#  Daily Stats Report helpers (ref #4)
# ═══════════════════════════════════════════════

async def get_all_active_users() -> list:
    """Get all users with active sessions for daily report."""
    sessions = await sessions_col.find({"active": True}).to_list(length=None)
    return [s["user_id"] for s in sessions if "user_id" in s]


async def get_daily_stats(user_id: int) -> dict:
    """Get formatted daily stats for a user."""
    stats = await stats_col.find_one({"user_id": user_id})
    if not stats:
        return {}
    total = stats.get("total_games", 0)
    wins = stats.get("wins", 0)
    win_rate = round((wins / total * 100), 1) if total > 0 else 0
    return {
        "total_games": total,
        "wins": wins,
        "win_rate": win_rate,
        "streak": stats.get("streak", 0),
        "max_streak": stats.get("max_streak", 0),
        "avg_attempts": round(stats.get("total_attempts", 0) / max(total, 1), 1),
        "one_attempt_wins": stats.get("one_attempt_wins", 0),
    }

