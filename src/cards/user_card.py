from math import pi
from string import Template
from dataclasses import asdict

from ..fetchers.user_fetcher import UserCard


RADIUS = 50
TEMPLATE = Template("""
<svg width="450" height="256" viewBox="0 0 450 256" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<title>${nickname} карточка Shikimori пользователя, Ранг: ${rank}</title>
<desc>
Просмотрено аниме: ${anime_count}, Прочитано манги: ${manga_count}, Выставлено оценок: ${scores_count},
Сделано контента: ${content_count}, Сделано правок: ${edits_count}, Написано комментариев: ${comments_count}
</desc>
<style>
.nickname {
    font-family: sans-serif;
    font-size: 24px;
    fill: #fff;
}
.id {
    font-size: 18px;
    fill: #9e9e9e;
}
.stat {
    font-family: sans-serif;
    font-size: 16px;
    fill: #9e9e9e;
}
.rank {
    font-family: sans-serif;
    font-size: 36px;
    fill: #9e9e9e;
    alignment-baseline: central;
    dominant-baseline: central;
    text-anchor: middle;
}
.rank-circle-rim {
    stroke: #fff;
    fill: none;
    stroke-width: 6;
    opacity: 0.2;
}
.rank-circle {
    stroke: #fff;
    stroke-dasharray: 314;
    stroke-dashoffset: ${offset};
    fill: none;
    stroke-width: 6;
    stroke-linecap: round;
    opacity: 0.8;
    transform: rotate(-90deg);
}
</style>
<rect width="100%" height="100%" rx="10" fill="#151515" />
<g transform="translate(20, 20)">
    <mask id="mask" fill="#fff"><circle cx="30" cy="30" r="30" /></mask>
    <image width="60" height="60" mask="url(#mask)" xlink:href="$image" />
</g>
<text x="90" y="56" class="nickname">${nickname} <tspan class="id">#${id}</tspan></text>
<text x="20" y="106" class="stat">Просмотрено аниме:<tspan x="250">${anime_count}</tspan></text>
<text x="20" y="132" class="stat">Прочитано манги:<tspan x="250">${manga_count}</tspan></text>
<text x="20" y="158" class="stat">Выставлено оценок:<tspan x="250">${scores_count}</tspan></text>
<text x="20" y="184" class="stat">Сделано контента:<tspan x="250">${content_count}</tspan></text>
<text x="20" y="210" class="stat">Сделано правок:<tspan x="250">${edits_count}</tspan></text>
<text x="20" y="236" class="stat">Написано комментариев:<tspan x="250">${comments_count}</tspan></text>
<g transform="translate(377, 163)">
    <circle class="rank-circle-rim" r="50"/>
    <circle class="rank-circle" r="50"/>
    <text class="rank">${rank}</text>
</g>
</svg>
""")


def calculate_circle_progress(value: int) -> int:
    # https://blog.logrocket.com/build-svg-circular-progress-component-react-hooks/
    arc_length = 2 * pi * RADIUS
    arc_offset = (100 - value) / 100 * arc_length
    return arc_offset


def render_user_card(user_card: UserCard) -> str:
    return TEMPLATE.substitute(
        **asdict(user_card.info),
        rank=user_card.rank,
        offset=int(calculate_circle_progress(100 - user_card.score))
    )
