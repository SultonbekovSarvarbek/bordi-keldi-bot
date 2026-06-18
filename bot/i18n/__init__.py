from __future__ import annotations

from bot.i18n.ru import RU
from bot.i18n.uz import UZ

TRANSLATIONS: dict[str, dict[str, str]] = {"uz": UZ, "ru": RU}

DEFAULT_LANG = "uz"


def t(key: str, lang: str | None = None, /, **kwargs: object) -> str:
    """Вернуть перевод по ключу.

    Если строки нет в выбранном языке — фолбэк на узбекский, затем на сам ключ.
    Поддерживает подстановку через str.format(**kwargs).
    """
    lang = lang if lang in TRANSLATIONS else DEFAULT_LANG
    text = TRANSLATIONS[lang].get(key) or TRANSLATIONS[DEFAULT_LANG].get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
