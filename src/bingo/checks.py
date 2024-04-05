from shikithon import ShikimoriAPI
from shikithon.models import (
    History,
    AnimeInfo,
    MangaInfo,
    RanobeInfo,
    Anime,
    Manga,
    Ranobe,
    Relation
)
from cashews import cache

from dataclasses import dataclass
from typing import List, Union

from .base_check import Check, FuncCheck
from .type_hints import ProductType


cache.setup("mem://", size=100)


def get_product_type(
    product: Union[AnimeInfo, MangaInfo, RanobeInfo]
) -> ProductType:
    if isinstance(product, AnimeInfo):
        return "anime"
    elif isinstance(product, MangaInfo):
        return "manga"
    elif isinstance(product, RanobeInfo):
        return "ranobe"
    else:
        raise Exception("Unknown type")


@cache(ttl="25m", key="product_info-{product_type}-{product_id}")
async def get_product_info(
    api: ShikimoriAPI,
    product_type: ProductType,
    product_id: int
) -> Union[Anime, Manga, Ranobe]:
    if product_type == "anime":
        data = await api.animes.get(product_id)
    elif product_type == "manga":
        data = await api.mangas.get(product_id)
    elif product_type == "ranobe":
        data = await api.ranobes.get(product_id)
    if data is None:
        raise Exception("Product data cannot be None")
    return data


@cache(ttl="25m", key="product_related-{product_type}-{product_id}")
async def get_product_related(
    api: ShikimoriAPI,
    product_type: ProductType,
    product_id: int
) -> List[Relation]:
    if product_type == "anime":
        data = await api.animes.related(product_id)
    elif product_type == "manga":
        data = await api.mangas.related(product_id)
    elif product_type == "ranobe":
        data = await api.ranobes.related(product_id)
    return data


WatchedAnimeCheck = FuncCheck(lambda h: (
    (h.description == "Просмотрено" or h.description.startswith("Просмотрено и оценено")) and
    h.target.url.startswith("/animes")
))


ReadMangaRanobeCheck = FuncCheck(lambda h: (
    (h.description == "Прочитано" or h.description.startswith("Прочитано и оценено")) and
    (h.target.url.startswith("/mangas") or h.target.url.startswith("/ranobe"))
))


class GenresCheck(Check):
    def __init__(self, genres: Union[str, List[str]]) -> None:
        if isinstance(genres, str):
            genres = [genres]
        self._genres = genres

    async def check(self, api: ShikimoriAPI, history: History) -> bool:
        if history.target is None:
            return False
        product_type = get_product_type(history.target)
        data = await get_product_info(api, product_type, history.target.id)

        genres = [g.russian for g in data.genres]
        if len(genres) == 0:
            return False
        return any([i in genres for i in self._genres])


class PlannedMoreCompletedCheck(Check):
    async def check(self, api: ShikimoriAPI, history: History) -> bool:
        if history.target is None:
            return False
        product_type = get_product_type(history.target)
        data = await get_product_info(api, product_type, history.target.id)
        return data.rates_statuses_stats[0].value > data.rates_statuses_stats[1].value


class CompletedLessNUsersCheck(Check):
    def __init__(self, n: int) -> None:
        self._n = n

    async def check(self, api: ShikimoriAPI, history: History) -> bool:
        if history.target is None:
            return False
        product_type = get_product_type(history.target)
        data = await get_product_info(api, product_type, history.target.id)
        return data.rates_statuses_stats[1].value < self._n


class AddListLessNUsersCheck(Check):
    def __init__(self, n: int) -> None:
        self._n = n

    async def check(self, api: ShikimoriAPI, history: History) -> bool:
        if history.target is None:
            return False
        product_type = get_product_type(history.target)
        data = await get_product_info(api, product_type, history.target.id)
        return sum([r.value for r in data.rates_statuses_stats]) < self._n


class StudiosNumMoreNCheck(Check):
    def __init__(self, n: int) -> None:
        self._n = n
    
    async def check(self, api: ShikimoriAPI, history: History) -> bool:
        if history.target is None:
            return False
        product_type = get_product_type(history.target)
        if product_type != "anime":
            return False
        data = await get_product_info(api, product_type, history.target.id)
        return len(data.studios) > self._n


class AnimeAdaptationCheck(Check):
    def __init__(self, kind: Union[str, List[str]]) -> None:
        if isinstance(kind, str):
            kind = [kind]
        self._kind = kind

    async def check(self, api: ShikimoriAPI, history: History) -> bool:
        if history.target is None:
            return False
        product_type = get_product_type(history.target)
        if product_type != "anime":
            return False
        data = await get_product_related(api, product_type, history.target.id)
        for rel in data:
            if (
                rel.relation == "Adaptation" and
                rel.manga is not None and
                any([rel.manga.kind == k for k in self._kind])
            ):
                return True
        return False


@dataclass(frozen=True)
class BingoTask:
    description: str
    check: Check
    weight: float
    products: List[ProductType]


BINGO_TASKS = [
    BingoTask("Посмотри любое аниме.", WatchedAnimeCheck, 1, ["anime"]),
    BingoTask("Прочитай любую мангу / ранобэ.", ReadMangaRanobeCheck, 1, ["manga", "ranobe"]),
    BingoTask("Посмотри фильм.", WatchedAnimeCheck & FuncCheck(lambda h: h.target.kind == "movie"), 0.5, ["anime"]),
    BingoTask("Посмотри OVA / ONA.", WatchedAnimeCheck & FuncCheck(lambda h: h.target.kind in ["ova", "ona"]), 0.5, ["anime"]),
    BingoTask("Посмотри аниме, основанное на манге.", WatchedAnimeCheck & AnimeAdaptationCheck("manga"), 0.5, ["anime"]),
    BingoTask("Посмотри аниме с оценкой 8 и выше.", WatchedAnimeCheck & FuncCheck(lambda h: h.target.score >= 8), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ с оценкой 8 и выше.", ReadMangaRanobeCheck & FuncCheck(lambda h: h.target.score >= 8), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме с оценкой 6 и ниже.", WatchedAnimeCheck & FuncCheck(lambda h: h.target.score <= 6), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ с оценкой 6 и ниже.", ReadMangaRanobeCheck & FuncCheck(lambda h: h.target.score <= 6), 0.3, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме, которое началось в 80-ых и раньше.", WatchedAnimeCheck & FuncCheck(lambda h: h.target.aired_on.year < 1990), 0.1, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ, которое началось в 80-ых и раньше.", ReadMangaRanobeCheck & FuncCheck(lambda h: h.target.aired_on.year < 1990), 0.1, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме, которое началось в 90-ых.", WatchedAnimeCheck & FuncCheck(lambda h: 1990 <= h.target.aired_on.year < 2000), 0.1, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ, которое началось в 90-ых.", ReadMangaRanobeCheck & FuncCheck(lambda h: 1990 <= h.target.aired_on.year < 2000), 0.1, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме, которое началось в 00-ых.", WatchedAnimeCheck & FuncCheck(lambda h: 2000 <= h.target.aired_on.year < 2010), 0.2, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ, которое началось в 00-ых.", ReadMangaRanobeCheck & FuncCheck(lambda h: 2000 <= h.target.aired_on.year < 2010), 0.2, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме, которое началось в 10-ых.", WatchedAnimeCheck & FuncCheck(lambda h: 2010 <= h.target.aired_on.year < 2020), 0.3, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ, которое началось в 10-ых.", ReadMangaRanobeCheck & FuncCheck(lambda h: 2010 <= h.target.aired_on.year < 2020), 0.3, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме, которое началось в 20-ых.", WatchedAnimeCheck & FuncCheck(lambda h: 2020 <= h.target.aired_on.year < 2030), 0.3, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ, которое началось в 20-ых.", ReadMangaRanobeCheck & FuncCheck(lambda h: 2020 <= h.target.aired_on.year < 2030), 0.3, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме в жанре комедия.", WatchedAnimeCheck & GenresCheck("Комедия"), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ в жанре комедия.", ReadMangaRanobeCheck & GenresCheck("Комедия"), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме в жанре драма / романтика.", WatchedAnimeCheck & GenresCheck(["Драма", "Романтика"]), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ в жанре драма / романтика.", ReadMangaRanobeCheck & GenresCheck(["Драма", "Романтика"]), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме про повседневность / кулинарию.", WatchedAnimeCheck & GenresCheck(["Повседневность", "Гурман"]), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ про повседневность / кулинарию.", ReadMangaRanobeCheck & GenresCheck(["Повседневность", "Гурман"]), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме в жанре ужасы / триллер.", WatchedAnimeCheck & GenresCheck(["Ужасы", "Триллер"]), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ в жанре ужасы / триллер.", ReadMangaRanobeCheck & GenresCheck(["Ужасы", "Триллер"]), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме в жанре сверхъестественное / фэнтези / фантастика.", WatchedAnimeCheck & GenresCheck(["Сверхъестественное", "Фэнтези", "Фантастика"]), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ в жанре сверхъестественное / фэнтези / фантастика.", ReadMangaRanobeCheck & GenresCheck(["Сверхъестественное", "Фэнтези", "Фантастика"]), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме в жанре тайна.", WatchedAnimeCheck & GenresCheck(["Тайна"]), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ в жанре тайна.", ReadMangaRanobeCheck & GenresCheck(["Тайна"]), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме про спорт.", WatchedAnimeCheck & GenresCheck(["Спорт"]), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ про спорт.", ReadMangaRanobeCheck & GenresCheck(["Спорт"]), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме в жанре экшен / приключения.", WatchedAnimeCheck & GenresCheck(["Экшен", "Приключения"]), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ в жанре экшен / приключения.", ReadMangaRanobeCheck & GenresCheck(["Экшен", "Приключения"]), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме в жанре авангард.", WatchedAnimeCheck & GenresCheck(["Авангард"]), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ в жанре авангард.", ReadMangaRanobeCheck & GenresCheck(["Авангард"]), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме с цифрой в названии.", WatchedAnimeCheck & FuncCheck(lambda h: len(list(filter(str.isdigit, h.target.russian))) > 0), 0.3, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ с цифрой в названии.", ReadMangaRanobeCheck & FuncCheck(lambda h: len(list(filter(str.isdigit, h.target.russian))) > 0), 0.3, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме, в котором меньше 30 серий.", WatchedAnimeCheck & FuncCheck(lambda h: max(h.target.episodes, h.target.episodes_aired) < 30), 0.5, ["anime"]),
    BingoTask("Посмотри аниме, в котором 30 серий и больше.", WatchedAnimeCheck & FuncCheck(lambda h: max(h.target.episodes, h.target.episodes_aired) >= 30), 0.5, ["anime"]),
    BingoTask("Посмотри аниме от нескольких студий.", WatchedAnimeCheck & StudiosNumMoreNCheck(1), 0.3, ["anime"]),
    BingoTask("Начни смотреть аниме в онгоинге.", FuncCheck(lambda h: h.target.status == "ongoing" and (h.description == "Смотрю" or "эпизод" in h.description)), 0.3, ["anime"]),
    BingoTask("Посмотри аниме, которое больше в запланированом, чем просмотреном.", WatchedAnimeCheck & PlannedMoreCompletedCheck(), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ, которое больше в запланированом, чем прочитаном.", ReadMangaRanobeCheck & PlannedMoreCompletedCheck(), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме, которое посмотрело меньше 10000 пользователей.", WatchedAnimeCheck & CompletedLessNUsersCheck(10000), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ, которое прочитало меньше 1000 пользователей.", ReadMangaRanobeCheck & CompletedLessNUsersCheck(1000), 0.5, ["manga", "ranobe"]),
    BingoTask("Посмотри аниме, которое добавили в список меньше 50000 пользователей.", WatchedAnimeCheck & AddListLessNUsersCheck(50000), 0.5, ["anime"]),
    BingoTask("Прочитай мангу / ранобэ, которое добавили в список меньше 10000 пользователей.", ReadMangaRanobeCheck & AddListLessNUsersCheck(10000), 0.5, ["manga", "ranobe"]),
]
