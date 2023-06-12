from dataclasses import dataclass


@dataclass(frozen=True)
class CardOptions:
    bg_color: str = "#fcfcfc"
    border_color: str = "#ddd"
    border_radius: int = 0
    font: str = "sans-serif"
    title_color: str = "#123"
    text_color: str = "#333"
    # user card
    avatar_round: bool = False
    stat_color: str = "#7b8084"
    bar_back_color: str = "#ccc"
    bar_color: str = "#4c86c8"
    bar_round: bool = False


themes = {
    "default": CardOptions(), # Shikimori style
    "shiki-theme": CardOptions(
        bg_color="#0000",
        border_color="var(--color-border, #dcdcdc)",
        border_radius=3,
        font="var(--font-main, 'Arial', sans-serif)",
        title_color="var(--color-text-primary, #212121)",
        text_color="var(--color-text-primary, #212121)",
        avatar_round=True,
        stat_color="var(--color-text-hint, #737373)",
        bar_back_color="var(--color-border, #dcdcdc)",
        bar_color="var(--color-primary, #009688)",
        bar_round=True
    )
}
