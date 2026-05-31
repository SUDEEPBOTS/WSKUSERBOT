import asyncio
from pyrogram import Client
from WSKUSERBOT.plugins import register_all
import config

async def main():
    print("╔═══════════════════════════╗")
    print("║   WSK UserBot Starting... ║")
    print("╚═══════════════════════════╝")
    
    app = Client(
        "WSKBot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
    )
    
    register_all(app)
    
    await app.start()
    me = await app.get_me()
    print(f"✅ Bot Started: @{me.username}")
    print("📖 Commands: /clone /start /bye /mode /stats")
    
    from pyrogram import idle
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
