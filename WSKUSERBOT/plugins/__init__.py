from pyrogram import Client, filters
from pyrogram.types import Message
from .game import handle_wordseek_response, active_games
import config

def register_all(client: Client):
    from .commands import register
    register(client)
    
    @client.on_message(
        filters.text & 
        filters.group
    )
    async def message_handler(_, message: Message):
        # Check if message is from WordSeek bot
        if message.from_user and message.from_user.username == config.WORDSEEK_BOT:
            text = message.text or ""
            # Find which user's game this is for
            for user_id, game in list(active_games.items()):
                if game.get("group_id") == message.chat.id:
                    await handle_wordseek_response(
                        game["client"], user_id, text
                    )
