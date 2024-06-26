from aiohttp import ClientSession
from shikithon import ShikimoriAPI
from shikithon.utils import Utils
from selectolax.parser import HTMLParser

import asyncio
from dataclasses import dataclass
from typing import Any, Union, Dict, Tuple


ANIME_MANGA_MEAN = 125
ANIME_MANGA_WEIGHT = 2
SCORE_MEAN = 0.25
SCORE_WEIGHT = 1
CONTENT_MEAN = 1
CONTENT_WEIGHT = 3
EDITS_MEAN = 9
EDITS_WEIGHT = 3
COMMENTS_MEAN = 7
COMMENTS_WEIGHT = 1
TOTAL_WEIGHT = (
    ANIME_MANGA_WEIGHT +
    SCORE_WEIGHT +
    CONTENT_WEIGHT +
    EDITS_WEIGHT +
    COMMENTS_WEIGHT
)


@dataclass(frozen=True)
class UserInfo:
    id: int
    nickname: str
    anime_count: int
    manga_count: int
    scores_count: int
    content_count: int
    edits_count: int
    comments_count: int


@dataclass(frozen=True)
class UserCard:
    info: UserInfo
    rank: str
    score: int


def expsf(x: float, l: float = 1) -> float:
    return 2 ** (-l * x)


def calculate_rank(user_info: UserInfo) -> Tuple[str, int]:
    am_count = user_info.anime_count + user_info.manga_count

    score = (
        ANIME_MANGA_WEIGHT * expsf(am_count, 1 / ANIME_MANGA_MEAN) +
        SCORE_WEIGHT * expsf(user_info.scores_count / (am_count or 1), 1 / SCORE_MEAN) +
        (CONTENT_WEIGHT + EDITS_WEIGHT) * expsf(
            user_info.content_count + user_info.edits_count,
            1 / (CONTENT_MEAN + EDITS_MEAN)
        ) +
        COMMENTS_WEIGHT * expsf(user_info.comments_count, 1 / COMMENTS_MEAN)
    ) / TOTAL_WEIGHT

    if score <= 0.1:
        rank = "S+"
    elif score <= 0.25:
        rank = "S"
    elif score <= 0.4:
        rank = "A++"
    elif score <= 0.55:
        rank = "A+"
    elif score <= 0.7:
        rank = "A"
    elif score <= 0.8:
        rank = "B+"
    else:
        rank = "B"

    return rank, int(score * 100)


def get_score_count(scores: Dict[str, Any]) -> int:
    s = 0
    for i in scores.values():
        for j in i:
            s += j["value"]
    return s


async def fetch_user_card(
    client: ClientSession,
    api: ShikimoriAPI,
    user_id: Union[str, int]
) -> UserCard:
    if isinstance(user_id, str):
        api_user, html_user = await asyncio.gather(
            fetch_api_user(api, user_id),
            fetch_html_user(client, user_id)
        )
    else:
        api_user = await fetch_api_user(api, user_id)
        html_user = await fetch_html_user(client, api_user["nickname"])

    user_info = UserInfo(
        id=api_user["id"],
        nickname=api_user["nickname"],
        anime_count=api_user["stats"]["statuses"]["anime"][2]["size"],
        manga_count=api_user["stats"]["statuses"]["manga"][2]["size"],
        scores_count=get_score_count(api_user["stats"]["scores"]),
        content_count=sum([
            html_user.get("critiques", 0),
            html_user.get("reviews", 0),
            html_user.get("collections", 0),
            html_user.get("articles", 0)
        ]),
        edits_count=sum([
            html_user.get("versions", 0),
            html_user.get("video_uploads", 0),
            html_user.get("video_changes", 0)
        ]),
        comments_count=html_user.get("comments", 0)
    )

    rank, score = calculate_rank(user_info)

    return UserCard(user_info, rank, score)


async def fetch_api_user(
    api: ShikimoriAPI,
    user_id: Union[str, int]
) -> Dict[str, Any]:
    is_nickname = True if isinstance(user_id, str) else None
    query_dict = Utils.create_query_dict(is_nickname=is_nickname)
    
    return await api.request(
        url=api.endpoints.user(user_id),
        query=query_dict
    )


async def fetch_html_user(
    client: ClientSession,
    user_name: str
) -> Dict[str, Any]:
    result = {}

    async with client.request(
        method="GET",
        url="https://shikimori.one/" + user_name
    ) as response:
        html_tree = HTMLParser(await response.text())
        activities = html_tree.css(".profile-head .c-additionals > div")
        for activity in activities:
            _type = activity.attributes["data-type"]
            count = int(activity.text().split()[0])
            result[_type] = count
    
    return result
