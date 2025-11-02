# career_bot.py
import os
import asyncio
from typing import Dict

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

from dao import (
    init_db, seed_data, add_user, set_age, set_interest,
    save_test_scores, get_user, prof_by_cat, courses_by_cat, random_tip
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8457793986:AAFZ3OJ92i127H5dcZxeJkRdCVHfD9W9CEw")

CATEGORIES = {
    "creative": "🎨 Творчество",
    "tech": "⚙️ Технологии",
    "social": "🤝 Коммуникации",
    "business": "📈 Бизнес"
}

# ---------- Keyboards ----------
def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 Подбор профессии"), KeyboardButton(text="🧭 Карьерный тест")],
            [KeyboardButton(text="📚 Курсы"), KeyboardButton(text="💡 Совет дня")],
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="ℹ️ О боте")],
        ],
        resize_keyboard=True
    )

def age_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🧒 Я подросток", callback_data="age:teen"),
        InlineKeyboardButton(text="👤 Я взрослый", callback_data="age:adult")
    ]])

def categories_inline_kb(prefix: str) -> InlineKeyboardMarkup:
    rows, row = [], []
    for idx, (code, title) in enumerate(CATEGORIES.items(), start=1):
        row.append(InlineKeyboardButton(text=title, callback_data=f"{prefix}:{code}"))
        if idx % 2 == 0:
            rows.append(row); row=[]
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="nav:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def back_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="nav:menu")]
    ])

# ---------- Career mini-test (кнопки-цифры) ----------
TEST_QUESTIONS = [
    ("Что тебя радует в процессе?\n"
     "1) Создавать визуально красивое\n"
     "2) Решать логические задачи\n"
     "3) Помогать людям и общаться\n"
     "4) Организовывать и влиять", [
        ("Создавать визуально красивое", "creative"),
        ("Решать логические задачи", "tech"),
        ("Помогать людям и общаться", "social"),
        ("Организовывать и влиять", "business")
    ]),
    ("Что проще начать сегодня?\n"
     "1) Обложка/пост/ролик\n"
     "2) Бот/скрипт\n"
     "3) Разобрать задачу и подсказать\n"
     "4) План и раздача задач", [
        ("Обложка/пост/ролик", "creative"),
        ("Бот/скрипт", "tech"),
        ("Подсказать людям", "social"),
        ("План и дедлайны", "business")
    ]),
    ("Что бы ты взял на хакатоне?\n"
     "1) Дизайн и презентация\n"
     "2) Код и интеграции\n"
     "3) Коммуникации и модерация\n"
     "4) Организация и сроки", [
        ("Дизайн/презентация", "creative"),
        ("Код/интеграции", "tech"),
        ("Коммуникации", "social"),
        ("Организация", "business")
    ])
]

def test_q_kb(q_index: int) -> InlineKeyboardMarkup:
    # самые компактные кнопки: цифры
    _, options = TEST_QUESTIONS[q_index]
    digits = ["1️⃣","2️⃣","3️⃣","4️⃣"]
    rows = [[InlineKeyboardButton(text=digits[i], callback_data=f"test:{q_index}:{tag}")]
            for i, (_, tag) in enumerate(options)]
    return InlineKeyboardMarkup(inline_keyboard=rows)

# временное хранилище результатов теста
user_test_scores: Dict[int, Dict[str, int]] = {}
user_test_step: Dict[int, int] = {}

# ---------- Router ----------
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    add_user(message.from_user.id, message.from_user.full_name)
    await message.answer(
        "Привет! Я Stepup 🚀 Помогу выбрать направление в карьере.\n"
        "Начнём с выбора возрастной группы:",
        reply_markup=main_menu_kb()
    )
    await message.answer("Выбери ниже:", reply_markup=age_inline_kb())

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Доступно:\n"
        "• 🎯 Подбор профессии\n"
        "• 🧭 Карьерный тест (3 вопроса)\n"
        "• 📚 Курсы\n"
        "• 💡 Совет дня\n"
        "• 👤 Профиль\n"
        "Проект Stepup. Автор: @Reniwzxy",
        reply_markup=main_menu_kb()
    )

@router.callback_query(F.data.startswith("age:"))
async def cb_age(cb: CallbackQuery):
    set_age(cb.from_user.id, "подросток" if cb.data.endswith("teen") else "взрослый")
    await cb.message.answer("Возрастная группа сохранена ✅", reply_markup=main_menu_kb())
    await cb.answer()

@router.callback_query(F.data == "nav:menu")
async def cb_nav_menu(cb: CallbackQuery):
    await cb.message.answer("Главное меню:", reply_markup=main_menu_kb())
    await cb.answer()

@router.message(F.text == "ℹ️ О боте")
async def about(message: Message):
    await message.answer(
        "Stepup — карьерный бот с мини-тестом. Подбирает направления, профессии, навыки и курсы.\n"
        "Автор: @Reniwzxy",
        reply_markup=main_menu_kb()
    )

@router.message(F.text == "💡 Совет дня")
async def tip(message: Message):
    await message.answer(f"Сегодняшний совет:\n\n{random_tip()}", reply_markup=main_menu_kb())

@router.message(F.text == "👤 Профиль")
async def profile(message: Message):
    u = get_user(message.from_user.id)
    if not u:
        await message.answer("Профиль не найден. Нажмите /start", reply_markup=main_menu_kb())
        return
    _, name, age_group, interest, test_scores = u
    text = (
        f"👤 <b>{name}</b>\n"
        f"Возрастная группа: {age_group or 'не указана'}\n"
        f"Интерес: {CATEGORIES.get(interest, 'не выбран') if interest else 'не выбран'}\n"
        f"Результаты теста: {test_scores or '—'}"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=main_menu_kb())

@router.message(F.text == "🎯 Подбор профессии")
async def pick_profession(message: Message):
    await message.answer("Выбери направление:", reply_markup=categories_inline_kb(prefix="cat"))

@router.message(F.text == "📚 Курсы")
async def menu_courses(message: Message):
    await message.answer("Для каких направлений показать курсы?", reply_markup=categories_inline_kb(prefix="course"))

@router.message(F.text == "🧭 Карьерный тест")
async def test_start(message: Message):
    user_test_scores[message.from_user.id] = {"creative":0,"tech":0,"social":0,"business":0}
    user_test_step[message.from_user.id] = 0
    await message.answer("Мини-тест: 3 вопроса. Отвечай цифрами на кнопках ниже.")
    await message.answer(TEST_QUESTIONS[0][0], reply_markup=test_q_kb(0))

@router.callback_query(F.data.startswith("cat:"))
async def cb_category(cb: CallbackQuery):
    code = cb.data.split(":",1)[1]
    set_interest(cb.from_user.id, code)
    profs = prof_by_cat(code)
    if not profs:
        await cb.message.answer("Пока нет данных по этой категории 😅", reply_markup=back_inline_kb())
        await cb.answer(); return

    lines = [f"<b>{CATEGORIES.get(code, code)}</b>: рекомендации\n"]
    for name, desc, skills, link in profs:
        lines.append(f"• <b>{name}</b>\n  {desc}\n  Навыки: {skills}\n  Подробнее: {link}\n")
    await cb.message.answer("\n".join(lines), parse_mode="HTML", reply_markup=back_inline_kb())
    await cb.answer()

@router.callback_query(F.data.startswith("course:"))
async def cb_courses(cb: CallbackQuery):
    code = cb.data.split(":",1)[1]
    crs = courses_by_cat(code)
    if not crs:
        await cb.message.answer("Курсы пока не найдены 😅", reply_markup=back_inline_kb())
        await cb.answer(); return

    lines = [f"<b>Курсы — {CATEGORIES.get(code, code)}</b>\n"]
    for title, link, level in crs:
        lines.append(f"• {title} ({level}) — {link}")
    await cb.message.answer("\n".join(lines), parse_mode="HTML", reply_markup=back_inline_kb())
    await cb.answer()

@router.callback_query(F.data.startswith("test:"))
async def cb_test(cb: CallbackQuery):
    parts = cb.data.split(":")  # ["test", q_index, tag]
    q_index = int(parts[1]); tag = parts[2]
    scores = user_test_scores.get(cb.from_user.id, {"creative":0,"tech":0,"social":0,"business":0})
    scores[tag] = scores.get(tag, 0) + 1
    user_test_scores[cb.from_user.id] = scores

    next_index = q_index + 1
    if next_index < len(TEST_QUESTIONS):
        user_test_step[cb.from_user.id] = next_index
        await cb.message.answer(TEST_QUESTIONS[next_index][0], reply_markup=test_q_kb(next_index))
        await cb.answer(); return

    # финал теста
    top_cat = max(scores.items(), key=lambda x: x[1])[0]
    save_test_scores(cb.from_user.id, str(scores))
    set_interest(cb.from_user.id, top_cat)

    profs = prof_by_cat(top_cat)[:3]
    lines = [f"Готово! Тебе ближе: <b>{CATEGORIES.get(top_cat, top_cat)}</b> ✨\n","Топ-рекомендации:"]
    if profs:
        for name, desc, skills, link in profs:
            lines.append(f"• <b>{name}</b>: {desc} (Навыки: {skills}) — {link}")
    else:
        lines.append("Профессии пока не найдены, но это поправимо 😉")

    crs = courses_by_cat(top_cat)
    if crs:
        lines.append("\nПодходящие курсы:")
        for title, link, level in crs[:3]:
            lines.append(f"• {title} ({level}) — {link}")

    await cb.message.answer("\n".join(lines), parse_mode="HTML", reply_markup=back_inline_kb())
    await cb.answer()

# ---------- App ----------
async def main():
    init_db()
    seed_data()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    print("Stepup is ready ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
