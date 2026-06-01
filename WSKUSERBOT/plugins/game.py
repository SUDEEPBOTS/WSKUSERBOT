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


async def start_game(client: Client, user_id: int, group_id: int, mode: int = 5, announce: bool = True, delay: int = 3):
    common, all_words = load_words(mode)
    blacklist = await get_blacklist(user_id)
    if blacklist:
        bl_set = set(w.lower().strip() for w in blacklist)
        common = [w for w in common if w not in bl_set]
        all_words = [w for w in all_words if w not in bl_set]
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
    }

    if announce:
        try:
            await client.send_message(
                group_id,
                f"**Game Started!** Guess the **{MODE_NAMES[mode]}** word!"
            )
        except Exception:
            pass

    await asyncio.sleep(1)
    await client.send_message(group_id, START_CMDS[mode])
    await asyncio.sleep(2)

    starter = get_starter(mode)
    await client.send_message(group_id, starter)
    active_games[(user_id, group_id)]["guesses_sent"].append(starter)


async def handle_wordseek_response(client: Client, user_id: int, group_id: int, message_text: str):
    key = (user_id, group_id)
    if key not in active_games:
        return

    game = active_games[key]
    mode = game["mode"]
    delay = game.get("delay", 3)
    common = game.get("common", [])
    all_words = game.get("all_words", common)

    grid = parse_grid(message_text, mode)
    attempt_count = len(grid) if grid else len(game.get("guesses_sent", []))
    LOGGER.info(f"[uid={user_id}] parse_grid returned: {grid}, attempt_count={attempt_count}")
    LOGGER.info(f"[uid={user_id}] msg_text preview: {message_text[:100]}")

    if "Congrats" in message_text or "correctly" in message_text:
        word = grid[-1][0] if grid else game.get("last_solved_word")
        await update_stats(user_id, won=True, attempts=attempt_count, group_id=group_id, correct_word=word)
        del active_games[key]
        await asyncio.sleep(delay)
        await start_game(client, user_id, group_id, mode, announce=True, delay=delay)
        return

    if "Better luck" in message_text or "Game over" in message_text or "better luck" in message_text:
        await update_stats(user_id, won=False, attempts=30, group_id=group_id)
        del active_games[key]
        await asyncio.sleep(delay)
        await start_game(client, user_id, group_id, mode, announce=True, delay=delay)
        return

    lower = message_text.lower()
    if any(msg in lower for msg in INVALID_MSGS):
        already_sent = game.get("guesses_sent", [])
        bad_word = already_sent[-1] if already_sent else None
        if bad_word:
            common = [w for w in common if w != bad_word]
            game["common"] = common
        await asyncio.sleep(1)
        next_word = best_guess(common, all_words, game.get("guesses", []), attempt=attempt_count)
        LOGGER.info(f"[uid={user_id}] INVALID path, next_word={next_word}, guesses_sent={game.get('guesses_sent', [])}")
        if next_word and next_word not in game.get("guesses_sent", []):
            try:
                await client.send_message(group_id, next_word)
                game.setdefault("guesses_sent", []).append(next_word)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.send_message(group_id, next_word)
                game.setdefault("guesses_sent", []).append(next_word)
        return

    if not grid:
        LOGGER.info(f"[uid={user_id}] grid is None, returning early")
        return

    game["guesses"] = grid
    game["attempts"] = len(grid)

    filtered = filter_words(common, grid)
    game["remaining"] = len(filtered)
    LOGGER.info(f"[uid={user_id}] filtered down to {len(filtered)} candidates")

    next_word = best_guess(common, all_words, grid, attempt=attempt_count)
    LOGGER.info(f"[uid={user_id}] best_guess={next_word}, guesses_sent={game.get('guesses_sent', [])}")
    if not next_word:
        LOGGER.error(f"[uid={user_id}] best_guess returned None, cannot proceed")
        return
    if next_word in game.get("guesses_sent", []):
        LOGGER.info(f"[uid={user_id}] next_word already in guesses_sent, returning")
        return

    await asyncio.sleep(2)
    try:
        await client.send_message(group_id, next_word)
        game.setdefault("guesses_sent", []).append(next_word)
        LOGGER.info(f"[uid={user_id}] sent: {next_word}")
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await client.send_message(group_id, next_word)
        game.setdefault("guesses_sent", []).append(next_word)
        LOGGER.info(f"[uid={user_id}] sent (after floodwait): {next_word}")
