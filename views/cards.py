from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException
from aiohttp import ClientSession
from aiohttp import ClientResponseError
from shikithon import ShikimoriAPI
from shikithon.exceptions import ShikimoriAPIResponseError
from jinja2 import Environment, FileSystemLoader

from datetime import datetime, timedelta

from src.fetchers.user_fetcher import fetch_user_card
from src.fetchers.collection_fetcher import fetch_collection_card
from src.utils import (
    send_svg_file,
    calculate_ring_progress,
    k_formatter,
    measure_text,
    wrap_text_multiline,
    parse_integer,
    parse_boolean,
    parse_hex_color
)
from src.themes import themes
from src.icons import icons


async def user_card(request: Request) -> Response:
    user_id: str = request.path_params["user_id"]
    try:
        user_id = int(user_id)
    except ValueError:
        pass
    else:
        if user_id <= 0:
            raise HTTPException(404)
    
    try:
        card = await fetch_user_card(
            client=ClientSession(trust_env=True),
            api=ShikimoriAPI(),
            user_id=user_id
        )
    except ShikimoriAPIResponseError:
        raise HTTPException(404)

    card_icons = icons["shikimori"]
    stats = [
        {"icon": card_icons.anime, "label": "Просмотрено аниме", "value": k_formatter(card.info.anime_count)},
        {"icon": card_icons.manga, "label": "Прочитано манги", "value": k_formatter(card.info.manga_count)},
        {"icon": card_icons.score, "label": "Выставлено оценок", "value": k_formatter(card.info.scores_count)},
        {"icon": card_icons.content, "label": "Создано контента", "value": k_formatter(card.info.content_count)},
        {"icon": card_icons.edit, "label": "Сделано правок", "value": k_formatter(card.info.edits_count)},
        {"icon": card_icons.comment, "label": "Написано комментариев", "value": k_formatter(card.info.comments_count)}
    ]
    jinja_env = Environment(
        trim_blocks=True,
        loader=FileSystemLoader("src/cards/"),
        auto_reload=False
    )
    tmpl = jinja_env.get_template(
        name="user_card.svg",
        globals={"calculateRingProgress": calculate_ring_progress}
    )
    svg_text = tmpl.render(
        height=226,
        width=480,
        title=f"Shikimori карточка {card.info.nickname}, Ранг: {card.rank}",
        description=", ".join([f"{stat['label']}: {stat['value']}" for stat in stats]),
        nickname=card.info.nickname,
        rank=card.rank,
        score=card.score,
        stats=stats,
        options={
            "bg_color": parse_hex_color(request.query_params.get("bg_color", "")),
            "border_color": parse_hex_color(request.query_params.get("border_color", "")),
            "border_radius": parse_integer(request.query_params.get("border_radius", "")),
            "title_color": parse_hex_color(request.query_params.get("title_color", "")),
            "text_color": parse_hex_color(request.query_params.get("text_color", "")),
            "icon_color": parse_hex_color(request.query_params.get("icon_color", "")),
            "bar_color": parse_hex_color(request.query_params.get("bar_color", "")),
            "bar_back_color": parse_hex_color(request.query_params.get("bar_back_color", "")),
            "bar_round": parse_boolean(request.query_params.get("bar_round", "")),
            "show_icons": parse_boolean(request.query_params.get("show_icons", "")),
            "animated": parse_boolean(request.query_params.get("animated", ""))
        },
        theme=themes.get(request.query_params.get("theme", "default"), themes["default"])
    )

    return send_svg_file(
        svg_text=svg_text,
        file_name=f"user_card_{user_id}.svg"
    )


async def collection_card(request: Request) -> Response:
    collection_id: int = request.path_params["collection_id"]
    if collection_id <= 0:
        raise HTTPException(404)
    try:
        card = await fetch_collection_card(
            client=ClientSession(trust_env=True),
            collection_id=collection_id
        )
    except ClientResponseError:
        raise HTTPException(404)

    status = "Пополняется"
    status_color = "#44bbff"
    if card.collection_size == 500:
        status = "Завершена"
        status_color = "#75d621"
    elif card.changed_at is not None:
        dt = datetime.fromisoformat(card.changed_at)
        if dt <= datetime.now(dt.tzinfo) - timedelta(days=730):
            status = "Заброшена"
            status_color = "#fc575e"

    collection_size_text = f"{card.collection_size}/500"
    comments_count_text = k_formatter(card.comments_count)
    votes_count = card.votes_for + card.votes_against
    collection_vote_text = f"{round(card.votes_for / votes_count * 10, 1)}/10 ({k_formatter(votes_count)})"

    card_icons = icons["shikimori"]
    stats=[
        {"x": 0,
         "icon": card_icons.collection_size,
         "value": collection_size_text},
        {"x": 35 + round(measure_text(collection_size_text, 16), 1), 
         "icon": card_icons.comment,
         "value": comments_count_text},
        {"x": 70 + round(measure_text(collection_size_text, 16) + measure_text(comments_count_text, 16), 1),
         "icon": card_icons.score,
         "value": collection_vote_text}
    ]
    collection_name=wrap_text_multiline(
        text=card.title,
        width=360,
        font_size=20
    )
    height = 102 + len(collection_name) * 20 * 1.2
    jinja_env = Environment(
        trim_blocks=True,
        loader=FileSystemLoader("src/cards/"),
        auto_reload=False
    )
    tmpl = jinja_env.get_template("collection_card.svg")
    svg_text = tmpl.render(
        height=height,
        width=400,
        status=status,
        status_color=status_color,
        collection_name=collection_name,
        stats=stats,
        options={
            "bg_color": parse_hex_color(request.query_params.get("bg_color", "")),
            "border_color": parse_hex_color(request.query_params.get("border_color", "")),
            "border_radius": parse_integer(request.query_params.get("border_radius", "")),
            "title_color": parse_hex_color(request.query_params.get("title_color", "")),
            "text_color": parse_hex_color(request.query_params.get("text_color", "")),
            "icon_color": parse_hex_color(request.query_params.get("icon_color", ""))
        },
        theme=themes.get(request.query_params.get("theme", "default"), themes["default"])
    )

    return send_svg_file(
        svg_text=svg_text,
        file_name=f"collection_card_{collection_id}.svg"
    )
