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

import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait
from .solver import load_words, parse_grid, filter_words, best_guess, get_starter
from WSKUSERBOT.Mangodb import update_stats, get_blacklist
from WSKUSERBOT.logging import LOGGER

START_CMDS = {
    4: "/new4@WordSeekBot",
    5: "/new5@WordSeekBot",
    6: "/new6@WordSeekBot",
}

MODE_NAMES = {4: "4-letter", 5: "5-letter", 6: "6-letter"}

INVALID_MSGS = ["invalid", "not a word", "not in", "doesn't exist", "try a different", "already guessed"]

active_games = {}


def get_user_games(user_id: int):
    return {k: v for k, v in active_games.items() if k[0] == user_id}


async def start_game(client: Client, user_id: int, group_id: int, mode: int = 5, announce: bool = False, delay: int = 3):
    LOGGER.info(f"[start_game] uid={user_id} group={group_id} mode={mode}")
    common, all_words = load_words(mode)
    blacklist = await get_blacklist(user_id)
    if blacklist:
        bl_set = set(w.lower().strip() for w in blacklist)
        common = [w for w in common if w not in bl_set]
        all_words = [w for w in all_words if w not in bl_set]

    # Game state banao — guesses_sent EMPTY rakho
    active_games[(user_id, group_id)] = {
        "client": client,
        "mode": mode,
        "guesses": [],
        "common": common,
        "all_words": all_words,
        "group_id": group_id,
        "attempts": 0,
        "guesses_sent": [],
        "delay": delay,
        "last_solved_word": None,
        "remaining": len(common),
        "waiting_for_start": True,
    }

    # FIXED: "Game Started!..." waala text broadcast yahan se poori tarah hata diya hai
    await asyncio.sleep(1)
    LOGGER.info(f"[start_game] sending START_CMD: {START_CMDS[mode]}")
    await client.send_message(group_id, START_CMDS[mode])


async def handle_wordseek_response(client: Client, user_id: int, group_id: int, message_text: str):
    key = (user_id, group_id)
    if key not in active_games:
        LOGGER.info(f"[handle] uid={user_id} group={group_id} — no active game, ignoring")
        return

    game = active_games[key]
    mode = game["mode"]
    delay = game.get("delay", 3)
    common = game.get("common", [])
    all_words = game.get("all_words", common)

    first_line = message_text.splitlines()[0] if message_text else ""
    LOGGER.info(f"[handle] uid={user_id} msg: {first_line}")

    # WordSeek ne game confirm kiya — ab starter bhejo
    if game.get("waiting_for_start") and ("Game started!" in message_text or "Guess the" in message_text):
        LOGGER.info(f"[handle] uid={user_id} WordSeek confirmed game start! Sending starter...")
        game["waiting_for_start"] = False
        starter = get_starter(mode)
        await asyncio.sleep(1)
        try:
            await client.send_message(group_id, starter)
            game.setdefault("guesses_sent", []).append(starter)
            LOGGER.info(f"[handle] uid={user_id} sent starter: {starter}")
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await client.send_message(group_id, starter)
            game.setdefault("guesses_sent", []).append(starter)
        return

    # Game jeet gaye
    if "Congrats" in message_text or "correctly" in message_text:
        LOGGER.info(f"[handle] uid={user_id} WON!")
        grid = parse_grid(message_text, mode)
        attempt_count = len(grid) if grid else len(game.get("guesses_sent", []))
        word = grid[-1][0] if grid else game.get("last_solved_word")
        await update_stats(user_id, won=True, attempts=attempt_count, group_id=group_id, correct_word=word)
        del active_games[key]
        await asyncio.sleep(delay)
        # FIXED: announce=False pass kiya taaki next round automatic bina shor ke shuru ho
        await start_game(client, user_id, group_id, mode, announce=False, delay=delay)
        return

    # Game over
    if "Better luck" in message_text or "Game over" in message_text or "better luck" in message_text:
        LOGGER.info(f"[handle] uid={user_id} GAME OVER")
        await update_stats(user_id, won=False, attempts=30, group_id=group_id)
        del active_games[key]
        await asyncio.sleep(delay)
        # FIXED: announce=False pass kiya yahan bhi
        await start_game(client, user_id, group_id, mode, announce=False, delay=delay)
        return

    # Invalid word
    lower = message_text.lower()
    if any(msg in lower for msg in INVALID_MSGS):
        already_sent = game.get("guesses_sent", [])
        bad_word = already_sent[-1] if already_sent else None
        LOGGER.info(f"[handle] uid={user_id} INVALID word: {bad_word}")
        if bad_word:
            common = [w for w in common if w != bad_word]
            game["common"] = common
        await asyncio.sleep(1)
        grid = game.get("guesses", [])
        attempt_count = len(already_sent)
        next_word = best_guess(common, all_words, grid, attempt=attempt_count)
        LOGGER.info(f"[handle] uid={user_id} INVALID -> next_word={next_word}")
        if next_word and next_word not in already_sent:
            try:
                await client.send_message(group_id, next_word)
                game.setdefault("guesses_sent", []).append(next_word)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.send_message(group_id, next_word)
                game.setdefault("guesses_sent", []).append(next_word)
        return

    # Emoji grid parse karo
    grid = parse_grid(message_text, mode)
    LOGGER.info(f"[handle] uid={user_id} parse_grid={grid}")

    if not grid:
        LOGGER.info(f"[handle] uid={user_id} grid is None/empty — ignoring message")
        return

    game["guesses"] = grid
    game["attempts"] = len(grid)
    attempt_count = len(grid)

    filtered = filter_words(common, grid)
    game["remaining"] = len(filtered)
    LOGGER.info(f"[handle] uid={user_id} filtered candidates={len(filtered)}")

    next_word = best_guess(common, all_words, grid, attempt=attempt_count)
    LOGGER.info(f"[handle] uid={user_id} best_guess={next_word} guesses_sent={game.get('guesses_sent', [])}")

    if not next_word:
        LOGGER.error(f"[handle] uid={user_id} best_guess returned None!")
        return

    if next_word in game.get("guesses_sent", []):
        LOGGER.info(f"[handle] uid={user_id} {next_word} already sent, skipping")
        return

    await asyncio.sleep(2)
    try:
        await client.send_message(group_id, next_word)
        game.setdefault("guesses_sent", []).append(next_word)
        LOGGER.info(f"[handle] uid={user_id} sent: {next_word}")
    except FloodWait as e:
        LOGGER.warning(f"[handle] uid={user_id} FloodWait {e.value}s")
        await asyncio.sleep(e.value)
        await client.send_message(group_id, next_word)
        game.setdefault("guesses_sent", []).append(next_word)
        LOGGER.info(f"[handle] uid={user_id} sent after floodwait: {next_word}")
            
