import uvloop
from flask import Flask, g
from asgiref.wsgi import WsgiToAsgi
from aiohttp import ClientSession
from shikithon import ShikimoriAPI

from typing import cast, Optional

from views.main import bp_main
from views.cards import bp_cards


wsgi_app = Flask(__name__)
wsgi_app.register_blueprint(bp_main)
wsgi_app.register_blueprint(bp_cards)


@wsgi_app.teardown_appcontext
async def teardown_web_sessions(_: Optional[Exception]) -> None:
    try:
        await cast(ClientSession, g.aiohttp_session).close()
    except AttributeError:
        pass

    try:
        await cast(ShikimoriAPI, g.shikimori_session).close()
    except AttributeError:
        pass


uvloop.install()
app = WsgiToAsgi(wsgi_app)
