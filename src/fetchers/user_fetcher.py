from cashews import cache
from selectolax.parser import HTMLParser

from dataclasses import dataclass
import base64
from typing import cast, Any, Dict, Tuple

from . import get_aiohttp_session, shiki_api
from ..type_hints import JsonObject


cache.setup("mem://", prefix="user_info", size=100)

ANIME_MANGA_MEAN = 125
ANIME_MANGA_WEIGHT = 3
SCORE_MEAN = 0.5
SCORE_WEIGHT = 2
CONTENT_MEAN = 1
CONTENT_WEIGHT = 5
EDITS_MEAN = 9
EDITS_WEIGHT = 4
COMMENTS_MEAN = 72
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
    image: str
    last_online: str
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


def expsf(x, l = 1):
    return 2 ** (-l * x)


def calculate_rank(user_info: UserInfo) -> Tuple[str, int]:
    am_count = user_info.anime_count + user_info.manga_count

    score = (
        ANIME_MANGA_WEIGHT * expsf(am_count, 1 / ANIME_MANGA_MEAN) +
        SCORE_WEIGHT * expsf(user_info.scores_count / am_count, 1 / SCORE_MEAN) +
        CONTENT_WEIGHT * expsf(user_info.content_count, 1 / CONTENT_MEAN) +
        EDITS_WEIGHT * expsf(user_info.edits_count, 1 / EDITS_MEAN) +
        COMMENTS_WEIGHT * expsf(user_info.comments_count, 1 / COMMENTS_MEAN)
    ) / TOTAL_WEIGHT

    if score <= 0.1:
        rank = "S"
    elif score <= 0.25:
        rank = "A"
    elif score <= 0.4:
        rank = "B"
    elif score <= 0.55:
        rank = "C"
    elif score <= 0.7:
        rank = "D"
    elif score <= 0.8:
        rank = "E"
    else:
        rank = "F"

    return rank, int(score * 100)


def get_score_count(scores: Dict[str, Any]) -> int:
    s = 0
    for i in scores.values():
        for j in i:
            s += j["value"]
    return s


@cache(ttl="5m", prefix="user_info", key="{user_id}")
async def fetch_user_card(user_id: int) -> UserCard:
    api_user = await fetch_api_user(user_id)
    image_user = await fetch_user_image(api_user["image"]["x64"])
    html_user = await fetch_html_user(api_user["nickname"])

    user_info = UserInfo(
        id=api_user["id"],
        nickname=api_user["nickname"],
        image=image_user,
        last_online=cast(str, api_user["last_online"]).capitalize(),
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


async def fetch_api_user(user_id: int) -> JsonObject:
    async with shiki_api:
        return await shiki_api.request(
            url=shiki_api.endpoints.user(user_id)
        )
    

async def fetch_user_image(url: str) -> str:
    async with get_aiohttp_session().request(
        method="GET",
        url=url
    ) as response:
        
        return (
            "data:" + 
            response.headers["Content-Type"] + ";" +
            "base64," +
            base64.b64encode(await response.content.read()).decode("utf-8")
        )


async def fetch_html_user(user_name: str) -> JsonObject:
    result = {}

    async with get_aiohttp_session().request(
        method="GET",
        url="https://shikimori.me/" + user_name
    ) as response:
        
        html_tree = HTMLParser(await response.text())
        activities = html_tree.css(".profile-head .c-additionals > div")
        for activity in activities:
            _type = activity.attributes["data-type"]
            count = int(activity.text().split()[0])
            result[_type] = count
    
    return result
