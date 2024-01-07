from flask import g
from jinja2 import Environment, FileSystemLoader
from hyphen import Hyphenator

import math
from textwrap import shorten
from re import search
from typing import Optional, List


HYPHENATOR = Hyphenator("ru_RU", directory="pyhyphen")

LETTER_WIDTHS = {
    ' ': 0.27783, '!': 0.27783, '"': 0.355, '#': 0.55617, '$': 0.55617, '%': 0.88917, '&': 0.667,
    "'": 0.191, '(': 0.333, ')': 0.333, '*': 0.38917, '+': 0.584, ',': 0.27783, '-': 0.333,
    '.': 0.27783, '/': 0.27783, '0': 0.55617, '1': 0.55617, '2': 0.55617, '3': 0.55617,
    '4': 0.55617, '5': 0.55617, '6': 0.55617, '7': 0.55617, '8': 0.55617, '9': 0.55617, ':': 0.27783,
    ';': 0.27783, '<': 0.584, '=': 0.584, '>': 0.584, '?': 0.55617, '@': 1.01517, 'A': 0.667,
    'B': 0.667, 'C': 0.72217, 'D': 0.72217, 'E': 0.667, 'F': 0.61083, 'G': 0.77783, 'H': 0.72217,
    'I': 0.27783, 'J': 0.5, 'K': 0.667, 'L': 0.55617, 'M': 0.833, 'N': 0.72217, 'O': 0.77783,
    'P': 0.667, 'Q': 0.77783, 'R': 0.72217, 'S': 0.667, 'T': 0.61083, 'U': 0.72217, 'V': 0.667,
    'W': 0.94383, 'X': 0.667, 'Y': 0.667, 'Z': 0.61083, '[': 0.27783, '\\': 0.27783, ']': 0.27783,
    '^': 0.46917, '_': 0.55617, '`': 0.333, 'a': 0.55617, 'b': 0.55617, 'c': 0.5, 'd': 0.55617,
    'e': 0.55617, 'f': 0.27783, 'g': 0.55617, 'h': 0.55617, 'i': 0.22217, 'j': 0.22217, 'k': 0.5,
    'l': 0.22217, 'm': 0.833, 'n': 0.55617, 'o': 0.55617, 'p': 0.55617, 'q': 0.55617, 'r': 0.333,
    's': 0.5, 't': 0.27783, 'u': 0.55617, 'v': 0.5, 'w': 0.72217, 'x': 0.5, 'y': 0.5, 'z': 0.5,
    '{': 0.334, '|': 0.25983, '}': 0.334, '~': 0.584, '_median': 0.55617
}
KERN_MODS = {
    '11': -0.07367, 'AT': -0.07366, 'AV': -0.07367, 'AW': -0.03666, 'AY': -0.07367, 'Av': -0.01767,
    'Aw': -0.01767, 'Ay': -0.01767, 'F,': -0.11083, 'F.': -0.11083, 'FA': -0.05466, 'LT': -0.07367,
    'LV': -0.07367, 'LW': -0.07367, 'LY': -0.07367, 'Ly': -0.03667, 'P,': -0.129, 'P.': -0.129,
    'PA': -0.07367, 'RT': -0.01767, 'RV': -0.01767, 'RW': -0.01767, 'RY': -0.01767, 'T,': -0.11083,
    'T-': -0.05466, 'T.': -0.11083, 'T:': -0.11083, 'T;': -0.11083, 'TA': -0.07366, 'TO': -0.01766,
    'Ta': -0.11083, 'Tc': -0.11083, 'Te': -0.11083, 'Ti': -0.03667, 'To': -0.11083, 'Tr': -0.03666,
    'Ts': -0.11083, 'Tu': -0.03667, 'Tw': -0.05467, 'Ty': -0.05466, 'V,': -0.09166, 'V-': -0.05467,
    'V.': -0.09166, 'V:': -0.03666, 'V;': -0.03666, 'VA': -0.07367, 'Va': -0.07367, 'Ve': -0.05467,
    'Vi': -0.01767, 'Vo': -0.05467, 'Vr': -0.03667, 'Vu': -0.03667, 'Vy': -0.03667, 'W,': -0.05466,
    'W-': -0.01766, 'W.': -0.05466, 'W:': -0.01766, 'W;': -0.01766, 'WA': -0.03666, 'Wa': -0.03667,
    'We': -0.01767, 'Wo': -0.01767, 'Wr': -0.01766, 'Wu': -0.01767, 'Wy': -0.00866, 'Y,': -0.129,
    'Y-': -0.09167, 'Y.': -0.129, 'Y:': -0.05466, 'Y;': -0.065, 'YA': -0.07367, 'Ya': -0.07367,
    'Ye': -0.09167, 'Yi': -0.03667, 'Yo': -0.09167, 'Yp': -0.07367, 'Yq': -0.09167, 'Yu': -0.05467,
    'Yv': -0.05467, 'ff': -0.01766, 'r,': -0.05466, 'r.': -0.05466, 'v,': -0.07366, 'v.': -0.07366,
    'w,': -0.05467, 'w.': -0.05467, 'y,': -0.07366, 'y.': -0.07366
}


def get_jinja_env() -> Environment:
    try:
        return g.jinja_env
    except AttributeError:
        env = g.jinja_env = Environment(
            trim_blocks=True,
            loader=FileSystemLoader("src/cards/"),
            auto_reload=False
        )
        return env


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
    if value in ["true", "t", "1"]:
        return True
    elif value in ["false", "f", "0"]:
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


def wrap_text_multiline(
    text: str,
    width: int,
    font_size: int = 10,
    max_lines: int = 3
) -> List[str]:
    sep_width = LETTER_WIDTHS[" "] * font_size
    hyphen_width = LETTER_WIDTHS["-"] * font_size

    lines: List[str] = []

    line = ""
    line_width = 0
    for word in text.split():
        word_width = measure_text(word, font_size)
        if line_width == 0:
            line += word
            line_width += word_width
            continue
        elif line_width + sep_width + word_width <= width:
            line += " " + word
            line_width += word_width + sep_width
            continue

        syllables = HYPHENATOR.syllables(word)
        if len(syllables) > 0:
            first_part = ""
            first_part_width = 0
            syllable_i = 0
            for syllable in syllables[:-1]:
                syllable_width = measure_text(syllable, font_size)
                if sep_width + first_part_width + syllable_width + hyphen_width <= width - line_width:
                    first_part += syllable
                    first_part_width += syllable_width
                else:
                    break
                syllable_i += 1

            if first_part_width > 0:
                line += f" {first_part}-"
                line_width += sep_width + first_part_width + hyphen_width
                lines.append(line)
                second_part = "".join(syllables[syllable_i:])
                line = second_part
                line_width = measure_text(second_part, font_size)
                continue
            
        lines.append(line)
        line = word
        line_width = word_width

    if line_width > 0:
        lines.append(line)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last_line = lines.pop(-1)
        lines.append(shorten(
            text=last_line,
            width=len(last_line) - 1,
            placeholder=" ..."
        ))

    return lines


def measure_text(text: str, font_size: int = 10) -> float:
    """https://chrishewett.com/blog/calculating-text-width-programmatically/?"""
    width = 0
    for idx, c in enumerate(list(text)):
        width += LETTER_WIDTHS.get(c) or LETTER_WIDTHS.get("_median")
        if idx != len(text) - 1:
            width += KERN_MODS.get(f"{c}{text[idx + 1]}") or 0
    return width * font_size
