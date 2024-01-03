import uvloop
from flask import Flask, g
from asgiref.wsgi import WsgiToAsgi
from aiohttp import ClientSession
from shikithon import ShikimoriAPI

from typing import Optional

from views.main import bp_main
from views.cards import bp_cards


uvloop.install()
wsgi_app = Flask(__name__)
wsgi_app.register_blueprint(bp_main)
wsgi_app.register_blueprint(bp_cards)


@wsgi_app.teardown_appcontext
async def teardown_web_sessions(exception: Optional[Exception]) -> None:
    aiohttp_session: ClientSession = g.pop("aiohttp_session", None)
    if aiohttp_session is not None:
        await aiohttp_session.close()

    shikimori_session: ShikimoriAPI = g.pop("shikimori_session", None)
    if shikimori_session is not None:
        await shikimori_session.close()


app = WsgiToAsgi(wsgi_app)
