import time
import os
import sys
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from WSKUSERBOT.Mangodb import get_user_session, update_user_delay, get_stats, get_top_players, reset_user_stats, remove_user_session, get_blacklist, add_blacklist_word, remove_blacklist_word, update_user_mode
from WSKUSERBOT.plugins.game import active_games, get_user_games, handle_wordseek_response, start_game
from WSKUSERBOT.plugins.solver import best_guess, best_guesses, get_word_stats, filter_words, get_starter, load_words, parse_grid
from WSKUSERBOT.plugins.commands import MODE_NAMES
from WSKUSERBOT.logging import LOGGER, LOG_FILE
import config
import traceback


DELAY_HELP = "Usage: `.delay <seconds>`\nSet restart delay (1-30s)."


def register_user(client: Client, user_id: int):
    """Register . commands, Hupp/Bye, and WordSeekBot listener on a user client."""
    LOGGER.info(f"register_user called for uid={user_id}, client={id(client)}")

    @client.on_message(
        filters.command(["ping", "start", "delay", "top", "hint", "suggest", "gstatus", "stats", "reset", "id", "streak", "das", "logout", "total", "mode4", "mode5", "mode6", "mode", "help", "restart", "logs", "export", "groups", "blacklist", "history", "define"], prefixes=".")
    )
    async def user_cmds(_, message: Message):
        cmd = message.command[0].lower()
        uid = message.from_user.id

        if cmd != "restart" and cmd != "logs":
            session = await get_user_session(uid)
            if not session:
                return

            if cmd == "ping":
                start_t = time.time()
                msg = await message.edit("Pinging...")
                ms = round((time.time() - start_t) * 1000, 2)
                await msg.edit(f"Pong! `{ms}ms`")

            elif cmd == "start":
                await message.edit(
                    "**𝐖ᴏʀᴅ𝐒ᴇᴇᴋ 𝐔𝐬𝐁𝐑ʙᴏᴛ**\n\n"
                    "**Commands:**\n"
                    "├ `.ping` — Check bot latency\n"
                    "├ `.delay <sec>` — Set restart delay (1-30s)\n"
                    "├ `.das` — Session info\n"
                    "├ `.logout` — Delete session\n"
                    "├ `.top` — Leaderboard top 10\n"
                    "├ `.stats` / `.streak` — View your stats\n"
                    "├ `.gstatus` — Current game status\n"
                    "├ `.hint` — Show best next guess\n"
                    "├ `.suggest` — Show top 5 suggestions\n"
                    "├ `.history` — Show guess history\n"
                    "├ `.define` — Definition of last solved word\n"
                    "├ `.reset` — Reset your stats\n"
                    "├ `.id` — Show your user ID\n"
                    "├ `.total` — Word counts per mode\n"
                    "├ `.mode4` / `.mode5` / `.mode6` — Quick mode switch\n"
                    "├ `.groups` — List active games\n"
                    "├ `.blacklist list|add|del <word>` — Manage blacklist\n"
                    "├ `.export` — Export stats\n"
                    "├ `Hupp` — Start game (groups)\n"
                    "├ `Bye` — Stop game (groups)\n"
                    "├ `.mode` — Select word length\n"
                    "└ `.help` — Show help"
                )

            elif cmd == "delay":
                parts = message.text.split()
                if len(parts) < 2:
                    cur = session.get("delay", 3)
                    await message.edit(f"Current delay: `{cur}s`\n{DELAY_HELP}")
                    return
                try:
                    sec = int(parts[1])
                    if sec < 1 or sec > 30:
                        await message.edit("Delay must be between `1` and `30` seconds.")
                        return
                    await update_user_delay(uid, sec)
                    for (u, gid), game in active_games.items():
                        if u == uid:
                            game["delay"] = sec
                    await message.edit(f"Restart delay set to `{sec}s`")
                except ValueError:
                    await message.edit(f"Invalid number. {DELAY_HELP}")

            elif cmd == "top":
                players = await get_top_players(10)
                if not players:
                    await message.edit("No stats yet.")
                    return
                lines = ["**Leaderboard**\n"]
                for i, p in enumerate(players, 1):
                    u = p.get("user_id", 0)
                    w = p.get("wins", 0)
                    t = p.get("total_games", 0)
                    wr = (w / t * 100) if t > 0 else 0
                    s = p.get("streak", 0)
                    lines.append(f"`{i}.` ID `{u}` — Wins: `{w}` WR: `{wr:.0f}%` 🔥`{s}`")
                await message.edit("\n".join(lines))

            elif cmd == "stats" or cmd == "streak":
                stats = await get_stats(uid)
                if not stats:
                    await message.edit("No stats yet. Start playing with **Hupp**.")
                    return
                total = stats.get("total_games", 0)
                wins = stats.get("wins", 0)
                attempts = stats.get("total_attempts", 0)
                streak = stats.get("streak", 0)
                max_streak = stats.get("max_streak", 0)
                one_attempt = stats.get("one_attempt_wins", 0)
                winrate = (wins / total * 100) if total > 0 else 0
                avg = (attempts / wins) if wins > 0 else 0
                last_word = stats.get("last_word", "")
                parts = []
                parts.append(f"**WordSeek Stats**\n")
                parts.append(f"Total Games: `{total}`")
                parts.append(f"Wins: `{wins}`")
                parts.append(f"Win Rate: `{winrate:.1f}%`")
                parts.append(f"Avg Attempts: `{avg:.1f}`")
                parts.append(f"1-Guess Wins: `{one_attempt}`")
                parts.append(f"Streak: `{streak}` 🔥")
                parts.append(f"Best Streak: `{max_streak}`")
                if cmd == "stats" and last_word:
                    parts.append(f"Last Word: `{last_word}`")
                await message.edit("\n".join(parts))

            elif cmd == "gstatus":
                key, game = None, None
                for (u, gid), g in active_games.items():
                    if u == uid:
                        if message.chat.type != "private" and gid == message.chat.id:
                            key, game = (u, gid), g
                            break
                        if key is None:
                            key, game = (u, gid), g
                if not game:
                    await message.edit("No active game. Say **Hupp** in your group to start.")
                    return
                mode = game.get("mode", 5)
                attempts = game.get("attempts", 0)
                remaining = game.get("remaining", 0)
                guess_count = len(game.get("guesses_sent", []))
                gid = key[1] if key else "?"
                await message.edit(
                    f"**Game Status**\n\n"
                    f"Mode: `{mode}-letter`\n"
                    f"Group: `{gid}`\n"
                    f"Guesses sent: `{guess_count}`\n"
                    f"Rounds solved: `{attempts}`\n"
                    f"Remaining words: `{remaining}`"
                )

            elif cmd == "hint":
                key, game = None, None
                for (u, gid), g in active_games.items():
                    if u == uid:
                        if message.chat.type != "private" and gid == message.chat.id:
                            key, game = (u, gid), g
                            break
                        if key is None:
                            key, game = (u, gid), g
                if not game:
                    await message.edit("No active game. Say **Hupp** in your group to start.")
                    return
                mode = game.get("mode", 5)
                guesses = game.get("guesses", [])
                common = game.get("common", [])
                all_words = game.get("all_words", common)
                if not guesses:
                    starter = get_starter(mode)
                    await message.edit(f"First guess will be: `{starter}`")
                    return
                filtered = filter_words(common, guesses)
                if not filtered:
                    await message.edit("No matching words found. Something went wrong!")
                    return
                next_word = best_guess(common, all_words, guesses)
                if not next_word:
                    await message.edit("Could not determine next guess.")
                    return
                await message.edit(
                    f"**Next best guess:** `{next_word}`\n"
                    f"Possible words remaining: `{len(filtered)}`"
                )

            elif cmd == "suggest":
                key, game = None, None
                for (u, gid), g in active_games.items():
                    if u == uid:
                        if message.chat.type != "private" and gid == message.chat.id:
                            key, game = (u, gid), g
                            break
                        if key is None:
                            key, game = (u, gid), g
                if not game:
                    await message.edit("No active game. Say **Hupp** in your group to start.")
                    return
                mode = game.get("mode", 5)
                guesses = game.get("guesses", [])
                common = game.get("common", [])
                all_words = game.get("all_words", common)
                if not guesses:
                    starter = get_starter(mode)
                    await message.edit(f"Top suggestions:\n`1.` `{starter}` (first guess)")
                    return
                filtered = filter_words(common, guesses)
                if not filtered:
                    await message.edit("No matching words found.")
                    return
                top_n = best_guesses(common, all_words, guesses, n=5)
                lines = ["**Top 5 Suggestions**\n"]
                for i, w in enumerate(top_n, 1):
                    lines.append(f"`{i}.` `{w}`")
                lines.append(f"\nPossible words: `{len(filtered)}`")
                await message.edit("\n".join(lines))

            elif cmd == "history":
                my_games = get_user_games(uid)
                if not my_games:
                    await message.edit("No active game.")
                    return
                key = list(my_games.keys())[0]
                game = my_games[key]
                guesses = game.get("guesses", [])
                if not guesses:
                    await message.edit("No guesses yet in this game.")
                    return
                lines = ["**Guess History**\n"]
                for i, (word, pattern) in enumerate(guesses, 1):
                    pattern_str = " ".join(pattern)
                    lines.append(f"`{i}.` `{word}` `[{pattern_str}]`")
                await message.edit("\n".join(lines))

            elif cmd == "define":
                my_games = get_user_games(uid)
                if my_games:
                    key = list(my_games.keys())[0]
                    last_word = my_games[key].get("last_solved_word")
                    if last_word:
                        await message.edit(f"**Last solved word:** `{last_word}`\nUse `/define` in DM for definition.")
                        return
                await message.edit("No word solved yet.")

            elif cmd == "mode4":
                await update_user_mode(uid, 4)
                for (u, gid), game in active_games.items():
                    if u == uid:
                        game["mode"] = 4
                await message.edit("**Mode set to 4-letter**")

            elif cmd == "mode5":
                await update_user_mode(uid, 5)
                for (u, gid), game in active_games.items():
                    if u == uid:
                        game["mode"] = 5
                await message.edit("**Mode set to 5-letter**")

            elif cmd == "mode6":
                await update_user_mode(uid, 6)
                for (u, gid), game in active_games.items():
                    if u == uid:
                        game["mode"] = 6
                await message.edit("**Mode set to 6-letter**")

            elif cmd == "mode":
                parts = message.text.split()
                if len(parts) < 2:
                    cur = session.get("mode", 5)
                    await message.edit(f"Current mode: `{cur}-letter`\nUsage: `.mode <4|5|6>`")
                    return
                try:
                    mode = int(parts[1])
                    if mode not in (4, 5, 6):
                        await message.edit("Mode must be `4`, `5`, or `6`.")
                        return
                    await update_user_mode(uid, mode)
                    for (u, gid), game in active_games.items():
                        if u == uid:
                            game["mode"] = mode
                    await message.edit(f"**Mode set to {mode}-letter**")
                except ValueError:
                    await message.edit("Usage: `.mode <4|5|6>`")

            elif cmd == "help":
                await message.edit(
                    "**𝐖ᴏʀᴅ𝐒ᴇᴇᴋ 𝐔𝐬𝐁𝐑ʙᴏ𝐭**\n\n"
                    "**Commands:**\n"
                    "├ `.ping` — Check bot latency\n"
                    "├ `.delay <sec>` — Set restart delay (1-30s)\n"
                    "├ `.das` — Session info\n"
                    "├ `.logout` — Delete session\n"
                    "├ `.top` — Leaderboard top 10\n"
                    "├ `.stats` / `.streak` — View your stats\n"
                    "├ `.gstatus` — Current game status\n"
                    "├ `.hint` — Show best next guess\n"
                    "├ `.suggest` — Show top 5 suggestions\n"
                    "├ `.history` — Show guess history\n"
                    "├ `.define` — Definition of last solved word\n"
                    "├ `.reset` — Reset your stats\n"
                    "├ `.id` — Show your user ID\n"
                    "├ `.total` — Word counts per mode\n"
                    "├ `.mode4` / `.mode5` / `.mode6` — Quick mode switch\n"
                    "├ `.mode <4|5|6>` — Select word length\n"
                    "├ `.groups` — List active games\n"
                    "├ `.blacklist list|add|del <word>` — Manage blacklist\n"
                    "├ `.export` — Export stats\n"
                    "├ `Hupp` — Start game (groups)\n"
                    "├ `Bye` — Stop game (groups)\n"
                    "└ `.help` — Show help"
                )

            elif cmd == "groups":
                my_games = get_user_games(uid)
                if not my_games:
                    await message.edit("No active games in any group.")
                    return
                lines = ["**Active Groups**\n"]
                for (u, gid), game in my_games.items():
                    mode = game.get("mode", 5)
                    attempts = game.get("attempts", 0)
                    lines.append(f"├ Group `{gid}` — `{mode}-letter` — Rounds: `{attempts}`")
                await message.edit("\n".join(lines))

            elif cmd == "blacklist":
                parts = message.text.split()
                if len(parts) < 2 or parts[1].lower() not in ("list", "add", "del", "remove"):
                    await message.edit(
                        "**Blacklist Manager**\n\n"
                        "├ `.blacklist list` — Show blacklisted words\n"
                        "├ `.blacklist add <word>` — Add word\n"
                        "└ `.blacklist del <word>` — Remove word"
                    )
                    return
                sub = parts[1].lower()
                if sub == "list":
                    words = await get_blacklist(uid)
                    if not words:
                        await message.edit("No blacklisted words.")
                        return
                    lines = ["**Blacklisted Words**\n"]
                    for w in words:
                        lines.append(f"├ `{w}`")
                    await message.edit("\n".join(lines))
                elif sub == "add":
                    if len(parts) < 3:
                        await message.edit("Usage: `.blacklist add <word>`")
                        return
                    word = parts[2].lower().strip()
                    await add_blacklist_word(uid, word)
                    await message.edit(f"Added `{word}` to blacklist.")
                elif sub in ("del", "remove"):
                    if len(parts) < 3:
                        await message.edit("Usage: `.blacklist del <word>`")
                        return
                    word = parts[2].lower().strip()
                    await remove_blacklist_word(uid, word)
                    await message.edit(f"Removed `{word}` to blacklist.")

            elif cmd == "export":
                stats = await get_stats(uid)
                if not stats:
                    await message.edit("No stats to export.")
                    return
                text = (
                    f"WordSeek Stats for User {uid}\n"
                    f"{'='*35}\n"
                    f"Total Games: {stats.get('total_games', 0)}\n"
                    f"Wins: {stats.get('wins', 0)}\n"
                    f"Total Attempts: {stats.get('total_attempts', 0)}\n"
                    f"Streak: {stats.get('streak', 0)}\n"
                    f"Best Streak: {stats.get('max_streak', 0)}\n"
                    f"1-Guess Wins: {stats.get('one_attempt_wins', 0)}\n"
                )
                await message.reply_document(
                    document=text.encode(),
                    file_name=f"wsk_stats_{uid}.txt",
                    caption="**Your Stats Export**"
                )

            elif cmd == "reset":
                parts = message.text.split()
                if len(parts) < 2 or parts[1].lower() != "confirm":
                    await message.edit("Are you sure? Stats will be lost forever.\nType `.reset confirm` to proceed.")
                    return
                await reset_user_stats(uid)
                await message.edit("Stats have been reset.")

            elif cmd == "id":
                chat = message.chat
                text = f"Your ID: `{uid}`"
                if chat.type != "private":
                    text += f"\nGroup ID: `{chat.id}`"
                await message.edit(text)

            elif cmd == "das":
                mode = MODE_NAMES.get(session.get("mode", 5), "5-letter")
                delay = session.get("delay", 3)
                my_games = get_user_games(uid)
                active_count = len(my_games)
                groups = ", ".join(str(gid) for (u, gid) in my_games) if my_games else "None"
                await message.edit(
                    "**Session Info**\n\n"
                    f"User ID: `{uid}`\n"
                    f"Mode: `{mode}`\n"
                    f"Delay: `{delay}s`\n"
                    f"Active Games: `{active_count}`\n"
                    f"Groups: `{groups}`"
                )

            elif cmd == "total":
                stats = get_word_stats()
                lines = ["**Word Counts**\n"]
                for mode in [4, 5, 6]:
                    s = stats.get(mode, {})
                    c = s.get("common", 0)
                    a = s.get("all", 0)
                    unique = a - c
                    lines.append(f"`{mode}-letter` — Common: `{c}` | All: `{a}` | Unique: `{unique}`")
                await message.edit("\n".join(lines))

            elif cmd == "logout":
                for (u, gid), game in list(active_games.items()):
                    if u == uid:
                        try:
                            await game["client"].stop()
                        except Exception:
                            pass
                        del active_games[(u, gid)]
                await remove_user_session(uid)
                await message.edit("**Logged out!** Session deleted.")

    @client.on_message(filters.text & filters.group)
    async def group_handler(_, message: Message):
        if message.from_user.id != user_id:
            return
        text = message.text.strip()
        lower_text = text.lower()
        group_id = message.chat.id

        if lower_text == "hupp":
            session_data = await get_user_session(user_id)
            if not session_data:
                await message.reply("No session found!")
                return
            key = (user_id, group_id)
            if key in active_games:
                return
            active_games[key] = None
            try:
                mode = session_data.get("mode", 5)
                delay = session_data.get("delay", 3)
                await start_game(client, user_id, group_id, mode, announce=False, delay=delay)
            except Exception:
                if key in active_games and active_games[key] is None:
                    del active_games[key]
                raise

        elif lower_text == "bye":
            key = (user_id, group_id)
            if key in active_games:
                del active_games[key]
                try:
                    await client.send_message(group_id, "/end@WordSeekBot")
                except Exception:
                    pass

    # Group 1: Isko alag group diya hai taaki ye baki listeners ko block na kare
    @client.on_message(filters.all, group=1)
    async def all_debug(_, message: Message):
        if os.environ.get("WSK_DEBUG") == "1":
            first_line = message.text.splitlines()[0] if message.text else "None"
            LOGGER.info(f"ALL_DEBUG: chat={message.chat.id} type={message.chat.type} from={'None' if not message.from_user else f'id={message.from_user.id} uname=\"{message.from_user.username}\"'} text={first_line}")

    async def _handle_wordseek_msg(chat_id: int, text: str):
        first_line = text.splitlines()[0] if text else ""
        LOGGER.info(f"wordseek_handler: msg in chat {chat_id}: {first_line}")
        found = False

        for (uid, gid), game in list(active_games.items()):
            if gid == chat_id:
                found = True
                LOGGER.info(f"wordseek_handler: found active game for uid={uid}, calling handle_wordseek_response")
                try:
                    await handle_wordseek_response(game["client"], uid, gid, text)
                except Exception as e:
                    LOGGER.error(f"wordseek_handler error: {e}\n{traceback.format_exc()}")

        if not found and any(c in text for c in ("🟥", "🟨", "🟩")):
            m = re.search(r"(\d)-letter mode", text)
            if m:
                mode = int(m.group(1))
                session_data = await get_user_session(user_id)
                if session_data:
                    delay = session_data.get("delay", 3)
                    common, all_words = load_words(mode)
                    grid = parse_grid(text, mode)
                    if grid:
                        guessed_words = [w for w, _ in grid]
                        active_games[(user_id, chat_id)] = {
                            "client": client,
                            "mode": mode,
                            "guesses": grid,
                            "common": common,
                            "all_words": all_words,
                            "group_id": chat_id,
                            "attempts": len(grid),
                            "guesses_sent": guessed_words[:],
                            "delay": delay,
                            "last_solved_word": None,
                            "remaining": len(filter_words(common, grid)),
                        }
                        next_word = best_guess(common, all_words, grid, attempt=len(grid))
                        if next_word and next_word not in guessed_words:
                            await asyncio.sleep(2)
                            await client.send_message(chat_id, next_word)
                            active_games[(user_id, chat_id)]["guesses_sent"].append(next_word)

    # Group 2: WordSeekBot ke naye messages read karne ke liye
    @client.on_message(filters.all, group=2)
    async def wordseek_listener(_, message: Message):
        sender = message.from_user or message.sender_chat
        if not sender:
            return
        username = getattr(sender, "username", None)
        if not username:
            return
        
        target_bot = config.WORDSEEK_BOT.replace("@", "").strip().lower()
        if username.lower() != target_bot:
            return
            
        first_line = message.text.splitlines()[0] if message.text else ""
        LOGGER.info(f"[wordseek_listener] @{username} chat={message.chat.id}: {first_line}")
        await _handle_wordseek_msg(message.chat.id, message.text or "")

    # Group 2: WordSeekBot ke edited messages read karne ke liye
    @client.on_edited_message(filters.all, group=2)
    async def wordseek_edited_listener(_, message: Message):
        sender = message.from_user or message.sender_chat
        if not sender:
            return
        username = getattr(sender, "username", None)
        if not username:
            return
            
        target_bot = config.WORDSEEK_BOT.replace("@", "").strip().lower()
        if username.lower() != target_bot:
            return
            
        first_line = message.text.splitlines()[0] if message.text else ""
        LOGGER.info(f"[wordseek_edited_listener] @{username} chat={message.chat.id}: {first_line}")
        await _handle_wordseek_msg(message.chat.id, message.text or "")
