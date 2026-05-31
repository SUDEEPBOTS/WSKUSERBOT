import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait
from .solver import load_words, parse_grid, filter_words, best_guess, STARTERS
from WSKUSERBOT.Mangodb import update_stats

START_CMDS = {
    4: "/new4@WordSeekBot",
    5: "/new5@WordSeekBot",
    6: "/new6@WordSeekBot",
}

MODE_NAMES = {4: "4-letter", 5: "5-letter", 6: "6-letter"}

INVALID_MSGS = ["invalid", "not a word", "not in", "doesn't exist", "try a different"]

active_games = {}


def get_user_games(user_id: int):
    return {k: v for k, v in active_games.items() if k[0] == user_id}


async def start_game(client: Client, user_id: int, group_id: int, mode: int = 5, announce: bool = True, delay: int = 3):
    words = load_words(mode)
    active_games[(user_id, group_id)] = {
        "client": client,
        "mode": mode,
        "guesses": [],
        "words": words,
        "group_id": group_id,
        "attempts": 0,
        "guesses_sent": [],
        "delay": delay,
        "last_solved_word": None,
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

    starter = STARTERS.get(mode, "crane")
    await client.send_message(group_id, starter)
    active_games[(user_id, group_id)]["guesses_sent"].append(starter)


async def handle_wordseek_response(client: Client, user_id: int, group_id: int, message_text: str):
    key = (user_id, group_id)
    if key not in active_games:
        return

    game = active_games[key]
    mode = game["mode"]
    delay = game.get("delay", 3)

    if "Congrats" in message_text or "correctly" in message_text:
        attempts = len(game.get("guesses", [])) + 1
        word = game.get("last_correct_word")
        await update_stats(user_id, won=True, attempts=attempts, group_id=group_id, correct_word=word)

        guesses = game.get("guesses", [])
        if guesses:
            last_guess_word = guesses[-1][0]
            if len(game.get("guesses_sent", [])) >= 1 and game["guesses_sent"][-1] == last_guess_word and attempts == 1:
                pass

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
        if already_sent:
            bad_word = already_sent[-1]
            if bad_word in game["words"]:
                game["words"].remove(bad_word)
        await asyncio.sleep(1)
        next_word = best_guess(game["words"], game["words"], game.get("guesses", []))
        if next_word and next_word not in game.get("guesses_sent", []):
            try:
                await client.send_message(group_id, next_word)
                game.setdefault("guesses_sent", []).append(next_word)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.send_message(group_id, next_word)
                game.setdefault("guesses_sent", []).append(next_word)
        return

    grid = parse_grid(message_text, mode)
    if not grid:
        return

    game["guesses"] = grid
    game["attempts"] = len(grid)

    filtered = filter_words(game["words"], grid)
    game["remaining"] = len(filtered)

    next_word = best_guess(game["words"], game["words"], grid)
    if next_word in game.get("guesses_sent", []):
        return

    await asyncio.sleep(2)
    try:
        await client.send_message(group_id, next_word)
        game.setdefault("guesses_sent", []).append(next_word)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await client.send_message(group_id, next_word)
        game.setdefault("guesses_sent", []).append(next_word)
