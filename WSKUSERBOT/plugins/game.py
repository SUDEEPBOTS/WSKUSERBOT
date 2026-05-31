import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait
from .solver import load_words, parse_grid, best_guess, STARTERS
from WSKUSERBOT.Mangodb import update_stats

START_CMDS = {
    4: "/new4@WordSeekBot",
    5: "/new5@WordSeekBot",
    6: "/new6@WordSeekBot",
}

# Active games: {user_id: {"client": client, "mode": mode, "guesses": [], "words": [], "group_id": int}}
active_games = {}

async def start_game(client: Client, user_id: int, group_id: int, mode: int = 5):
    words = load_words(mode)
    active_games[user_id] = {
        "client": client,
        "mode": mode,
        "guesses": [],
        "words": words,
        "group_id": group_id,
        "attempts": 0,
    }
    await asyncio.sleep(1)
    await client.send_message(group_id, START_CMDS[mode])
    await asyncio.sleep(2)
    # Send first guess
    starter = STARTERS.get(mode, "crane")
    await client.send_message(group_id, starter)
    active_games[user_id]["guesses_sent"] = [starter]

async def handle_wordseek_response(client: Client, user_id: int, message_text: str):
    if user_id not in active_games:
        return
    
    game = active_games[user_id]
    mode = game["mode"]
    
    # Check if won
    if "Congrats" in message_text or "correctly" in message_text:
        attempts = game.get("attempts", 0)
        await update_stats(user_id, won=True, attempts=attempts)
        del active_games[user_id]
        # Auto start next game after 3 seconds
        await asyncio.sleep(3)
        await start_game(client, user_id, game["group_id"], mode)
        return
    
    # Check if lost
    if "Better luck" in message_text or "Game over" in message_text:
        await update_stats(user_id, won=False, attempts=30)
        del active_games[user_id]
        await asyncio.sleep(3)
        await start_game(client, user_id, game["group_id"], mode)
        return
    
    # Parse grid
    grid = parse_grid(message_text, mode)
    if not grid:
        return
    
    game["guesses"] = grid
    game["attempts"] = len(grid)
    
    # Get next guess
    next_word = best_guess(game["words"], game["words"], grid)
    
    await asyncio.sleep(2)
    try:
        await client.send_message(game["group_id"], next_word)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await client.send_message(game["group_id"], next_word)
