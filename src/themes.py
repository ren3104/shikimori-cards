from dataclasses import dataclass


@dataclass(frozen=True)
class CardOptions:
    bg_color: str = "#fcfcfc"
    border_color: str = "#ddd"
    border_radius: int = 0
    title_color: str = "#123"
    text_color: str = "#333"
    # user card
    avatar_round: bool = False
    stat_color: str = "#7b8084"
    bar_back_color: str = "#ccc"
    bar_color: str = "#4c86c8"
    bar_round: bool = False


themes = {
    "default": CardOptions() # Shikimori style
}
