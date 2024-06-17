from starlette.responses import Response

import math
from textwrap import TextWrapper
from re import search
from email.utils import formatdate
from typing import Optional


def send_svg_file(
    svg_text: str,
    file_name: str,
    cache_seconds: int = 3600,
    swr_seconds: int = 43200
) -> Response:
    return Response(
        content=svg_text,
        headers={
            "Content-Disposition": f"inline; filename={file_name}",
            "Last-Modified": formatdate(usegmt=True), # current time gmt
            "Cache-Control": f"max-age={cache_seconds // 2}, s-maxage={cache_seconds}, stale-while-revalidate={swr_seconds}"
        },
        media_type="image/svg+xml"
    )


def calculate_ring_progress(value: int, radius: int = 50) -> int:
    # https://blog.logrocket.com/build-svg-circular-progress-component-react-hooks/
    arc_length = 2 * math.pi * radius
    arc_offset = (100 - value) / 100 * arc_length
    return int(arc_offset)


def parse_integer(value: str) -> Optional[int]:
    try:
        return int(value)
    except ValueError:
        return None


def parse_boolean(value: str) -> Optional[bool]:
    value = value.lower()
    if value in ("true", "t", "1"):
        return True
    elif value in ("false", "f", "0"):
        return False
    return None


def parse_hex_color(value: str) -> Optional[str]:
    if search(
        pattern="^([A-Fa-f0-9]{8}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}|[A-Fa-f0-9]{4})$",
        string=value
    ):
        return "#" + value
    return None


def k_formatter(value: int) -> str:
    if value > 999:
        return f"{round(value / 1000, 1)}к"
    return str(value)
