from starlette.applications import Starlette
from starlette.routing import Route

from views.main import index, migrate_route
from views.cards import user_card, collection_card, bingo_card


app = Starlette(
    routes=[
        Route("/", index),
        Route("/migrate", migrate_route),
        Route("/user/{user_id:str}", user_card),
        Route("/collection/{collection_id:int}", collection_card),
        Route("/bingo/{user_id:int}", bingo_card)
    ]
)
