# i18n.py
import gettext
import os
from typing import Dict

LOCALES_DIR = os.path.join(os.path.dirname(__file__), "locales")
DOMAIN = "messages"

# встроенные переводы (fallback — чтобы НЕ печатать ключи)
_FALLBACK: Dict[str, Dict[str, str]] = {
    "ru": {
        "pick_lang": "Выбери язык / Choose language / Dil seç:",
        "greet": "Привет! Я Stepup 🚀 Помогу выбрать направление в карьере.",
        "test": "🧭 Тест",
        "catalog": "🎯 Каталог",
        "courses": "📚 Курсы",
        "fav": "⭐ Избранное",
        "tip": "💡 Совет дня",
        "profile": "👤 Профиль",
        "back_menu": "⬅️ В меню",
        "choose_dir": "Выбери направление:",
        "choose_below": "Выбери пункт ниже:",
        "professions_for": "Профессии — ",
        "free_for": "Бесплатные курсы:",
        "added": "Добавлено в избранное ⭐",
        "removed": "Удалено из избранного",
        "profile_not_found": "Профиль не найден. Нажмите /start",
        "today_tip": "Сегодняшний совет:",
        "test_unavail": "Тест временно недоступен.",
        "question": "Вопрос",
        "itogi": "Итоги карьерного теста",
        "closest": "Твоё ближайшее направление:",
        "also": "Также близко:",
        "lang_title": "Выбери язык:",
        "lang_set": "Язык интерфейса: {lang}",
        "send_feedback": "Напиши сюда свой отзыв/вопрос одним сообщением — я передам его администраторам.",
        "feedback_sent": "Спасибо! Сообщение передано администраторам.",
        "help": (
            "Команды:\n"
            "/test — пройти карьерный тест\n"
            "/catalog — открыть каталог направлений\n"
            "/courses — подобрать бесплатные курсы\n"
            "/favorites — показать избранное\n"
            "/fav_courses — только избранные курсы\n"
            "/roles — список направлений\n"
            "/lang — сменить язык\n"
            "/profile — профиль\n"
            "/feedback — отправить отзыв"
        ),
        "id_label": "Ваш Telegram ID:",
        "reset_done": "Данные профиля и избранное очищены. Начнём заново — /start",

        "about": "Я Stepup — карьерный бот, который помогает примерить направления и подобрать бесплатные курсы.",
        "no_data": "Пока нет данных для этого запроса.",
        "fav_empty": "У тебя пока нет избранных профессий или курсов.",
        "courses_for": "Подбор курсов для направления: ",
        "profile_block": "Твой профиль:",
        "age_saved": "Возрастная группа",
        "skills_label": "Навыки:",
        "no_interest": "Сначала выбери направление в каталоге, чтобы я мог подобрать курсы.",
        "fav_header": "Твоё избранное:",
        "fav_courses_header": "Избранные курсы:",
        "fav_prof_header": "Избранные профессии:",
        "course_link": "Ссылка",
        "ok": "Ок",
    },
    "en": {
        "pick_lang": "Choose language:",
        "greet": "Hi! I’m Stepup 🚀 I’ll help you choose a career direction.",
        "test": "🧭 Test",
        "catalog": "🎯 Catalog",
        "courses": "📚 Courses",
        "fav": "⭐ Favorites",
        "tip": "💡 Daily tip",
        "profile": "👤 Profile",
        "back_menu": "⬅️ Back",
        "choose_dir": "Choose a direction:",
        "choose_below": "Choose an option below:",
        "professions_for": "Professions — ",
        "free_for": "Free courses:",
        "added": "Added to favorites ⭐",
        "removed": "Removed from favorites",
        "profile_not_found": "Profile not found. Press /start",
        "today_tip": "Today’s tip:",
        "test_unavail": "Test is temporarily unavailable.",
        "question": "Question",
        "itogi": "Test results",
        "closest": "Your closest track:",
        "also": "Also close:",
        "lang_title": "Choose language:",
        "lang_set": "Interface language: {lang}",
        "send_feedback": "Send your feedback in one message — I’ll forward it to admins.",
        "feedback_sent": "Thanks! Message forwarded to admins.",
        "help": (
            "Commands:\n"
            "/test — take the career test\n"
            "/catalog — open track catalog\n"
            "/courses — get free courses\n"
            "/favorites — show favorites\n"
            "/fav_courses — only favorite courses\n"
            "/roles — list of tracks\n"
            "/lang — change language\n"
            "/profile — profile\n"
            "/feedback — send feedback"
        ),
        "id_label": "Your Telegram ID:",
        "reset_done": "Profile and favorites cleared. Start again — /start",

        "about": "I’m Stepup — a career bot that helps you explore tracks and find free courses.",
        "no_data": "No data for this request yet.",
        "fav_empty": "You don’t have any favorite professions or courses yet.",
        "courses_for": "Courses for your track: ",
        "profile_block": "Your profile:",
        "age_saved": "Age group",
        "skills_label": "Skills:",
        "no_interest": "First choose a direction in the catalog so I can suggest courses.",
        "fav_header": "Your favorites:",
        "fav_courses_header": "Favorite courses:",
        "fav_prof_header": "Favorite professions:",
        "course_link": "Link",
        "ok": "OK",
    },
    "az": {
        "pick_lang": "Dili seç:",
        "greet": "Salam! Stepup karyera seçiminə kömək edəcək 🚀",
        "test": "🧭 Test",
        "catalog": "🎯 Kataloq",
        "courses": "📚 Kurslar",
        "fav": "⭐ Seçilənlər",
        "tip": "💡 Günün məsləhəti",
        "profile": "👤 Profil",
        "back_menu": "⬅️ Geri",
        "choose_dir": "İstiqaməti seç:",
        "choose_below": "Aşağıdan seçim et:",
        "professions_for": "Peşələr — ",
        "free_for": "Pulsuz kurslar:",
        "added": "Seçilənlərə əlavə olundu ⭐",
        "removed": "Seçilənlərdən silindi",
        "profile_not_found": "Profil tapılmadı. /start yazın",
        "today_tip": "Bu günün məsləhəti:",
        "test_unavail": "Test müvəqqəti əlçatmazdır.",
        "question": "Sual",
        "itogi": "Test nəticələri",
        "closest": "Ən yaxın istiqamət:",
        "also": "Həmçinin:",
        "lang_title": "Dili seç:",
        "lang_set": "Dil: {lang}",
        "send_feedback": "Rəyinizi bir mesajla yazın — adminlərə göndərəcəyəm.",
        "feedback_sent": "Təşəkkürlər! Mesaj adminlərə göndərildi.",
        "help": (
            "Komandalar:\n"
            "/test — karyera testi\n"
            "/catalog — istiqamət kataloqu\n"
            "/courses — pulsuz kurslar\n"
            "/favorites — seçilənlər\n"
            "/fav_courses — yalnız kurslar\n"
            "/roles — istiqamətlər siyahısı\n"
            "/lang — dili dəyişmək\n"
            "/profile — profil\n"
            "/feedback — rəy göndərmək"
        ),
        "id_label": "Telegram ID:",
        "reset_done": "Məlumatlar təmizləndi. Yenidən başlamaq üçün /start yazın.",

        "about": "Mən Stepupam — karyera istiqaməti seçməyə və pulsuz kurs tapmağa kömək edən botam.",
        "no_data": "Bu sorğu üzrə məlumat yoxdur.",
        "fav_empty": "Seçilmiş peşə və ya kursların yoxdur.",
        "courses_for": "İstiqamət üçün kurslar: ",
        "profile_block": "Sənin profilin:",
        "age_saved": "Yaş qrupu",
        "skills_label": "Bacarıqlar:",
        "no_interest": "Əvvəlcə kataloqdan istiqamət seç, sonra kurslar təklif edim.",
        "fav_header": "Sənin seçilənlərin:",
        "fav_courses_header": "Seçilmiş kurslar:",
        "fav_prof_header": "Seçilmiş peşələr:",
        "course_link": "Keçid",
        "ok": "OK",
    },
}

_cache = {}


def _load_gettext(lang: str):
    if lang in _cache:
        return _cache[lang]
    try:
        tr = gettext.translation(DOMAIN, localedir=LOCALES_DIR, languages=[lang])
    except Exception:
        tr = gettext.NullTranslations()
    _cache[lang] = tr
    return tr


def tr(lang: str, key: str) -> str:
    """
    Надёжный транслятор: сначала gettext, если результат равен ключу -> fallback dictionary.
    """
    lang = lang or "ru"
    tr_obj = _load_gettext(lang)
    translated = tr_obj.gettext(key)
    if translated == key:
        return _FALLBACK.get(lang, {}).get(key, key)
    return translated
