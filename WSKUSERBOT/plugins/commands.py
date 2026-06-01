import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from WSKUSERBOT.Mangodb import (
    add_user_session, get_user_session,
    update_user_mode, remove_user_session, get_stats,
    get_all_sessions
)
from WSKUSERBOT.plugins.game import active_games, get_user_games
from WSKUSERBOT.plugins.solver import get_word_stats
from WSKUSERBOT.logging import LOGGER
import config


BOT_USERNAME = None
START_IMAGE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "start.jpeg")
MODE_NAMES = {4: "4-letter", 5: "5-letter", 6: "6-letter"}


def make_buttons(bot_username: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("𝐎𝐰𝐧𝐁𝐫", url=f"tg://user?id={config.OWNER_ID}"),
            InlineKeyboardButton("𝐇𝐁𝐥𝐩", url=f"https://t.me/{bot_username}?start=help"),
        ],
        [
            InlineKeyboardButton("𝐀𝐝𝐝 𝐌𝐁", url=f"https://t.me/{bot_username}?startgroup=start"),
            InlineKeyboardButton("𝐋𝐨𝐠𝐢𝐧", url=f"https://t.me/{bot_username}?start=login"),
        ],
    ])


HELP_TEXT = (
    "𝐖ᴏʀᴅ𝐒ᴇᴇᴋ 𝐁𝐨𝐓 𝐇𝐁𝐥𝐩\n\n"
    "**Bot Commands (DM):**\n"
    "├ `/login <session>` — Save your session\n"
    "├ `/logout` — Stop + delete session\n"
    "├ `/das` — Session info\n"
    "├ `/stats` — Your stats\n"
    "├ `/total` — Word counts\n"
    "├ `/export` — Export stats\n"
    "├ `/broadcast <msg>` — Owner broadcast\n"
    "├ `/help` — Show this\n"
    "└ `/start` — Welcome message\n\n"
    "**Userbot Commands (anywhere):**\n"
    "├ `.ping` — Latency\n"
    "├ `.delay <sec>` — Restart delay\n"
    "├ `.mode` / `.mode4/5/6` — Word length\n"
    "├ `.hint` / `.suggest` — Get hints\n"
    "├ `.gstatus` — Game status\n"
    "├ `.history` — Guess history\n"
    "├ `.streak` — Your streak\n"
    "├ `.top` — Leaderboard\n"
    "├ `.groups` — Active games\n"
    "├ `.blacklist` — Manage words\n"
    "├ `.das` — Session info\n"
    "├ `.logout` — Delete session\n"
    "├ `.export` — Export stats\n"
    "├ `.reset` — Reset stats\n"
    "├ `.id` — Your user ID\n"
    "├ `.total` — Word counts\n"
    "├ `Hupp` — Start game (group)\n"
    "└ `Bye` — Stop game (group)\n\n"
    "Powered by **𝐖ᴏʀᴅ𝐒ᴇᴇᴋ**"
)


def register(client: Client):
    global BOT_USERNAME

    @client.on_message(filters.command(["start", "clone", "login", "logout", "mode", "stats", "help", "delay", "das", "total", "broadcast", "test", "export"]) & filters.private)
    async def control_cmd(_, message: Message):
        global BOT_USERNAME
        user_id = message.from_user.id
        cmd = message.command[0].lower()

        if not BOT_USERNAME:
            bot_me = await client.get_me()
            BOT_USERNAME = bot_me.username

        if cmd == "help":
            await message.reply(HELP_TEXT)
            return

        if cmd == "start":
            deep_link = message.command[1] if len(message.command) > 1 else None
            if deep_link == "help":
                await message.reply(HELP_TEXT)
                return
            if deep_link == "login":
                await message.reply(
                    "**Send your session string:**\n\n"
                    "`/login <string_session>`\n\n"
                    "Example: `/login BQA...`"
                )
                return
            caption = (
                "<b>𝐖ᴏʀᴅ𝐒ᴇᴇᴋ 𝐁𝐨𝐓</b>\n\n"
                "<b>Welcome to 𝐖ᴏʀᴅ𝐒ᴇᴇᴋ 𝐔𝐬𝐁𝐑𝐁𝐨𝐓!</b>\n\n"
                "<blockquote>I automatically play WordSeek for you. "
                "Just clone your session, join a group, and type Hupp!</blockquote>\n\n"
                "├ <b>/login</b> — Save your session\n"
                "├ <b>/help</b> — Show all commands\n"
                "├ <b>/stats</b> — Your stats\n"
                "├ <b>/total</b> — Word counts\n"
                "└ <b>/das</b> — Session info\n\n"
                f"Made with ❤️ by <a href=\"tg://user?id={config.OWNER_ID}\"><b>Owner</b></a>"
            )
            await message.reply_photo(
                START_IMAGE,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=make_buttons(BOT_USERNAME)
            )
            return

        if cmd in ("clone", "login"):
            parts = message.text.split(None, 2)
            if len(parts) < 2:
                await message.reply(
                    "**Usage:** `/login <string_session>`\n"
                    "Example: `/login BQA...`\n\n"
                    "Then go to any group and say **Hupp**!"
                )
                return

            session = parts[1]
            msg = await message.reply("Connecting your session...")

            try:
                await add_user_session(user_id, session, 5, 3)
                from WSKUSERBOT.user_manager import start_user_client
                await start_user_client(user_id, session)
                await msg.delete()

                caption = (
                    "<b>𝐖ᴏʀᴅ𝐒ᴇᴇᴋ 𝐁𝐨𝐓</b>\n\n"
                    "<b>✅ Connected!</b>\n"
                    f"├ Mode: <code>5-letter</code>\n"
                    f"└ Delay: <code>3s</code>\n\n"
                    "<blockquote>Go to any group and type <b>Hupp</b> to start playing!</blockquote>"
                )
                await message.reply_photo(
                    START_IMAGE,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=make_buttons(BOT_USERNAME)
                )

            except Exception as e:
                err = str(e)
                if "AUTH_KEY_UNREGISTERED" in err or "SESSION_EXPIRED" in err or "unregistered" in err.lower():
                    await remove_user_session(user_id)
                    await msg.edit("Session expired or invalid. Generate a new one.")
                else:
                    await msg.edit(f"Error: `{err}`")
            return

        session_data = await get_user_session(user_id)

        if cmd == "logout":
            for (uid, gid), game in list(active_games.items()):
                if uid == user_id:
                    try:
                        await game["client"].stop()
                    except Exception:
                        pass
                    del active_games[(uid, gid)]
            from WSKUSERBOT.user_manager import stop_user_client
            await stop_user_client(user_id)
            await remove_user_session(user_id)
            await message.reply("**Logged out!** Session deleted.")

        elif cmd == "das":
            if not session_data:
                await message.reply("No session found. Use `/login <session>` first.")
                return
            mode = MODE_NAMES.get(session_data.get("mode", 5), "5-letter")
            delay = session_data.get("delay", 3)
            from WSKUSERBOT.user_manager import user_clients
            user_active = "Yes" if user_id in user_clients else "No"
            await message.reply(
                "**Session Info**\n\n"
                f"User ID: `{user_id}`\n"
                f"Mode: `{mode}`\n"
                f"Delay: `{delay}s`\n"
                f"Userbot Active: `{user_active}`"
            )

        elif cmd == "mode":
            parts = message.text.split()
            mode_map = {"four": 4, "five": 5, "six": 6}
            if len(parts) < 2:
                await message.reply(
                    "**𝐖ᴏʀᴅ𝐒ᴇᴇᴋ — Select Mode**\n\n"
                    "Use:\n"
                    "├ `/mode four` — 4-letter words\n"
                    "├ `/mode five` — 5-letter words\n"
                    "└ `/mode six` — 6-letter words"
                )
                return
            mode_str = parts[1].lower()
            if mode_str not in mode_map:
                await message.reply("Invalid! Use: `four`, `five`, or `six`")
                return
            mode = mode_map[mode_str]
            await update_user_mode(user_id, mode)
            for (uid, gid), game in active_games.items():
                if uid == user_id:
                    game["mode"] = mode
            await message.reply(f"Mode set to **{MODE_NAMES.get(mode, mode)}**")

        elif cmd == "delay":
            parts = message.text.split()
            if len(parts) < 2:
                cur = session_data.get("delay", 3) if session_data else 3
                await message.reply(f"Current delay: `{cur}s`\nUsage: `/delay <seconds>`")
                return
            try:
                sec = int(parts[1])
                if sec < 1 or sec > 30:
                    await message.reply("Delay must be between `1` and `30` seconds.")
                    return
                from WSKUSERBOT.Mangodb import update_user_delay
                await update_user_delay(user_id, sec)
                for (uid, gid), game in active_games.items():
                    if uid == user_id:
                        game["delay"] = sec
                await message.reply(f"Restart delay set to `{sec}s`")
            except ValueError:
                await message.reply("Invalid number. Usage: `/delay <seconds>`")

        elif cmd == "stats":
            stats = await get_stats(user_id)
            if not stats:
                await message.reply("**No stats yet!** Start playing with **Hupp**.")
                return
            total = stats.get("total_games", 0)
            wins = stats.get("wins", 0)
            attempts = stats.get("total_attempts", 0)
            streak = stats.get("streak", 0)
            max_streak = stats.get("max_streak", 0)
            one_attempt = stats.get("one_attempt_wins", 0)
            winrate = (wins / total * 100) if total > 0 else 0
            avg = (attempts / wins) if wins > 0 else 0
            await message.reply(
                f"**𝐖ᴏʀᴅ𝐒ᴇᴇᴋ Stats**\n\n"
                f"Total Games: `{total}`\n"
                f"Wins: `{wins}`\n"
                f"Win Rate: `{winrate:.1f}%`\n"
                f"Avg Attempts: `{avg:.1f}`\n"
                f"1-Guess Wins: `{one_attempt}`\n"
                f"Streak: `{streak}` 🔥\n"
                f"Best Streak: `{max_streak}`"
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
            await message.reply("\n".join(lines))

        elif cmd == "export":
            stats = await get_stats(user_id)
            if not stats:
                await message.reply("No stats to export.")
                return
            text = (
                f"WordSeek Stats for User {user_id}\n"
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
                file_name=f"wsk_stats_{user_id}.txt",
                caption="**Your Stats Export**"
            )

        elif cmd == "test":
            session = await get_user_session(user_id)
            from WSKUSERBOT.user_manager import user_clients
            text = f"**Bot:** Working ✅\nYour ID: `{user_id}`\n"
            if session:
                text += f"Session: Found ✅\nUserbot: {'Active ✅' if user_id in user_clients else 'Inactive ❌'}"
            else:
                text += "Session: Not found ❌"
            await message.reply(text)
            return

        elif cmd == "broadcast":
            if user_id != config.OWNER_ID:
                await message.reply("Only owner can use this command.")
                return
            parts = message.text.split(None, 1)
            if len(parts) < 2:
                await message.reply("Usage: `/broadcast <message>`")
                return
            msg_text = parts[1]
            sessions = await get_all_sessions()
            sent = 0
            failed = 0
            status = await message.reply(f"Broadcasting to {len(sessions)} users...")
            for s in sessions:
                uid = s.get("user_id")
                if not uid:
                    continue
                try:
                    await client.send_message(uid, msg_text)
                    sent += 1
                except Exception:
                    failed += 1
            await status.edit(f"Broadcast done. Sent: `{sent}`, Failed: `{failed}`")
