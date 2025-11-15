# career_bot.py
import os
import asyncio
import json
from typing import Dict, List, Tuple

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

import i18n
import db_dao as dao

BOT_TOKEN = os.getenv("BOT_TOKEN", "8592571477:AAEDSYMcIOrOrRTMmQcp4tGaOGespVA6M34")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

LANGS = {"ru": "Русский", "en": "English", "az": "Azərbaycan"}

CATEGORY_TITLES = {
    "creative": {"ru": "Творчество", "en": "Creative", "az": "Yaradıcılıq"},
    "tech": {"ru": "Технологии", "en": "Technology", "az": "Texnologiyalar"},
    "social": {"ru": "Коммуникации", "en": "Communication", "az": "Kommunikasiya"},
    "business": {"ru": "Бизнес", "en": "Business", "az": "Biznes"},
    "green": {"ru": "Green/ESG", "en": "Green/ESG", "az": "Green/ESG"},
}

ICONS = {
    "creative": "🎨",
    "tech": "💻",
    "social": "🤝",
    "business": "📈",
    "green": "🌿",
}


# ---------- Helpers ----------

def t(lang: str, key: str) -> str:
    return i18n.tr(lang or "ru", key)


def cat_title(lang: str, code: str) -> str:
    lang = lang or "ru"
    base = CATEGORY_TITLES.get(code, {})
    title = base.get(lang) or base.get("en") or code
    icon = ICONS.get(code, "")
    return f"{icon} {title}" if icon else title


def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t(lang, "test")),
                KeyboardButton(text=t(lang, "catalog")),
            ],
            [
                KeyboardButton(text=t(lang, "courses")),
                KeyboardButton(text=t(lang, "fav")),
            ],
            [
                KeyboardButton(text=t(lang, "tip")),
                KeyboardButton(text=t(lang, "profile")),
            ],
            [
                KeyboardButton(text=f"🌐 {LANGS.get(lang, '')}"),
                KeyboardButton(text="/lang"),
            ],
        ],
        resize_keyboard=True,
    )


def lang_inline_kb(cur: str | None = None):
    rows = [
        [
            InlineKeyboardButton(
                text=("✅ " if k == cur else "") + v,
                callback_data=f"lang:{k}",
            )
        ]
        for k, v in LANGS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def categories_inline_kb(lang: str, prefix: str = "cat"):
    rows = []
    row = []
    for idx, code in enumerate(CATEGORY_TITLES.keys(), start=1):
        row.append(
            InlineKeyboardButton(
                text=cat_title(lang, code),
                callback_data=f"{prefix}:{code}",
            )
        )
        if idx % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append(
        [InlineKeyboardButton(text=t(lang, "back_menu"), callback_data="nav:menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def create_answers_kb(lang: str, answers: List[Tuple[int, str]]) -> InlineKeyboardMarkup:
    rows = []
    for aid, text in answers:
        rows.append([InlineKeyboardButton(text=text, callback_data=f"ans:{aid}")])
    rows.append(
        [InlineKeyboardButton(text=t(lang, "back_menu"), callback_data="nav:menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _bar(val: int, max_val: int, length: int = 10) -> str:
    filled = 0 if max_val <= 0 else round(length * val / max_val)
    filled = max(0, min(length, filled))
    return "▮" * filled + "▯" * (length - filled)


def format_scores(scores: Dict[str, int], lang: str) -> Tuple[str, List[str]]:
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    if not ordered:
        return (t(lang, "test_unavail"), [])
    max_val = max(1, ordered[0][1])
    total = sum(scores.values()) or 1
    lines = [f"<b>{t(lang, 'itogi')}</b>\n"]
    for key, val in ordered:
        pct = round(100 * val / total)
        lines.append(
            f"{cat_title(lang, key)}: {val}  <i>({pct}%)</i>\n{_bar(val, max_val)}"
        )
    top1, v1 = ordered[0]
    resume = [f"{t(lang, 'closest')} <b>{cat_title(lang, top1)}</b>."]
    if len(ordered) > 1 and (v1 - ordered[1][1]) <= 1:
        top2, _ = ordered[1]
        resume.append(f"{t(lang, 'also')} <b>{cat_title(lang, top2)}</b>.")
    lines.append("\n".join(resume))
    return ("\n\n".join(lines), [k for k, _ in ordered])


def self_escape(s: str) -> str:
    # простая защита от html в тексте вопросов
    return s.replace("<", "&lt;").replace(">", "&gt;")


# ---------- State ----------

user_scores: Dict[int, Dict[str, int]] = {}
user_qidx: Dict[int, int] = {}


# ---------- Handlers ----------

async def on_start(message: Message):
    dao.add_user(message.from_user.id, message.from_user.full_name)
    u = dao.get_user(message.from_user.id)
    lang = u[5] if u else None
    if not lang:
        await message.answer(t("ru", "pick_lang"), reply_markup=lang_inline_kb(None))
        return
    await message.answer(t(lang, "greet"), reply_markup=main_menu_kb(lang))
    await message.answer(t(lang, "choose_below"))


async def cb_lang(callback: CallbackQuery):
    code = callback.data.split(":", 1)[1]
    if code not in LANGS:
        await callback.answer()
        return
    dao.set_lang(callback.from_user.id, code)
    await callback.message.answer(t(code, "lang_set").format(lang=LANGS[code]))
    await callback.message.answer(t(code, "greet"), reply_markup=main_menu_kb(code))
    await callback.answer()


async def nav_cb(callback: CallbackQuery):
    if callback.data != "nav:menu":
        await callback.answer()
        return
    lang = dao.get_lang(callback.from_user.id)
    await callback.message.answer(t(lang, "greet"), reply_markup=main_menu_kb(lang))
    await callback.answer()


async def cmd_lang(message: Message):
    u = dao.get_user(message.from_user.id)
    cur = u[5] if u else None
    await message.answer(t(cur or "ru", "lang_title"), reply_markup=lang_inline_kb(cur))


async def cmd_help(message: Message):
    lang = dao.get_lang(message.from_user.id)
    await message.answer(t(lang, "help"), reply_markup=main_menu_kb(lang))


async def cmd_about(message: Message):
    lang = dao.get_lang(message.from_user.id)
    await message.answer(t(lang, "about"))


async def cmd_id(message: Message):
    lang = dao.get_lang(message.from_user.id)
    await message.answer(
        f"{t(lang, 'id_label')} <code>{message.from_user.id}</code>",
        parse_mode="HTML",
    )


async def cmd_reset(message: Message):
    lang = dao.get_lang(message.from_user.id)
    dao.reset_user(message.from_user.id)
    await message.answer(t(lang, "reset_done"))
    await on_start(message)


async def catalog_cmd(message: Message):
    lang = dao.get_lang(message.from_user.id)
    await message.answer(t(lang, "choose_dir"), reply_markup=categories_inline_kb(lang))


async def cat_cb(callback: CallbackQuery):
    lang = dao.get_lang(callback.from_user.id)
    code = callback.data.split(":", 1)[1]
    dao.set_interest(callback.from_user.id, code)
    profs = dao.prof_by_cat(code)
    if not profs:
        await callback.message.answer(t(lang, "no_data"), reply_markup=None)
        await callback.answer()
        return

    await callback.message.answer(
        f"<b>{t(lang, 'professions_for')}{cat_title(lang, code)}</b>",
        parse_mode="HTML",
    )

    skills_label = t(lang, "skills_label")

    for row in profs[:20]:
        pid = row[0]
        # row: id, name, description, skills, link, name_en, description_en, skills_en
        name = row[1] if lang == "ru" else (row[5] or row[1])
        desc = row[2] if lang == "ru" else (row[6] or row[2])
        skills = row[3] if lang == "ru" else (row[7] or row[3])

        text_lines = [f"• <b>{name}</b>"]
        if desc:
            text_lines.append(desc)
        if skills:
            text_lines.append(f"{skills_label} {skills}")

        await callback.message.answer("\n".join(text_lines), parse_mode="HTML")

    await callback.answer()


# ----- Test flow -----

async def start_test(message: Message):
    lang = dao.get_lang(message.from_user.id)
    cnt = dao.questions_count()
    if cnt == 0:
        await message.answer(t(lang, "test_unavail"))
        return
    user_scores[message.from_user.id] = {
        "creative": 0,
        "tech": 0,
        "social": 0,
        "business": 0,
        "green": 0,
    }
    user_qidx[message.from_user.id] = 0
    await send_question(message.from_user.id, message)


async def send_question(user_id: int, origin_message: Message):
    lang = dao.get_lang(user_id)
    idx = user_qidx.get(user_id, 0)

    # берём вопрос уже с учётом языка
    q = dao.get_question_by_index(idx, lang=lang)
    if not q:
        await finish_test(user_id, origin_message)
        return

    qid, text = q
    answers = dao.get_answers_for_question(qid, lang=lang)
    kb_answers = [(a[0], a[1]) for a in answers]

    kb = create_answers_kb(lang, kb_answers)
    await origin_message.answer(
        f"{t(lang, 'question')} {idx + 1}/{dao.questions_count()}\n\n{self_escape(text)}",
        reply_markup=kb,
    )


async def answer_callback(callback: CallbackQuery):
    data = callback.data
    if not data.startswith("ans:"):
        await callback.answer()
        return
    aid = int(data.split(":", 1)[1])
    uid = callback.from_user.id
    lang = dao.get_lang(uid)
    weights = dao.get_answer_weights(aid)
    if not weights:
        await callback.answer(t(lang, "ok"))
        return
    sc = user_scores.get(
        uid, {"creative": 0, "tech": 0, "social": 0, "business": 0, "green": 0}
    )
    for k, v in weights.items():
        sc[k] = sc.get(k, 0) + (v or 0)
    user_scores[uid] = sc
    user_qidx[uid] = user_qidx.get(uid, 0) + 1
    await callback.answer()
    await send_question(uid, callback.message)


async def finish_test(user_id: int, origin_message: Message):
    lang = dao.get_lang(user_id)
    scores = user_scores.get(
        user_id, {"creative": 0, "tech": 0, "social": 0, "business": 0, "green": 0}
    )
    text, order = format_scores(scores, lang)
    dao.save_test_scores(user_id, json.dumps(scores))
    await origin_message.answer(text, parse_mode="HTML")
    user_scores.pop(user_id, None)
    user_qidx.pop(user_id, None)


# ---------- Utilities / Favorites / Courses ----------

async def send_feedback(message: Message):
    lang = dao.get_lang(message.from_user.id)
    await message.answer(t(lang, "send_feedback"))
    # примитивное состояние: -999 означает "ждём текст отзыва"
    user_qidx[message.from_user.id] = -999


async def cmd_courses(message: Message):
    await show_courses_for_user(message)


async def show_courses_for_user(message: Message):
    uid = message.from_user.id
    lang = dao.get_lang(uid)
    u = dao.get_user(uid)
    if not u or not u[3]:
        await message.answer(t(lang, "no_interest"))
        return
    cat = u[3]
    courses = dao.free_courses_by_cat(cat, limit=5)
    if not courses:
        await message.answer(t(lang, "no_data"))
        return
    await message.answer(t(lang, "courses_for") + cat_title(lang, cat))
    for cid, title, link, level, title_en in courses:
        name = title if lang == "ru" else (title_en or title)
        text = f"• <b>{name}</b>\n{t(lang, 'course_link')}: {link}"
        await message.answer(text, parse_mode="HTML")


async def cmd_favorites(message: Message):
    uid = message.from_user.id
    lang = dao.get_lang(uid)
    favs = dao.list_favorites(uid)
    if not favs["profession"] and not favs["course"]:
        await message.answer(t(lang, "fav_empty"))
        return
    lines = [t(lang, "fav_header")]
    if favs["profession"]:
        lines.append("\n" + t(lang, "fav_prof_header"))
        for p in favs["profession"]:
            pid, name, category, link = p
            lines.append(f"• {name} ({cat_title(lang, category)})")
    if favs["course"]:
        lines.append("\n" + t(lang, "fav_courses_header"))
        for c in favs["course"]:
            cid, title, category, link = c
            lines.append(f"• {title} — {link}")
    await message.answer("\n".join(lines))


async def cmd_fav_courses(message: Message):
    uid = message.from_user.id
    lang = dao.get_lang(uid)
    rows = dao.list_fav_courses_only(uid)
    if not rows:
        await message.answer(t(lang, "fav_empty"))
        return
    lines = [t(lang, "fav_courses_header")]
    for cid, title, category, link in rows:
        lines.append(f"• {title} — {link}")
    await message.answer("\n".join(lines))


async def cmd_roles(message: Message):
    lang = dao.get_lang(message.from_user.id)
    lines = [t(lang, "choose_dir")]
    for code in CATEGORY_TITLES.keys():
        lines.append(f"• {cat_title(lang, code)}")
    await message.answer("\n".join(lines), reply_markup=categories_inline_kb(lang))


async def handle_text(message: Message):
    uid = message.from_user.id
    lang = dao.get_lang(uid)

    # Если ждём отзыв
    if user_qidx.get(uid, None) == -999:
        text = f"[Feedback] From: {message.from_user.full_name} ({uid})\n\n{message.text}"
        try:
            if ADMIN_CHAT_ID:
                bot = message.bot
                await bot.send_message(ADMIN_CHAT_ID, text)
            await message.answer(t(lang, "feedback_sent"))
        except Exception as e:
            await message.answer(t(lang, "feedback_sent") + f" ({e})")
        user_qidx.pop(uid, None)
        return

    # кнопки
    if message.text == t(lang, "catalog"):
        await catalog_cmd(message)
        return
    if message.text == t(lang, "test") or message.text == "/test":
        await start_test(message)
        return
    if message.text == t(lang, "courses"):
        await show_courses_for_user(message)
        return
    if message.text == t(lang, "fav"):
        await cmd_favorites(message)
        return
    if message.text == t(lang, "tip"):
        await message.answer(t(lang, "today_tip") + "\n" + dao.random_tip(lang))
        return
    if message.text == t(lang, "profile"):
        u = dao.get_user(uid)
        if not u:
            await message.answer(t(lang, "profile_not_found"))
            return
        # user: (user_id, name, age_group, interest, test_scores, lang)
        scores = u[4] or ""
        interest = u[3]
        interest_title = cat_title(lang, interest) if interest else "-"
        age_group = u[2] or "-"
        text = (
            f"{t(lang, 'profile_block')}\n\n"
            f"{t(lang, 'id_label')} {uid}\n"
            f"{t(lang, 'profile')}: {u[1]}\n"
            f"{t(lang, 'age_saved')}: {age_group}\n"
            f"{t(lang, 'choose_dir')}: {interest_title}\n"
            f"{t(lang, 'itogi')}: {scores}"
        )
        await message.answer(text)
        return

    # fallback
    await message.answer(t(lang, "no_data"))


# ---------- Runner ----------

async def main():
    dao.init_db()
    dao.seed_data()

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    # callbacks
    dp.message.register(on_start, CommandStart())
    dp.callback_query.register(cb_lang, lambda c: c.data and c.data.startswith("lang:"))
    dp.callback_query.register(nav_cb, lambda c: c.data == "nav:menu")
    dp.callback_query.register(cat_cb, lambda c: c.data and c.data.startswith("cat:"))
    dp.callback_query.register(
        answer_callback, lambda c: c.data and c.data.startswith("ans:")
    )

    # commands
    dp.message.register(cmd_lang, Command(commands=["lang"]))
    dp.message.register(cmd_help, Command(commands=["help"]))
    dp.message.register(cmd_about, Command(commands=["about"]))
    dp.message.register(cmd_id, Command(commands=["id"]))
    dp.message.register(cmd_reset, Command(commands=["reset"]))
    dp.message.register(cmd_courses, Command(commands=["courses"]))
    dp.message.register(cmd_favorites, Command(commands=["favorites"]))
    dp.message.register(cmd_fav_courses, Command(commands=["fav_courses"]))
    dp.message.register(cmd_roles, Command(commands=["roles"]))
    dp.message.register(start_test, Command(commands=["test"]))
    dp.message.register(send_feedback, Command(commands=["feedback"]))

    # общий текстовый обработчик
    dp.message.register(handle_text)

    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
