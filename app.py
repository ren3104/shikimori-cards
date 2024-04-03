from starlette.applications import Starlette
from starlette.routing import Route
from aiohttp import ClientSession
from shikithon import ShikimoriAPI
from jinja2 import Environment, FileSystemLoader

from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict

from views.main import index
from views.cards import user_card, collection_card


class State(TypedDict):
    client: ClientSession
    api: ShikimoriAPI
    jinja_env: Environment


@asynccontextmanager
async def lifespan(_: Starlette) -> AsyncIterator[State]:
    client = ClientSession(trust_env=True)
    api = ShikimoriAPI()
    async with client, api:
        yield {
            "client": client,
            "api": api,
            "jinja_env": Environment(
                trim_blocks=True,
                loader=FileSystemLoader("src/cards/"),
                auto_reload=False
            )
        }


app = Starlette(
    routes=[
        Route("/", index),
        Route("/user/{user_id:str}", user_card),
        Route("/collection/{collection_id:int}", collection_card)
    ],
    lifespan=lifespan
)
