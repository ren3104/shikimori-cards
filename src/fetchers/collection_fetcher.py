from aiohttp import ClientSession
from selectolax.parser import HTMLParser

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CollectionCard:
    title: str
    votes_for: int
    votes_against: int
    collection_size: int
    comments_count: int
    changed_at: Optional[str]


async def fetch_collection_card(
    client: ClientSession,
    collection_id: int
) -> CollectionCard:
    async with client:
        async with client.request(
            method="GET",
            url=f"https://shikimori.one/collections/{collection_id}"
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
