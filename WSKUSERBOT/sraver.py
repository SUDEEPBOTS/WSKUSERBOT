import asyncio
import signal

from aiohttp import web


async def ping_handler(_):
    return web.Response(text="ok")


async def start_server():
    app = web.Application()
    app.router.add_get("/", ping_handler)
    app.router.add_get("/health", ping_handler)

    runner = web.AppRunner(app)
    await runner.setup()

    port = 8080
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[sraver] Keep-alive server running on port {port}")

    stop = asyncio.Future()

    def shutdown():
        if not stop.done():
            stop.set_result(None)

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown)
        except NotImplementedError:
            pass

    await stop
    await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(start_server())
