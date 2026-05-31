import asyncio
from pyrogram import Client
from WSKUSERBOT.plugins import register_all
from WSKUSERBOT.logging import LOGGER
from WSKUSERBOT.plugins.solver import load_words, WORD_CACHE
from WSKUSERBOT.user_manager import start_all_user_clients, user_clients
import config


async def main():
    LOGGER.info("Starting WordSeek Bot...")
    print("╔══════════════════════════════════╗")
    print("║     𝐖ᴏʀᴅ𝐒ᴇᴇᴋ 𝐁𝐨𝐓 𝐒𝐁𝐚𝐫𝐁𝐢𝐁𝐆...  ║")
    print("╚══════════════════════════════════╝")

    LOGGER.info("Preloading solver word cache...")
    for mode in (4, 5, 6):
        load_words(mode)
        LOGGER.info(f"Cached {len(WORD_CACHE.get(mode, []))} words for {mode}-letter mode")

    app = Client(
        "WSKBot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
    )

    register_all(app)

    await app.start()
    me = await app.get_me()
    LOGGER.info(f"Bot started as @{me.username}")

    LOGGER.info("Starting user clients...")
    await start_all_user_clients()

    print(f"╔══════════════════════════════════╗")
    print(f"║  𝐖ᴏʀᴅ𝐒ᴇᴇᴋ 𝐁𝐨𝐓 𝐑𝐮𝐧𝐁𝐢𝐁𝐆!      ║")
    print(f"║  @{me.username:<24}║")
    print(f"║  User clients: {len(user_clients)}                    ║")
    print(f"╚══════════════════════════════════╝")

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass

    for uid in list(user_clients.keys()):
        try:
            await user_clients[uid].stop()
        except Exception:
            pass
    await app.stop()
    LOGGER.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        LOGGER.info("Received shutdown signal, exiting.")
    except SystemExit:
        LOGGER.info("Restart triggered by owner.")
    except Exception as e:
        LOGGER.exception("Fatal error: %s", e)
