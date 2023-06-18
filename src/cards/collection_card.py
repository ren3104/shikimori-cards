from jinja2 import Template

from datetime import datetime, timedelta
from typing import Any, Dict

from ..fetchers.collection_fetcher import CollectionCard
from ..themes import themes
from ..utils import wrap_text_multiline, measure_text, k_formatter


CARD_TEMPLATE = Template("""\
<svg width="400" height="{{ height }}" viewBox="0 0 400 {{ height }}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<style>
.background {
    fill: {{ options.bg_color or theme.bg_color }};
    stroke: {{ options.border_color or theme.border_color }};
}
text {
    font-family: monospace;
    font-size: 16px;
    fill: {{ options.text_color or theme.text_color }};
}
.title {
    font-size: 20px;
    fill: {{ options.title_color or theme.title_color }};
}
.icon {
    fill: {{ options.icon_color or theme.icon_color }};
}
</style>
<rect width="100%" height="100%" class="background" rx="{{ options.border_radius or theme.border_radius }}" />
<g transform="translate(20, 36)">
    <circle cx="8" cy="-5.5" r="8" fill="{{ status_color }}" />
    <text x="21">{{ status }}</text>
</g>
<text class="title" x="20" y="46">
    {% for line in title %}
    <tspan dy="1.2em" x="20">{{ line }}</tspan>
    {% endfor %}
</text>
<g transform="translate(20, {{ height - 24 }})">
    {% for stat in stats %}
    <g transform="translate({{ stat.x }}, 0)">
        <svg y="-15" width="20" height="20" viewBox="0 0 20 20" class="icon"><path d="{{ stat.icon }}"/></svg>
        <text x="25">{{ stat.value }}</text>
    </g>
    {% endfor %}
</g>
</svg>""")
                         

def render_collection_card(collection_card: CollectionCard, options: Dict[str, Any]) -> str:
    theme = themes.get(options["theme"], themes["default"])

    status = "Пополняется"
    status_color = "#44bbff"
    if collection_card.collection_size == 500:
        status = "Завершена"
        status_color = "#75d621"
    elif collection_card.changed_at is not None:
        dt = datetime.fromisoformat(collection_card.changed_at)
        if dt <= datetime.now(dt.tzinfo) - timedelta(days=730):
            status = "Заброшена"
            status_color = "#fc575e"

    title=wrap_text_multiline(
        text=collection_card.title,
        width=30
    )

    height = 102 + len(title) * 20 * 1.2

    collection_size_text = f"{collection_card.collection_size}/500"
    comments_count_text = k_formatter(collection_card.comments_count)
    votes_count = collection_card.votes_for + collection_card.votes_against
    collection_vote_text = f"{round(collection_card.votes_for / votes_count * 10, 1)}/10 ({k_formatter(votes_count)})"

    return CARD_TEMPLATE.render(
        collection_card=collection_card,
        options=options,
        theme=theme,
        height=height,
        status=status,
        status_color=status_color,
        title=title,
        stats=[
            {
                "x": 0,
                "icon": "M.7 18.36v-5.72c0-.3.1-.54.3-.74.2-.2.45-.3.74-.32h5.7c.3 0 .54.1.74.32.2.21.3.46.3.74v5.72c0 .28-.1.52-.3.72a1 1 0 0 1-.74.3h-5.7a1 1 0 0 1-.74-.3.98.98 0 0 1-.3-.72Zm0-10.92V1.72c0-.28.1-.52.3-.72a1 1 0 0 1 .74-.3h5.7c.3 0 .54.1.74.3.2.2.3.44.3.72v5.72a1 1 0 0 1-.3.74c-.2.2-.45.3-.74.32h-5.7c-.3 0-.54-.1-.74-.32-.2-.21-.3-.46-.3-.74Zm10.94 10.92v-5.72c0-.3.1-.54.3-.74.2-.2.45-.3.74-.32h5.72c.28 0 .53.1.74.32.21.21.31.46.3.74v5.72c0 .28-.1.52-.3.72a1 1 0 0 1-.74.3h-5.72c-.28 0-.53-.1-.74-.3a.89.89 0 0 1-.3-.72Zm0-10.92V1.72c0-.28.1-.52.3-.72a1 1 0 0 1 .74-.3h5.72c.3 0 .54.1.74.3.2.2.3.44.3.72v5.72a1 1 0 0 1-.3.74c-.2.2-.45.3-.74.32h-5.72c-.28 0-.53-.1-.74-.32a.95.95 0 0 1-.3-.74Z",
                "value": collection_size_text
            },
            {
                "x": 35 + round(measure_text(collection_size_text, 16), 1),
                "icon": "M15.41 7.6c0 1.02-.34 1.95-1.04 2.81a7 7 0 0 1-2.8 2.04 9.8 9.8 0 0 1-3.86.75c-.63 0-1.27-.06-1.93-.18a9.65 9.65 0 0 1-3.98 1.59h-.04a.36.36 0 0 1-.23-.1.3.3 0 0 1-.12-.24l-.02-.05.02-.08a.15.15 0 0 0 .02-.06l.02-.06.08-.12.1-.1.55-.58c.06-.07.14-.18.23-.34.1-.15.19-.3.28-.4.09-.13.16-.3.21-.5a6.3 6.3 0 0 1-2.12-1.92A4.43 4.43 0 0 1 0 7.6a4.4 4.4 0 0 1 1.04-2.83 7 7 0 0 1 2.8-2.03A9.8 9.8 0 0 1 7.71 2c1.4 0 2.68.25 3.86.75a7.02 7.02 0 0 1 2.8 2.03 4.4 4.4 0 0 1 1.04 2.83Zm4.2 2.8c0 .87-.26 1.69-.79 2.46a6.28 6.28 0 0 1-2.11 1.92c.1.33.27.64.49.9l.53.65c.11.15.2.24.25.28l.1.1.08.11.06.2-.02.06a.54.54 0 0 1-.14.25.26.26 0 0 1-.24.08 8.89 8.89 0 0 1-4-1.59c-.65.12-1.3.18-1.92.18-1.97 0-3.7-.48-5.15-1.45a11.54 11.54 0 0 0 4.33-.43 9.93 9.93 0 0 0 2.9-1.41 7.66 7.66 0 0 0 2.1-2.34 5.6 5.6 0 0 0 .47-4.43 6.37 6.37 0 0 1 2.23 1.94c.55.79.83 1.62.83 2.51Z",
                "value": comments_count_text
            },
            {
                "x": 70 + round(measure_text(collection_size_text, 16) + measure_text(comments_count_text, 16), 1),
                "icon": "M19.63 7.31c0 .17-.11.36-.32.57l-4.21 4.1 1 5.81v.25c0 .16-.04.29-.13.4a.43.43 0 0 1-.34.17.86.86 0 0 1-.47-.13l-5.23-2.75-5.2 2.75a.96.96 0 0 1-.48.14.4.4 0 0 1-.36-.18.7.7 0 0 1-.12-.4c0-.05 0-.14.02-.25l1-5.81-4.23-4.1c-.2-.21-.3-.4-.3-.57 0-.29.22-.47.65-.54l5.84-.83L9.37.64c.16-.32.34-.47.56-.47.22 0 .42.15.59.48l2.6 5.29 5.83.83c.45.07.67.25.67.54Z",
                "value": collection_vote_text
            }
        ]
    )
