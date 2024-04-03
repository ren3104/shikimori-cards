from starlette.applications import Starlette
from starlette.routing import Route

from views.main import index
from views.cards import user_card, collection_card


app = Starlette(
    routes=[
        Route("/", index),
        Route("/user/{user_id:str}", user_card),
        Route("/collection/{collection_id:int}", collection_card)
    ]
)
