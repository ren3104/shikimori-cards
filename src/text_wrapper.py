from hyphen import Hyphenator

from textwrap import TextWrapper
from typing import Optional, List


HYPHENATOR = Hyphenator("ru_RU", directory="pyhyphen")

# Sans-Serif font
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


class PixelTextWrapper(TextWrapper):
    def __init__(
        self,
        *args,
        font_size: int = 12,
        use_hyphenator: Optional[Hyphenator] = None,
        **kwargs
    ):
        self.font_size = font_size
        self.use_hyphenator = use_hyphenator
        super().__init__(*args, **kwargs)

    def _handle_long_word(self, reversed_chunks, cur_line, cur_width, width):
        if width < 1 * self.font_size:
            space_left = 1 * self.font_size
        else:
            space_left = width - cur_width

        if self.break_long_words:
            end = int(space_left // self.font_size)
            chunk = reversed_chunks[-1]
            if self.break_on_hyphens and measure_text(chunk, self.font_size) > space_left:
                hyphen = chunk.rfind('-', 0, int(space_left // self.font_size))
                if hyphen > 0 and any(c != '-' for c in chunk[:hyphen]):
                    end = hyphen + 1
            cur_line.append(chunk[:end])
            reversed_chunks[-1] = chunk[end:]
        elif not cur_line:
            cur_line.append(reversed_chunks.pop())

    def _wrap_chunks(self, chunks):
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)
        if self.max_lines is not None:
            if self.max_lines > 1:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent
            if measure_text(indent + self.placeholder.lstrip(), self.font_size) > self.width:
                raise ValueError("placeholder too large for max width")

        chunks.reverse()

        while chunks:
            cur_line = []
            cur_width = 0
            hyphenated_last = False

            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            width = self.width - measure_text(indent, self.font_size)

            if self.drop_whitespace and chunks[-1].strip() == '' and lines:
                del chunks[-1]

            while chunks:
                w = measure_text(chunks[-1], self.font_size)

                if cur_width + w <= width:
                    cur_line.append(chunks.pop())
                    cur_width += w
                else:
                    if self.use_hyphenator and (width - cur_width >= 2 * self.font_size):
                        hyphen = "-"
                        hyphen_width = measure_text(hyphen, self.font_size)
                        word_pairs = self.use_hyphenator.pairs(chunks[-1])
                        max_word_width = width - cur_width - hyphen_width
                        while word_pairs:
                            if word_pairs[-1][0].endswith(hyphen):
                                cur_max_width = max_word_width - hyphen_width
                            else:
                                cur_max_width = max_word_width
                            if measure_text(word_pairs[-1][0], self.font_size) > cur_max_width:
                                word_pairs.pop()
                            else:
                                break
                        if word_pairs:
                            if round(cur_max_width) == round(max_word_width):
                                word_pairs[-1][0] += hyphen
                            hyphenated_chunk = word_pairs[-1]
                        else:
                            hyphenated_chunk = []
                        if hyphenated_chunk:
                            cur_line.append(hyphenated_chunk[0])
                            chunks[-1] = hyphenated_chunk[1]
                            hyphenated_last = True
                    break

            if chunks and measure_text(chunks[-1], self.font_size) > width and not hyphenated_last:
                self._handle_long_word(chunks, cur_line, cur_width, width)
                cur_width= sum([measure_text(i, self.font_size) for i in cur_line])

            if self.drop_whitespace and cur_line and cur_line[-1].strip() == '':
                cur_width -= measure_text(cur_line[-1], self.font_size)
                del cur_line[-1]

            if cur_line:
                if (self.max_lines is None or
                    len(lines) + 1 < self.max_lines or
                    (not chunks or
                     self.drop_whitespace and
                     len(chunks) == 1 and
                     not chunks[0].strip()) and cur_width <= width):
                    
                    lines.append(indent + ''.join(cur_line))
                else:
                    while cur_line:
                        if (cur_line[-1].strip() and
                            cur_width + measure_text(self.placeholder, self.font_size) <= width):
                            cur_line.append(self.placeholder)
                            lines.append(indent + ''.join(cur_line))
                            break
                        cur_width -= measure_text(cur_line[-1], self.font_size)
                        del cur_line[-1]
                    else:
                        if lines:
                            prev_line = lines[-1].rstrip()
                            if measure_text(prev_line + self.placeholder, self.font_size) <= self.width:
                                lines[-1] = prev_line + self.placeholder
                                break
                        lines.append(indent + self.placeholder.lstrip())
                    break

        return lines
    

def wrap_text_multiline(
    text: str,
    width: int,
    font_size: int = 10,
    max_lines: int = 3
) -> List[str]:
    return PixelTextWrapper(
        width=width,
        font_size=font_size,
        use_hyphenator=HYPHENATOR,
        max_lines=max_lines,
        placeholder=" ..."
    ).wrap(text)


def measure_text(text: str, font_size: int = 10) -> float:
    """https://chrishewett.com/blog/calculating-text-width-programmatically/?"""
    width = 0
    for idx, c in enumerate(list(text)):
        width += LETTER_WIDTHS.get(c) or LETTER_WIDTHS.get("_median")
        if idx != len(text) - 1:
            width += KERN_MODS.get(f"{c}{text[idx + 1]}") or 0
    return width * font_size
