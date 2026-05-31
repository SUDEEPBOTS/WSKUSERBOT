from pyrogram import Client


def register_all(client: Client):
    from .commands import register
    register(client)
