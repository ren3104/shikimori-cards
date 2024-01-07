from dataclasses import dataclass


@dataclass(frozen=True)
class CardOptions:
    bg_color: str = "#fff" # цвет фона tooltip
    border_color: str = "#999" # цвет границы tooltip
    border_radius: int = 0 # радиус границы tooltip
    title_color: str = "#123" # --headline-color
    text_color: str = "#333" # цвет текста tooltip
    icon_color: str = "#444" # цвет иконок, например под аватаркой в профиле
    bar_color: str = "#79a9cf" # цвет заполнения полоски в опросе
    bar_back_color: str = "#eef0f3" # цвет полоски в опросе
    bar_round: bool = False
    show_icons: bool = True
    animated: bool = True


themes = {
    "default": CardOptions(), # Shikimori style
    "shiki-theme": CardOptions(
        bg_color="#fff",
        border_color="#e0e0e0",
        border_radius=2,
        title_color="#212121",
        text_color="#212121",
        icon_color="#757575",
        bar_color="#4682B4",
        bar_back_color="#e0e0e0",
        bar_round=True
    ),
}
