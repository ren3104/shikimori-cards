from cashews import cache
from selectolax.parser import HTMLParser

from dataclasses import dataclass
from typing import Optional

from . import get_aiohttp_session


@dataclass(frozen=True)
class CollectionCard:
    title: str
    votes_for: int
    votes_against: int
    collection_size: int
    comments_count: int
    changed_at: Optional[str]


@cache(ttl="4h", prefix="collection_card", key="{collection_id}")
async def fetch_collection_card(collection_id: int):
    async with get_aiohttp_session().request(
        method="GET",
        url=f"https://shikimori.me/collections/{collection_id}",
        raise_for_status=True
    ) as response:

        html_tree = HTMLParser(await response.text())
        status_line_html = html_tree.css_first(".l-page .inner .b-status-line")
        votes_html = status_line_html.css_first(".critique-votes_count")

        changed_at = None
        changed_at_html = status_line_html.css_first(".changed_at time")
        if changed_at_html is None:
            changed_at = status_line_html.css_first(".created_at time").attrs.get("datetime")
        else:
            changed_at = changed_at_html.attrs.get("datetime")

        return CollectionCard(
            title=html_tree.css_first(".l-page .head > h1").text(),
            votes_for=int(votes_html.css_first(".votes-for").text()),
            votes_against=int(votes_html.css_first(".votes-against").text()),
            collection_size=int(status_line_html.css_first(".collection-size").text()),
            comments_count=int(status_line_html.css_first(".comments").text()),
            changed_at=changed_at
        )
