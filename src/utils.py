from re import search
from typing import Optional


def parse_integer(value: str) -> Optional[int]:
    try:
        return int(value)
    except ValueError:
        return None


def parse_boolean(value: str) -> Optional[bool]:
    value = value.lower()
    if value == "true" or value == "1":
        return True
    elif value == "false" or value == "0":
        return False
    return None


def parse_hex_color(value: str) -> Optional[str]:
    if search(pattern="^([A-Fa-f0-9]{8}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}|[A-Fa-f0-9]{4})$",
              string=value):
        return "#" + value
    return None
