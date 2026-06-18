# Узбекский (основной язык интерфейса)
UZ: dict[str, str] = {
    # Общие
    "start": (
        "Assalomu alaykum! 👋\n\n"
        "«Bordi Keldi Korea» — Oʻzbekiston ↔ Koreya yoʻnalishida hamroh topish boti.\n\n"
        "Quyidagi menyudan kerakli boʻlimni tanlang."
    ),
    "choose_lang": "Tilni tanlang / Выберите язык:",
    "lang_set": "Til oʻrnatildi ✅",
    "main_menu": "Asosiy menyu:",
    "cancelled": "Bekor qilindi.",
    "banned": "Siz bloklangansiz va botdan foydalana olmaysiz.",
    "unknown": "Tushunmadim. Menyudagi tugmalardan foydalaning.",
    "back": "⬅️ Orqaga",
    "cancel": "❌ Bekor qilish",
    "skip": "Oʻtkazib yuborish ▶️",
    # Главное меню (reply-кнопки)
    "btn_post": "➕ Eʼlon berish",
    "btn_search": "🔍 Qidirish",
    "btn_subscribe": "🔔 Yangi eʼlonlar",
    "btn_my_trips": "📋 Mening eʼlonlarim",
    "btn_lang": "🌐 Til",
    # Направления
    "dir_uz_kr": "🇺🇿 → 🇰🇷 Oʻzbekiston → Koreya",
    "dir_kr_uz": "🇰🇷 → 🇺🇿 Koreya → Oʻzbekiston",
    # Дисклеймер
    "disclaimer": (
        "⚠️ <b>Muhim ogohlantirish</b>\n\n"
        "Notanish odamlardan yopiq yoki begona paketlarni koʻrmasdan qabul qilmang. "
        "Yuk tarkibini albatta tekshiring. Bot faqat odamlarni <b>bogʻlaydi</b> va "
        "tashuvchi yoki vositachi emas. Yuk uchun javobgarlik taraflar zimmasida.\n\n"
        "Davom etish uchun «Roziman» tugmasini bosing."
    ),
    "disclaimer_accept": "✅ Roziman, davom etish",
    # Подача объявления
    "post_direction": "Yoʻnalishni tanlang:",
    "post_from_city": "Qaysi shahardan uchasiz?",
    "post_to_city": "Qaysi shaharga uchasiz?",
    "post_city_manual": "✍️ Qoʻlda kiritish",
    "post_city_manual_prompt": "Shahar nomini yozing:",
    "post_date": (
        "Uchish sanasini kiriting.\n"
        "Format: <code>KK.OO.YYYY</code>, <code>KK.OO.YY</code> yoki <code>KK.OO</code>\n"
        "Masalan: <code>25.06.2026</code>"
    ),
    "post_date_pick": "📅 Kalendardan sanani tanlang yoki yuqoridagi formatda yozing:",
    "post_date_invalid": "Sana notoʻgʻri. Namuna: <code>25.06.2026</code>",
    "post_date_past": "Sana oʻtmishda boʻlishi mumkin emas. Boshqa sana kiriting.",
    "post_baggage": (
        "Qancha boʻsh joy bera olasiz?\n"
        "Tugmani tanlang yoki qoʻlda yozing (masalan <code>23+23</code>):"
    ),
    "baggage_negotiable": "Kelishuv asosida",
    "baggage_custom_btn": "✍️ Oʻzim yozaman",
    "baggage_custom_prompt": "Qancha boʻsh joy bera olishingizni yozing (masalan <code>23+23</code>):",
    "post_cargo": "Nimani olib keta olasiz?\n(bir nechtasini tanlash yoki oʻzingiznikini qoʻshish mumkin)",
    "cargo_documents": "📄 Hujjatlar",
    "cargo_cosmetics": "💄 Kosmetika",
    "cargo_clothes": "👕 Kiyim va buyumlar",
    "cargo_any": "📦 Farqi yoʻq",
    "cargo_add_custom": "✍️ Oʻzim qoʻshaman",
    "cargo_done": "✅ Tayyor",
    "cargo_custom_prompt": "Nimani olib ketishingizni yozing:",
    "cargo_empty": "Kamida bittasini tanlang.",
    "post_contact": (
        "Bogʻlanish uchun telefon yoki @username yozing (ixtiyoriy).\n"
        "Tugma orqali raqam yuborishingiz yoki oʻtkazib yuborishingiz mumkin — "
        "siz bilan Telegram orqali bogʻlanishadi."
    ),
    "post_contact_share": "📱 Raqamni yuborish",
    "post_comment": "Izoh qoldirasizmi? (ixtiyoriy)\nMatn yozing yoki oʻtkazib yuboring.",
    "post_confirm": "Eʼlon tayyor. Tasdiqlaysizmi?",
    "confirm_yes": "✅ Tasdiqlash",
    "post_saved": "✅ Eʼloningiz joylandi va obunachilarga yuborildi!",
    # Карточка объявления
    "card_title": "✈️ <b>{from_city} → {to_city}</b>",
    "card_date": "📅 Sana: <b>{date}</b>",
    "card_baggage": "🧳 Boʻsh joy: {baggage}",
    "card_cargo": "📦 Oladi: {cargo}",
    "card_comment": "💬 {comment}",
    "card_contact": "📞 Aloqa: {contact}",
    "card_username": "👤 Telegram: @{username}",
    "btn_contact": "📞 Bogʻlanish",
    "new_match": "🔔 Yoʻnalishingiz boʻyicha yangi eʼlon:",
    # Поиск
    "search_direction": "Qaysi yoʻnalish boʻyicha qidiramiz?",
    "search_date": (
        "Sanani kiriting (masalan <code>25.06</code>) "
        "yoki barcha eʼlonlar uchun <b>hammasi</b> deb yozing."
    ),
    "search_all_word": "hammasi",
    "search_all_btn": "📋 Hammasini koʻrsatish",
    "search_empty": (
        "Hech narsa topilmadi 😔\n"
        "Mos eʼlon paydo boʻlsa darhol xabar berishimiz uchun obuna boʻling."
    ),
    "search_subscribe_offer": "🔔 Shu yoʻnalish boʻyicha yangi eʼlonlarni olish",
    "search_results": "Topildi: {count} ta eʼlon",
    # Подписки
    "sub_direction": "Qaysi yoʻnalish boʻyicha yangi eʼlonlarni yuborib turaylik?",
    "sub_added": "✅ Boʻldi! Shu yoʻnalish boʻyicha yangi eʼlonlar chiqsa, darhol yuboramiz.",
    "sub_exists": "Siz bu yoʻnalish boʻyicha yangi eʼlonlarni allaqachon olyapsiz.",
    "sub_list_title": "Siz quyidagi yoʻnalishlar boʻyicha yangi eʼlonlarni olasiz:",
    "sub_empty": "Hali birorta yoʻnalish tanlanmagan.",
    "sub_remove": "🗑 Oʻchirish",
    "sub_removed": "Oʻchirildi.",
    # Мои объявления
    "my_empty": "Sizda faol eʼlon yoʻq.",
    "my_title": "Sizning faol eʼlonlaringiz:",
    "my_delete": "🗑 Oʻchirish",
    "my_deleted": "Eʼlon oʻchirildi.",
    # Админ
    "admin_only": "Bu buyruq faqat administratorlar uchun.",
    "admin_banned": "Foydalanuvchi {uid} bloklandi.",
    "admin_unbanned": "Foydalanuvchi {uid} blokdan chiqarildi.",
    "admin_trip_deleted": "Eʼlon {tid} oʻchirildi.",
    "admin_not_found": "Topilmadi.",
    "admin_stats": (
        "📊 <b>Statistika</b>\n"
        "Foydalanuvchilar: {users}\n"
        "Faol eʼlonlar: {active_trips}\n"
        "Jami eʼlonlar: {total_trips}\n"
        "Obunalar: {subs}"
    ),
    "admin_usage": (
        "Admin buyruqlari:\n"
        "/ban <id> — bloklash\n"
        "/unban <id> — blokdan chiqarish\n"
        "/del <trip_id> — eʼlonni oʻchirish\n"
        "/stats — statistika"
    ),
}
