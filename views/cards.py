from flask import Blueprint, abort, send_file
from shikithon.exceptions import ShikimoriAPIResponseError

from io import BytesIO
import time

from src.fetchers.user_fetcher import fetch_user_card
from src.cards.user_card import render_user_card


bp_cards = Blueprint("cards", __name__)


@bp_cards.route("/user/<string:user_id>")
async def user_card(user_id: str):
    try:
        user_id = int(user_id)
    except ValueError:
        pass

    if isinstance(user_id, int) and user_id <= 0:
        abort(404)
    
    try:
        user_card = await fetch_user_card(user_id)
    except ShikimoriAPIResponseError:
        abort(404)

    b = BytesIO(render_user_card(user_card).encode("utf-8"))
    b.seek(0)

    return send_file(
        b,
        mimetype="image/svg+xml",
        download_name=f"user_card_{user_id}.svg",
        last_modified=int(time.time()),
        max_age=300
    )
