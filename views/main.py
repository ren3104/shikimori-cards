from starlette.requests import Request
from starlette.responses import Response, RedirectResponse


async def index(_: Request) -> Response:
    return RedirectResponse("https://github.com/ren3104/shikimori-cards")
