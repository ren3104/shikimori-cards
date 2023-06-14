from flask import Blueprint, request, abort, send_file
from shikithon.exceptions import ShikimoriAPIResponseError

from io import BytesIO

from src.fetchers.user_fetcher import fetch_user_card
from src.cards.user_card import render_user_card
from src.utils import parse_integer, parse_boolean, parse_hex_color


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

    svg = render_user_card(
        user_card=user_card,
        options={
            "theme": request.args.get("theme", "default"),
            "bg_color": parse_hex_color(request.args.get("bg_color", "")),
            "border_color": parse_hex_color(request.args.get("border_color", "")),
            "border_radius": parse_integer(request.args.get("border_radius", "")),
            "font": request.args.get("font", type=str),
            "title_color": parse_hex_color(request.args.get("title_color", "")),
            "text_color": parse_hex_color(request.args.get("text_color", "")),
            "animate": parse_boolean(request.args.get("animate", "")),
            "avatar_round": parse_boolean(request.args.get("avatar_round", "")),
            "icon_color": parse_hex_color(request.args.get("icon_color", "")),
            "stat_color": parse_hex_color(request.args.get("stat_color", "")),
            "bar_back_color": parse_hex_color(request.args.get("bar_back_color", "")),
            "bar_color": parse_hex_color(request.args.get("bar_color", "")),
            "bar_round": parse_boolean(request.args.get("bar_round", "")),
            "show_icons": parse_boolean(request.args.get("show_icons", ""))
        }
    )

    b = BytesIO(svg.encode("utf-8"))
    b.seek(0)

    return send_file(
        b,
        mimetype="image/svg+xml",
        download_name=f"user_card_{user_id}.svg",
        max_age=14400
    )
