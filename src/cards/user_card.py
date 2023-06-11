from math import pi
from string import Template
from dataclasses import asdict
from typing import Any, Dict

from ..fetchers.user_fetcher import UserCard
from ..themes import CardOptions, themes


RADIUS = 50
STYLE_TEMPLATE = Template("""\
text {
    font-family: sans-serif;
    fill: ${text_color};
}
.background {
    fill: ${bg_color};
    stroke: ${border_color};
    rx: ${border_radius};
}
.nickname {
    font-size: 20px;
    fill: ${title_color};
}
.id {
    font-size: 16px;
}
.stat {
    font-size: 16px;
    fill: ${stat_color};
}
.stat-value {
    fill: ${text_color};
}
.rank {
    font-size: 36px;
    alignment-baseline: central;
    dominant-baseline: central;
    text-anchor: middle;
}
.rank-score {
    font-size: 12px;
    text-anchor: middle;
}
.rank-circle-back {
    stroke: ${bar_back_color};
    fill: none;
    stroke-width: 6;
}
.rank-circle {
    stroke: ${bar_color};
    stroke-dasharray: 314;
    stroke-dashoffset: ${progress};
    fill: none;
    stroke-width: 6;
    stroke-linecap: ${bar_round};
    transform: rotate(-90deg);
}""")
CARD_TEMPLATE = """
<svg width="450" height="256" viewBox="0 0 450 256" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<title>{nickname} карточка Shikimori пользователя, Ранг: {rank}</title>
<desc>
Просмотрено аниме: {anime_count}, Прочитано манги: {manga_count}, Выставлено оценок: {scores_count},
Создано контента: {content_count}, Сделано правок: {edits_count}, Написано комментариев: {comments_count}
</desc>
<style>
{styles}
</style>
<rect width="100%" height="100%" class="background" />
{avatar}
<text x="90" y="45" class="nickname">{nickname}</text>
<text x="90" y="71" class="id">#{id}</text>
<text x="20" y="106" class="stat">Просмотрено аниме:<tspan x="250" class="stat-value">{anime_count}</tspan></text>
<text x="20" y="132" class="stat">Прочитано манги:<tspan x="250" class="stat-value">{manga_count}</tspan></text>
<text x="20" y="158" class="stat">Выставлено оценок:<tspan x="250" class="stat-value">{scores_count}</tspan></text>
<text x="20" y="184" class="stat">Создано контента:<tspan x="250" class="stat-value">{content_count}</tspan></text>
<text x="20" y="210" class="stat">Сделано правок:<tspan x="250" class="stat-value">{edits_count}</tspan></text>
<text x="20" y="236" class="stat">Написано комментариев:<tspan x="250" class="stat-value">{comments_count}</tspan></text>
<g transform="translate(377, 163)">
    <circle class="rank-circle-back" r="50"/>
    <circle class="rank-circle" r="50"/>
    <text class="rank">{rank}</text>
    <text y="72" class="rank-score">Топ {rank_score}%</text>
</g>
</svg>
"""


def calculate_circle_progress(value: int) -> int:
    # https://blog.logrocket.com/build-svg-circular-progress-component-react-hooks/
    arc_length = 2 * pi * RADIUS
    arc_offset = (100 - value) / 100 * arc_length
    return int(arc_offset)


def get_styles(progress: int, theme: CardOptions) -> str:
    return STYLE_TEMPLATE.substitute(
        bg_color=theme.bg_color,
        border_color=theme.border_color,
        border_radius=theme.border_radius,
        title_color=theme.title_color,
        text_color=theme.text_color,
        stat_color=theme.stat_color,
        bar_back_color=theme.bar_back_color,
        bar_color=theme.bar_color,
        bar_round=(
            "round"
            if (theme.bar_round) else
            "butt"
        ),
        progress=calculate_circle_progress(progress)
    )


def get_avatar(avatar_round: bool, image: str) -> str:
    if avatar_round:
        return f'''<g transform="translate(20, 20)">
            <mask id="mask" fill="#fff"><circle cx="30" cy="30" r="30" /></mask>
            <image width="60" height="60" mask="url(#mask)" xlink:href="{image}" />
        </g>'''
    return f'<image x="20" y="20" width="60" height="60" xlink:href="{image}" />'


def render_user_card(user_card: UserCard, options: Dict[str, Any]) -> str:
    theme = themes.get(options["theme"])
    if theme is None:
        theme = themes["default"]

    return CARD_TEMPLATE.format(
        **asdict(user_card.info),
        rank=user_card.rank,
        rank_score=user_card.score,
        avatar=get_avatar(theme.avatar_round, user_card.info.image),
        styles=get_styles(
            progress=100 - user_card.score,
            theme=theme
        )
    )
