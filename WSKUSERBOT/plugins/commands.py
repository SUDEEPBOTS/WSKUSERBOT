from pyrogram import Client, filters
from pyrogram.types import Message
from WSKUSERBOT.Mangodb import (
    add_user_session, get_user_session, 
    update_user_mode, remove_user_session, get_stats
)
from .game import start_game, active_games
import config

app = None  # Will be set from __init__

def register(client: Client):
    
    @client.on_message(filters.command("clone") & filters.private)
    async def clone_cmd(_, message: Message):
        parts = message.text.split(None, 2)
        if len(parts) < 3:
            await message.reply(
                "**Usage:** `/clone <string_session> <group_id>`\n\n"
                "Example: `/clone BQA... -1001234567890`"
            )
            return
        
        session = parts[1]
        try:
            group_id = int(parts[2])
        except ValueError:
            await message.reply("❌ Invalid group ID!")
            return
        
        user_id = message.from_user.id
        mode = 5  # default
        
        msg = await message.reply("🔄 Connecting your session...")
        
        try:
            user_client = Client(
                f"user_{user_id}",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=session,
                in_memory=True
            )
            await user_client.start()
            me = await user_client.get_me()
            
            await add_user_session(user_id, session, mode)
            
            await msg.edit(
                f"✅ **Connected!**\n\n"
                f"👤 Account: `{me.first_name}`\n"
                f"📊 Mode: `{mode}-letter`\n\n"
                f"Use `.start <group_id>` to begin!"
            )
            
        except Exception as e:
            await msg.edit(f"❌ Error: `{e}`")
    
    @client.on_message(filters.command(["start", "bye", "mode", "stats"]) & filters.private)
    async def control_cmd(_, message: Message):
        user_id = message.from_user.id
        cmd = message.command[0]
        
        session_data = await get_user_session(user_id)
        
        if cmd == "start":
            if not session_data:
                await message.reply("❌ No session! Use `/clone <session> <group_id>` first.")
                return
            
            parts = message.text.split()
            group_id = int(parts[1]) if len(parts) > 1 else None
            if not group_id:
                await message.reply("❌ Group ID do!\nUsage: `/start <group_id>`")
                return
            
            await message.reply("🎮 **Game Starting...**")
            
            user_client = Client(
                f"user_{user_id}",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=session_data["session"],
                in_memory=True
            )
            await user_client.start()
            
            mode = session_data.get("mode", 5)
            await start_game(user_client, user_id, group_id, mode)
            await message.reply(f"✅ **Started!** Mode: `{mode}-letter`")
        
        elif cmd == "bye":
            if user_id in active_games:
                del active_games[user_id]
            await remove_user_session(user_id)
            await message.reply("👋 **Stopped!**")
        
        elif cmd == "mode":
            parts = message.text.split()
            if len(parts) < 2:
                await message.reply("Usage: `/mode four` or `/mode five` or `/mode six`")
                return
            
            mode_map = {"four": 4, "five": 5, "six": 6}
            mode_str = parts[1].lower()
            
            if mode_str not in mode_map:
                await message.reply("❌ Invalid! Use: `four`, `five`, or `six`")
                return
            
            mode = mode_map[mode_str]
            await update_user_mode(user_id, mode)
            
            # Update active game if running
            if user_id in active_games:
                active_games[user_id]["mode"] = mode
            
            await message.reply(f"✅ Mode set to **{mode_str} ({mode}-letter)**")
        
        elif cmd == "stats":
            stats = await get_stats(user_id)
            if not stats:
                await message.reply("📊 No stats yet! Start playing first.")
                return
            
            total = stats.get("total_games", 0)
            wins = stats.get("wins", 0)
            attempts = stats.get("total_attempts", 0)
            winrate = (wins / total * 100) if total > 0 else 0
            avg = (attempts / wins) if wins > 0 else 0
            
            await message.reply(
                f"📊 **Your Stats**\n\n"
                f"🎮 Total Games: `{total}`\n"
                f"✅ Wins: `{wins}`\n"
                f"📈 Win Rate: `{winrate:.1f}%`\n"
                f"🎯 Avg Attempts: `{avg:.1f}`"
            )
