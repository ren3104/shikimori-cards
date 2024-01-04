import uvloop
from flask import Flask, g
from aiohttp import ClientSession
from shikithon import ShikimoriAPI

from typing import cast, Optional

from views.main import bp_main
from views.cards import bp_cards


uvloop.install()

app = Flask(__name__)
app.register_blueprint(bp_main)
app.register_blueprint(bp_cards)


@app.teardown_appcontext
async def teardown_web_sessions(_: Optional[Exception]) -> None:
    try:
        await cast(ClientSession, g.aiohttp_session).close()
    except AttributeError:
        pass

    try:
        await cast(ShikimoriAPI, g.shikimori_session).close()
    except AttributeError:
        pass
