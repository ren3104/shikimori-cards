from jinja2 import Template

from math import pi
from typing import Any, Dict

from ..fetchers.user_fetcher import UserCard
from ..themes import themes
from ..utils import k_formatter


def calculate_circle_progress(value: int, radius: int = 50) -> int:
    # https://blog.logrocket.com/build-svg-circular-progress-component-react-hooks/
    arc_length = 2 * pi * radius
    arc_offset = (100 - value) / 100 * arc_length
    return int(arc_offset)


CARD_TEMPLATE = Template("""\
<svg width="480" height="256" viewBox="0 0 480 256" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<title>{{ user_card.info.nickname }} карточка Shikimori пользователя, Ранг: {{ user_card.rank }}</title>
<desc>
{{ zip(stats | map(attribute="label"), stats | map(attribute="value")) | map("join", ": ") | join(", ") }}
</desc>
<style>
text {
    font-family: monospace;
    font-size: 16px;
    fill: {{ options.text_color or theme.text_color }};
}
.background {
    fill: {{ options.bg_color or theme.bg_color }};
    stroke: {{ options.border_color or theme.border_color }};
}
.nickname {
    font-size: 20px;
    fill: {{ options.title_color or theme.title_color }};
}
{% if show_icons %}
.icon {
    fill: {{ options.icon_color or theme.icon_color }};
}
{% endif %}
.stat {
    font-size: 16px;
    fill: {{ options.stat_color or theme.stat_color }};
}
.stat-value {
    fill: {{ options.text_color or theme.text_color }};
}
.rank {
    font-size: 32px;
    alignment-baseline: central;
    dominant-baseline: central;
    text-anchor: middle;
}
.rank-score {
    font-size: 12px;
    text-anchor: middle;
}
.rank-circle-back {
    stroke: {{ options.bar_back_color or theme.bar_back_color }};
    fill: none;
    stroke-width: 6;
}
.rank-circle {
    stroke: {{ options.bar_color or theme.bar_color }};
    stroke-dasharray: 314;
    {% if animate %}
    animation: rankAnimation 1s forwards ease-in-out;
    {% else %}
    stroke-dashoffset: {{ calculate_circle_progress(100 - user_card.score) }};
    {% endif %}
    fill: none;
    stroke-width: 6;
    stroke-linecap: {{ "round" if options.bar_round or theme.bar_round else "butt" }};
    transform: rotate(-90deg);
}
{% if animate %}
.stagger {
    opacity: 0;
    animation: fadeInAnimation 0.3s ease-in-out forwards;
}
@keyframes rankAnimation {
    from {
        stroke-dashoffset: {{ calculate_circle_progress(0) }};
    }
    to {
        stroke-dashoffset: {{ calculate_circle_progress(100 - user_card.score) }};
    }
}
@keyframes fadeInAnimation {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}
{% endif %}
</style>
<rect width="100%" height="100%" class="background" rx="{{ options.border_radius or theme.border_radius }}" />
<g {% if animate %}class="stagger" style="animation-delay: 150ms"{% endif %} transform="translate(20, 20)">
    {% if avatar_round %}
    <mask id="mask" fill="#fff"><circle cx="30" cy="30" r="30" /></mask>
    <image width="60" height="60" mask="url(#mask)" xlink:href="{{ user_card.info.image }}" />
    {% else %}
    <image width="60" height="60" xlink:href="{{ user_card.info.image }}" />
    {% endif %}
    <text x="70" y="25" class="nickname">{{ user_card.info.nickname }}</text>
    <text x="70" y="51" class="id">#{{ user_card.info.id }}</text>
</g>
{% for stat in stats %}
<g {% if animate %}class="stagger" style="animation-delay: {{ 150 + loop.index * 150 }}ms"{% endif %} transform="translate(20, {{ 80 + loop.index * 26 }})">
    {% if show_icons %}
    <svg y="-15" width="20" height="20" viewBox="0 0 20 20" class="icon"><path d="{{ stat.icon }}"/></svg>
    {% endif %}
    <text {% if show_icons %}x="30"{% endif %}>{{ stat.label }}:</text>
    <text {% if show_icons %}x="270"{% else %}x="250"{% endif %} class="stat-value">{{ k_formatter(stat.value) }}</text>
</g>
{% endfor %}
<g transform="translate(407, 163)">
    <circle class="rank-circle-back" r="50"/>
    <circle class="rank-circle" r="50"/>
    <text class="rank">{{ user_card.rank }}</text>
    <text y="72" class="rank-score">Топ {{ user_card.score }}%</text>
</g>
</svg>""")
CARD_TEMPLATE.globals["zip"] = zip
CARD_TEMPLATE.globals["calculate_circle_progress"] = calculate_circle_progress
CARD_TEMPLATE.globals["k_formatter"] = k_formatter


def render_user_card(user_card: UserCard, options: Dict[str, Any]) -> str:
    theme = themes.get(options["theme"], themes["default"])

    return CARD_TEMPLATE.render(
        user_card=user_card,
        options=options,
        theme=theme,
        avatar_round=options.get("avatar_round") or theme.avatar_round,
        animate=options.get("animate") or theme.animate,
        show_icons=options.get("show_icons") or theme.show_icons,
        stats=[
            {
                "icon": "M9.4 5.7h1.22l3.2 8.22h-1.2l-.9-2.52H8.24l-.92 2.52H6.17L9.4 5.7Zm-.82 4.84h2.8l-1.4-3.8-1.4 3.8ZM.38 9.8C.45 7.15 1.4 4.88 3.22 2.99a8.93 8.93 0 0 1 6.79-2.8c2.7.03 4.97.97 6.82 2.83a9.38 9.38 0 0 1 2.8 6.8 9.04 9.04 0 0 1-2.81 6.78 9.47 9.47 0 0 1-6.8 2.81 9.19 9.19 0 0 1-6.8-2.8 9.27 9.27 0 0 1-2.84-6.8Zm1.54 0c0 1.02.23 2.04.68 3.04a8.05 8.05 0 0 0 1.77 2.6 8.8 8.8 0 0 0 2.6 1.76 7.22 7.22 0 0 0 6.08.02 8.62 8.62 0 0 0 4.35-4.38c.44-.96.67-2 .68-3.04 0-1.01-.22-2.03-.67-3.05a8.28 8.28 0 0 0-4.4-4.4 7.37 7.37 0 0 0-6.04.03A8.26 8.26 0 0 0 1.92 9.8Z",
                "label": "Просмотрено аниме",
                "value": user_card.info.anime_count
            },
            {
                "icon": "M13.8 5.73v8.54h-1.15V6.9l-2.23 5.02h-.69L7.52 6.9v7.37H6.46V5.73H8l2.14 4.76 2.05-4.76h1.6ZM.31 10c.07-2.7 1.03-5.02 2.9-6.95A9.11 9.11 0 0 1 10.14.2c2.75.02 5.06.98 6.95 2.88A9.57 9.57 0 0 1 19.94 10a9.22 9.22 0 0 1-2.86 6.92 9.66 9.66 0 0 1-6.93 2.86 9.37 9.37 0 0 1-6.93-2.85A9.45 9.45 0 0 1 .32 10Zm1.57 0c0 1.05.23 2.08.69 3.1a8.2 8.2 0 0 0 1.8 2.65 8.97 8.97 0 0 0 2.65 1.8 7.36 7.36 0 0 0 6.2.02 8.79 8.79 0 0 0 4.44-4.47 7.6 7.6 0 0 0 .7-3.1 8.44 8.44 0 0 0-5.16-7.6 7.52 7.52 0 0 0-6.17.03A8.42 8.42 0 0 0 1.89 10Z",
                "label": "Прочитано манги",
                "value": user_card.info.manga_count
            },
            {
                "icon": "M19.63 7.31c0 .17-.11.36-.32.57l-4.21 4.1 1 5.81v.25c0 .16-.04.29-.13.4a.43.43 0 0 1-.34.17.86.86 0 0 1-.47-.13l-5.23-2.75-5.2 2.75a.96.96 0 0 1-.48.14.4.4 0 0 1-.36-.18.7.7 0 0 1-.12-.4c0-.05 0-.14.02-.25l1-5.81-4.23-4.1c-.2-.21-.3-.4-.3-.57 0-.29.22-.47.65-.54l5.84-.83L9.37.64c.16-.32.34-.47.56-.47.22 0 .42.15.59.48l2.6 5.29 5.83.83c.45.07.67.25.67.54Z",
                "label": "Выставлено оценок",
                "value": user_card.info.scores_count
            },
            {
                "icon": "M4.16 19.39c-.07.26-.24.3-.5.16-.24-.11-.35-.33-.32-.67.05-1.3.38-2.8.98-4.43a7.19 7.19 0 0 1-1.02-6.2 14.1 14.1 0 0 0 1.49 3.1c.29.44.5.64.6.59.13-.05.13-.6.03-1.63-.1-1.03-.18-2.12-.22-3.25-.05-1.05.12-2.1.5-3.08.28-.58.8-1.2 1.56-1.85A8.79 8.79 0 0 1 9.3.76c-.31.6-.53 1.22-.65 1.84-.11.5-.14 1.02-.07 1.53.06.4.2.6.4.63.16 0 .7-.78 1.65-2.35S12.27.04 12.7 0c.6-.04 1.35.14 2.24.57.89.44 1.42.86 1.6 1.28.16.3.16.83 0 1.55-.1.6-.37 1.17-.78 1.63a5.3 5.3 0 0 1-2.86 1.2c-1.33.25-2.08.4-2.24.48-.2.13-.13.35.24.67.7.63 1.85.76 3.45.4a6.21 6.21 0 0 1-2.67 2.23 8.7 8.7 0 0 1-2.6.74c-.66.05-1.02.12-1.04.2-.05.3.26.66.96 1.06.7.39 1.35.48 1.98.27-.4.73-.8 1.28-1.24 1.65-.43.36-.78.6-1.06.68-.27.1-.77.17-1.5.22-.7.05-1.26.1-1.65.16l-1.4 4.39h.02Z",
                "label": "Создано контента",
                "value": user_card.info.content_count
            },
            {
                "icon": "M0 12.58v-1.94l1.88-.16c.1-.4.26-.77.46-1.1L1.14 7.9 2.5 6.52l1.48 1.22c.34-.21.71-.37 1.1-.46l.16-1.88h1.94l.2 1.88c.39.1.75.25 1.1.46l1.48-1.22 1.36 1.38-1.2 1.48c.21.33.37.7.46 1.1l1.88.16v1.94l-1.88.2c-.1.39-.25.76-.46 1.1l1.2 1.44-1.36 1.4-1.48-1.2c-.35.2-.71.35-1.1.46l-.2 1.88H5.24l-.16-1.88c-.39-.1-.75-.26-1.1-.46l-1.48 1.2-1.36-1.4 1.2-1.44c-.2-.35-.35-.71-.46-1.1L0 12.58Zm4.42-.98c0 .5.17.92.52 1.28.33.35.8.54 1.28.52A1.78 1.78 0 0 0 8 11.6c.01-.52-.16-.94-.52-1.26-.35-.31-.8-.5-1.26-.52-.48-.03-.95.16-1.28.52a1.6 1.6 0 0 0-.52 1.26Zm6.36-4.76.16-1.44 1.4.04c.1-.3.24-.55.4-.78L12 3.52l1.08-.9.98.98c.26-.13.54-.22.82-.28L15.16 2l1.44.16-.04 1.36c.3.1.55.25.78.44l1.14-.78.9 1.08-.98.98c.13.27.21.55.24.86l1.36.28-.16 1.4h-1.36c-.1.27-.26.52-.44.74l.78 1.18-1.12.9-.94-.98c-.3.1-.58.19-.86.24l-.28 1.32-1.4-.12v-1.4c-.26-.1-.51-.24-.74-.4L12.3 10l-.9-1.08.98-.98c-.1-.26-.19-.54-.24-.82l-1.36-.28Zm3.32-.38c-.05.36.04.68.28.96.24.28.54.45.9.5.36.05.68-.05.96-.3.27-.23.43-.55.46-.9a1.4 1.4 0 0 0-.28-.96c-.2-.29-.53-.47-.88-.48h-.14c-.35 0-.64.11-.88.34-.24.23-.38.5-.42.84Zm-2.7 9.28.12-1h.98c.08-.21.17-.4.28-.56l-.52-.86.74-.66.72.74c.17-.1.37-.17.58-.2l.2-.96.96.1v.98c.21.08.4.19.56.32l.82-.54.62.82-.7.7c.08.17.15.37.2.58l.94.24-.12 1.02h-.98c-.05.2-.15.38-.28.54l.56.86-.8.66-.7-.74c-.17.1-.37.17-.58.2l-.2.98-.98-.12v-1.02a1.9 1.9 0 0 1-.54-.28l-.82.56-.62-.82.7-.72a2 2 0 0 1-.16-.58l-.98-.24Zm2.36-.26c-.05.28 0 .52.16.72.16.2.37.31.64.34a.9.9 0 0 0 .68-.18c.19-.15.3-.37.34-.68.04-.3-.03-.54-.2-.7a1.68 1.68 0 0 0-.62-.36h-.12a.93.93 0 0 0-.62.24.73.73 0 0 0-.26.62Z",
                "label": "Сделано правок",
                "value": user_card.info.edits_count
            },
            {
                "icon": "M15.41 7.6c0 1.02-.34 1.95-1.04 2.81a7 7 0 0 1-2.8 2.04 9.8 9.8 0 0 1-3.86.75c-.63 0-1.27-.06-1.93-.18a9.65 9.65 0 0 1-3.98 1.59h-.04a.36.36 0 0 1-.23-.1.3.3 0 0 1-.12-.24l-.02-.05.02-.08a.15.15 0 0 0 .02-.06l.02-.06.08-.12.1-.1.55-.58c.06-.07.14-.18.23-.34.1-.15.19-.3.28-.4.09-.13.16-.3.21-.5a6.3 6.3 0 0 1-2.12-1.92A4.43 4.43 0 0 1 0 7.6a4.4 4.4 0 0 1 1.04-2.83 7 7 0 0 1 2.8-2.03A9.8 9.8 0 0 1 7.71 2c1.4 0 2.68.25 3.86.75a7.02 7.02 0 0 1 2.8 2.03 4.4 4.4 0 0 1 1.04 2.83Zm4.2 2.8c0 .87-.26 1.69-.79 2.46a6.28 6.28 0 0 1-2.11 1.92c.1.33.27.64.49.9l.53.65c.11.15.2.24.25.28l.1.1.08.11.06.2-.02.06a.54.54 0 0 1-.14.25.26.26 0 0 1-.24.08 8.89 8.89 0 0 1-4-1.59c-.65.12-1.3.18-1.92.18-1.97 0-3.7-.48-5.15-1.45a11.54 11.54 0 0 0 4.33-.43 9.93 9.93 0 0 0 2.9-1.41 7.66 7.66 0 0 0 2.1-2.34 5.6 5.6 0 0 0 .47-4.43 6.37 6.37 0 0 1 2.23 1.94c.55.79.83 1.62.83 2.51Z",
                "label": "Написано комментариев",
                "value": user_card.info.comments_count
            }
        ]
    )
