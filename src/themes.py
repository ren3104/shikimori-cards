from dataclasses import dataclass


@dataclass(frozen=True)
class CardOptions:
    bg_color: str = "#fcfcfc"
    border_color: str = "#ddd"
    border_radius: int = 0
    title_color: str = "#123"
    text_color: str = "#333"
    animate: bool = False
    # user card
    avatar_round: bool = False
    icon_color: str = "#444"
    stat_color: str = "#7b8084"
    bar_back_color: str = "#ccc"
    bar_color: str = "#4c86c8"
    bar_round: bool = False
    show_icons: bool = False


themes = {
    "default": CardOptions(), # Shikimori style
    "shiki-theme": CardOptions(
        bg_color="#0000",
        border_color="var(--color-border, #e0e0e0)",
        border_radius=3,
        title_color="var(--color-text-primary, #212121)",
        text_color="var(--color-text-primary, #212121)",
        # user card
        avatar_round=True,
        icon_color="var(--color-text-hint, #737373)",
        stat_color="var(--color-text-hint, #737373)",
        bar_back_color="var(--color-border, #e0e0e0)",
        bar_color="var(--color-primary, #4682b4)",
        bar_round=True
    )
}
