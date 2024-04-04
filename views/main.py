from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.responses import Response, PlainTextResponse, RedirectResponse

import os

from src.database import migrate


async def index(_: Request) -> Response:
    return RedirectResponse("https://github.com/ren3104/shikimori-cards")


async def migrate_route(request: Request) -> Response:
    secret = request.query_params.get("secret")
    if secret is None or secret != os.environ.get("SHIKIMORI_CARDS_SECRET", "4ever"):
        raise HTTPException(403)
    
    await migrate()
    return PlainTextResponse("ok")
