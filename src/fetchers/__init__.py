from cashews import cache
from flask import g
from aiohttp import ClientSession
from shikithon import ShikimoriAPI


cache.setup("mem://", size=100)

shiki_api = ShikimoriAPI()


def get_aiohttp_session() -> ClientSession:
    if "aiohttp_session" not in g:
        g.aiohttp_session = ClientSession()

    return g.aiohttp_session
