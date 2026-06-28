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

from pyrogram import Client
from WSKUSERBOT.Mangodb import get_all_sessions, remove_user_session
from WSKUSERBOT.plugins.start import register_user
from WSKUSERBOT.logging import LOGGER
import config

user_clients: dict[int, Client] = {}


async def start_all_user_clients():
    sessions = await get_all_sessions()
    started = 0
    for s in sessions:
        uid = s["user_id"]
        try:
            await start_user_client(uid, s["session"])
            started += 1
        except Exception as e:
            LOGGER.error(f"Failed to start user client {uid}: {e}")
            await remove_user_session(uid)
    LOGGER.info(f"Started {started}/{len(sessions)} user clients")


async def start_user_client(user_id: int, session_string: str) -> Client | None:
    if user_id in user_clients:
        return user_clients[user_id]

    client = Client(
        f"user_{user_id}",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=session_string,
        in_memory=True,
    )

    register_user(client, user_id)

    try:
        await client.start()
        user_clients[user_id] = client
        LOGGER.info(f"Started user client for {user_id}")
        return client
    except Exception as e:
        LOGGER.error(f"Could not start user client {user_id}: {e}")
        raise


async def stop_user_client(user_id: int):
    if user_id in user_clients:
        try:
            await user_clients[user_id].stop()
        except Exception:
            pass
        del user_clients[user_id]
        LOGGER.info(f"Stopped user client for {user_id}")


async def restart_user_client(user_id: int, session_string: str | None = None):
    await stop_user_client(user_id)
    if session_string:
        return await start_user_client(user_id, session_string)
    return None
