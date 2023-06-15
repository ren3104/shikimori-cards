<div align="center">
    <h1>Shikimori Cards</h1>
    <p>Динамически генерируемые карточки для Шикимори. Вдохновлено <a href="https://github.com/anuraghazra/github-readme-stats">github-readme-stats</a>.</p>
</div>

<img src="assets/user_card_555400.svg" alt="User card example">

## Как использовать
Скопируйте и вставьте это в своем `BBCode` контенте.

Замените `<user_id>` в ссылке ниже на ваш **никнейм** или `id` пользователя Шикимори.

> **Note**
> Регистр никнейма учитывается! Если есть пробелы в никнейме, то замените их `+`!

```
[url=https://github.com/ren3104/shikimori-cards]
[img no-zoom]https://shikimori-cards.vercel.app/user/<user_id>[/img]
[/url]
```

Без `BBCode`:

```
https://shikimori-cards.vercel.app/user/<user_id>
```

> **Note**
> Доступные ранги: S+ (топ 10%), S (топ 25%), A++ (топ 40%), A+ (топ 55%), A (топ 70%), B+ (топ 80%) и B (все).  Значения рассчитываются с использованием [кумулятивной функции распределения](https://ru.wikipedia.org/wiki/%D0%A4%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D1%8F_%D1%80%D0%B0%D1%81%D0%BF%D1%80%D0%B5%D0%B4%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F) используя списки аниме и манги, отношение оценок к спискам аниме и манги, рецензии, отзывы, коллекции, статьи, правки, комментарии. Реализацию можно посмотреть в [src/fetchers/user_fetcher.py (calculate_rank)](src/fetchers/user_fetcher.py).

## Готовые темы
| | | |
| :--: | :--: | :--: |
| `default` ![default][default] | `shiki-theme` ![shiki-theme][shiki-theme] | [Добавь свою тему][add-theme] |

[default]: https://shikimori-cards.vercel.app/user/555400?theme=default
[shiki-theme]: https://shikimori-cards.vercel.app/user/555400?theme=shiki-theme

[add-theme]: https://github.com/ren3104/shikimori-cards/blob/master/src/themes.py

## Настройка темы
Вы можете настроить внешний вид своей карты пользователя по своему усмотрению с помощью параметров запроса.

### Типы
- `string` - строка.
- `integer` - целое число.
- `boolean` - `true` | `false` | 1 | 0.
- `color` - цвет в формате `hex` **без** `#`. Прозрачность можно указать с помощью `hex8`.

### Параметры
- `theme` - (`string`) название темы. По умолчанию: `default`.
- `bg_color` - (`color`) цвет фона карточки.
- `border_color` - (`color`) цвет границы карточки.
- `border_radius` - (`integer`) скругление углов карточки.
- `font` - (`string`) шрифт текста.
- `title_color` - (`color`) цвет заголовка. (Никнейм)
- `text_color` - (`color`) основной цвет текста.
- `animate` - (`boolean`) плавное появление карточки.
- `avatar_round` - (`boolean`) круглая аватарка.
- `stat_color` - (`color`) цвет "ключа" статистики.
- `bar_back_color` - (`color`) цвет ранговой окружности.
- `bar_color` - (`color`) цвет заполнения ранговой окружности.
- `bar_round` - (`boolean`) круглые концы заполнения ранговой окружности.
- `show_icons` - (`boolean`) показывать иконки.

### Пример
```
https://shikimori-cards.vercel.app/user/<user_id>?bg_color=0000&avatar_round=true&bar_round=1
```