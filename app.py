from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import HTTPConnection, Request
from starlette.responses import Response
from starlette.types import Message
from starlette.middleware import Middleware
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins import Plugin
from starlette_context import context
from aiohttp import ClientSession
from shikithon import ShikimoriAPI
from jinja2 import Environment, FileSystemLoader

from views.main import index, migrate_route
from views.cards import user_card, collection_card, bingo_card

from typing import Any, Optional, Union


class AiohttpSessionPlugin(Plugin):
    key = "aiohttp"

    async def process_request(
        self, _: Union[Request, HTTPConnection]
    ) -> Optional[Any]:
        """Runs always on request."""
        return ClientSession(trust_env=True)

    async def enrich_response(self, _: Union[Response, Message]) -> None:
        """Runs always on response."""
        session: ClientSession = context.get("aiohttp")
        await session.close()


class ShikimoriSessionPlugin(Plugin):
    key = "shikimori"

    async def process_request(
        self, _: Union[Request, HTTPConnection]
    ) -> Optional[Any]:
        """Runs always on request."""
        return await ShikimoriAPI().open()

    async def enrich_response(self, _: Union[Response, Message]) -> None:
        """Runs always on response."""
        session: ShikimoriAPI = context.get("shikimori")
        await session.close()


class JinjaPlugin(Plugin):
    key = "jinja"

    async def process_request(
        self, _: Union[Request, HTTPConnection]
    ) -> Optional[Any]:
        """Runs always on request."""
        return Environment(
            trim_blocks=True,
            loader=FileSystemLoader("src/cards/"),
            auto_reload=False
        )


app = Starlette(
    routes=[
        Route("/", index),
        Route("/migrate", migrate_route),
        Route("/user/{user_id:str}", user_card),
        Route("/collection/{collection_id:int}", collection_card),
        Route("/bingo/{user_id:int}", bingo_card)
    ],
    middleware=[
        Middleware(
            RawContextMiddleware,
            plugins=(
                AiohttpSessionPlugin(),
                ShikimoriSessionPlugin(),
                JinjaPlugin()
            )
        )
    ]
)
