from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException
from aiohttp import ClientSession, ClientResponseError
from shikithon import ShikimoriAPI
from shikithon.exceptions import ShikimoriAPIResponseError
from jinja2 import Environment
from starlette_context import context

import asyncio
from datetime import datetime, timedelta
from base64 import b64encode
from typing import Tuple, get_args

from src.fetchers.user_fetcher import fetch_user_card
from src.fetchers.collection_fetcher import fetch_collection_card
from src.database import get_db_session, BingoCard
from src.bingo.__main__ import (
    generate_bingo_card,
    db_get_bingo_card,
    count_completed_tasks
)
from src.bingo.checks import BINGO_TASKS, get_product_type
from src.bingo.type_hints import ProductType
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
            client=context["aiohttp"],
            api=context["shikimori"],
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
    jinja_env: Environment = context["jinja"]
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
        theme=themes.get(request.query_params.get("theme", "default"))
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
            client=context["aiohttp"],
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
    jinja_env: Environment = context["jinja"]
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
        theme=themes.get(request.query_params.get("theme", "default"))
    )

    return send_svg_file(
        svg_text=svg_text,
        file_name=f"collection_card_{collection_id}.svg"
    )


async def bingo_card(request: Request) -> Response:
    user_id: int = request.path_params["user_id"]
    if user_id <= 0:
        raise HTTPException(404)

    product_types = request.query_params.get("types", "").split(",")
    if len(product_types) == 0 or any([t not in get_args(ProductType) for t in product_types]):
        raise HTTPException(400)

    async with get_db_session() as db:
        bingo_card = await db_get_bingo_card(db, user_id)
        api: ShikimoriAPI = context["shikimori"]
        if bingo_card is None:
            history = await api.users.history(
                user_id=user_id,
                page=1,
                limit=1
            )
            if len(history) == 0:
                raise HTTPException(400)

            bingo_card = BingoCard(
                user_id=user_id,
                last_history_id=history[0].id,
                stats=generate_bingo_card(16, product_types)
            )

            db.add(bingo_card)
            await db.commit()
        else:
            if count_completed_tasks(bingo_card.stats) < len(bingo_card.stats):
                history = await api.users.history(
                    user_id=user_id,
                    page=1,
                    limit=100
                )
                if len(history) != 0:
                    # [! Change this code only if you have checked it thoroughly
                    bingo_stats: dict = bingo_card.stats.copy()
                    for h in history:
                        if h.id == bingo_card.last_history_id:
                            break
                        for k, v in bingo_stats.items():
                            if v is not None:
                                continue
                            task_check = BINGO_TASKS[int(k) - 1]
                            if not await task_check.check(api, h):
                                continue
                            bingo_stats[k] = f"{get_product_type(h.target)}-{h.target.id}"
                    bingo_card.stats = bingo_stats
                    # !]
                    bingo_card.last_history_id = history[0].id
                    await db.commit()
            else:
                bingo_card.stats = generate_bingo_card(16, product_types)
                await db.commit()

        async def _get_poster(stat: str, url: str) -> Tuple[str, str]:
            client: ClientSession = context["aiohttp"]
            async with client.get(url) as resp:
                return stat, "data:image/jpg;base64," + b64encode(await resp.read()).decode("ascii")
            
        posters = dict(await asyncio.gather(*[
            _get_poster(
                stat=stat,
                url="https://shikimori.one/" + (
                    "system/animes/preview/{}.jpg"
                    if stat.startswith("anime") else
                    "system/mangas/preview/{}.jpg"
                ).format(stat.split("-")[1])
            )
            for stat in bingo_card.stats.values()
            if stat is not None
        ]))

        jinja_env: Environment = context["jinja"]
        tmpl = jinja_env.get_template("bingo_card.svg")
        svg_text = tmpl.render(
            height=1000,
            width=700,
            cell_per_row=4,
            cell_height=200,
            cell_width=150,
            cell_gap=20,
            bingo_stats=bingo_card.stats,
            posters=posters,
            stats_descr={
                n: wrap_text_multiline(
                    text=BINGO_TASKS[int(n) - 1].description,
                    width=150,
                    font_size=20,
                    max_lines=7
                )
                for n in bingo_card.stats.keys()
            },
            options={
                "bg_color": parse_hex_color(request.query_params.get("bg_color", "")),
                "border_color": parse_hex_color(request.query_params.get("border_color", "")),
                "border_radius": parse_integer(request.query_params.get("border_radius", "")),
                "title_color": parse_hex_color(request.query_params.get("title_color", "")),
                "text_color": parse_hex_color(request.query_params.get("text_color", ""))
            },
            theme=themes.get(request.query_params.get("theme", "default"))
        )

        db.expire(bingo_card)

    return send_svg_file(
        svg_text=svg_text,
        file_name=f"bingo_card_{user_id}.svg"
    )
