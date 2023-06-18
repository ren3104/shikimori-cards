from re import search
from hyphen import Hyphenator
from hyphen.textwrap2 import wrap
from typing import Optional, List


HYPHENATOR = Hyphenator("ru_RU", directory="pyhyphen")


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


def k_formatter(value: int) -> str:
    if value > 999:
        return f"{round(value / 1000, 1)}к"
    return str(value)


def wrap_text_multiline(text: str, width: int = 59, max_lines: int = 3) -> List[str]:
    placeholder = " [...]"
    wrapped = wrap(
        text=text,
        width=width,
        max_lines=max_lines,
        placeholder=placeholder,
        use_hyphenator=HYPHENATOR
    )
    if wrapped[-1].endswith(placeholder):
        wrapped[-1] = wrapped[-1][:-(len(placeholder) + 3)] + "..."
    return wrapped


def measure_text(text: str, font_size: int = 10) -> float:
    return len(text) * 0.6 * font_size
