from __future__ import annotations

# Канонические ключи "что готов взять" (хранятся в БД, рендерятся через i18n).
# Порядок = порядок кнопок: Kiyim-kechak, Hujjatlar, Telefon, Noutbuk.
CARGO_KEYS = ["clothes", "documents", "phone", "laptop"]
CARGO_LABEL = {
    "clothes": "cargo_clothes",
    "documents": "cargo_documents",
    "phone": "cargo_phone",
    "laptop": "cargo_laptop",
    # Legacy-ключи: в кнопках не показываются, но старые объявления рендерятся.
    "cosmetics": "cargo_cosmetics",
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
