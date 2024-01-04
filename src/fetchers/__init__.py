from cashews import cache
from quart import g
from aiohttp import ClientSession
from shikithon import ShikimoriAPI


cache.setup("mem://", size=100)


def get_aiohttp_session() -> ClientSession:
    try:
        return g.aiohttp_session
    except AttributeError:
        s = g.aiohttp_session = ClientSession(trust_env=True)
        return s


async def get_shikimori_session() -> ShikimoriAPI:
    try:
        return g.shikimori_session
    except AttributeError:
        s = g.shikimori_session = await ShikimoriAPI().open()
        return s
