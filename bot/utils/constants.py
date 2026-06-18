from __future__ import annotations

# Канонические ключи "что готов взять" (хранятся в БД, рендерятся через i18n).
CARGO_KEYS = ["documents", "cosmetics", "clothes", "any"]
CARGO_LABEL = {
    "documents": "cargo_documents",
    "cosmetics": "cargo_cosmetics",
    "clothes": "cargo_clothes",
    "any": "cargo_any",
}

# Префикс для пользовательского пункта груза (свободный текст).
CARGO_CUSTOM_PREFIX = "custom:"
# Разделитель нескольких выбранных пунктов груза в БД, напр. "documents|cosmetics".
CARGO_SEP = "|"

# Пресеты багажа. "negotiable" рендерится через i18n, остальные — как есть.
BAGGAGE_PRESETS = ["23", "23+23", "23+23+23"]
BAGGAGE_NEGOTIABLE = "negotiable"

# Маркер ручного ввода города.
CITY_MANUAL = "__manual__"
