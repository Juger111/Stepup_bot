# dao.py
import os
import sqlite3
from contextlib import closing
from typing import List, Tuple, Optional

DB_PATH = os.getenv("CAREER_BOT_DB", "career_bot.db")

def db_connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db() -> None:
    with closing(db_connect()) as conn, conn:
        cur = conn.cursor()
        # базовые таблицы
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            name TEXT,
            age_group TEXT,
            interest TEXT,
            test_scores TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS professions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            description TEXT,
            skills TEXT,
            link TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            link TEXT,
            level TEXT
        )
        """)

        # миграции на случай старой БД
        cur.execute("PRAGMA table_info(users)")
        u_cols = [r[1] for r in cur.fetchall()]
        if "test_scores" not in u_cols:
            cur.execute("ALTER TABLE users ADD COLUMN test_scores TEXT")

        cur.execute("PRAGMA table_info(professions)")
        p_cols = [r[1] for r in cur.fetchall()]
        if "skills" not in p_cols:
            cur.execute("ALTER TABLE professions ADD COLUMN skills TEXT")
        if "link" not in p_cols:
            cur.execute("ALTER TABLE professions ADD COLUMN link TEXT")

        cur.execute("PRAGMA table_info(courses)")
        c_cols = [r[1] for r in cur.fetchall()]
        if "level" not in c_cols:
            cur.execute("ALTER TABLE courses ADD COLUMN level TEXT")

def seed_data() -> None:
    with closing(db_connect()) as conn, conn:
        cur = conn.cursor()

        # профессии
        cur.execute("SELECT COUNT(*) FROM professions")
        if cur.fetchone()[0] == 0:
            profs = [
                ("creative","Дизайнер цифровых продуктов",
                 "Создаёт интерфейсы и визуальные решения для веба/мобилки.",
                 "UI/UX, Figma, Типографика","https://career.yandex.ru/design"),
                ("creative","Контент-креатор",
                 "Ролики, тексты и визуал для соцсетей.",
                 "Сценарий, Монтаж, SMM","https://practicum.yandex.ru/"),
                ("tech","Python-разработчик",
                 "Пишет ботов и веб-сервисы на Python.",
                 "Python, SQL, Git, API","https://stepik.org/"),
                ("tech","Data Analyst",
                 "Аналитика данных и дашборды.",
                 "SQL, Python, BI","https://stepik.org/"),
                ("social","Психолог-консультант",
                 "Помогает людям с целями и состояниями.",
                 "Эмпатия, Коммуникация, Этика","https://netology.ru/"),
                ("social","Куратор онлайн-курсов",
                 "Сопровождает студентов, помогает проходить обучение.",
                 "Коммуникация, Тайм-менеджмент","https://skillbox.ru/"),
                ("business","Продакт-менеджер",
                 "Гипотезы, метрики, развитие продукта.",
                 "Аналитика, CJM, A/B","https://productstar.ru/"),
                ("business","Проджект-менеджер",
                 "Сроки, задачи, команда, результат.",
                 "Планирование, Риски, Коммуникация","https://pmclub.pro/"),
            ]
            cur.executemany("""
                INSERT INTO professions (category, name, description, skills, link)
                VALUES (?, ?, ?, ?, ?)
            """, profs)

        # советы
        cur.execute("SELECT COUNT(*) FROM tips")
        if cur.fetchone()[0] == 0:
            tips = [
                ("Начни с малого: 20 минут в день, но ежедневно.",),
                ("Не сравнивай свой старт с чужой серединой.",),
                ("Контроль — в привычках. Навык — в практике.",),
                ("Вопросы важнее ответов — будь любопытным.",),
            ]
            cur.executemany("INSERT INTO tips (text) VALUES (?)", tips)

        # курсы
        cur.execute("SELECT COUNT(*) FROM courses")
        if cur.fetchone()[0] == 0:
            courses = [
                ("Основы Python","tech","https://stepik.org/course/67","Новичок"),
                ("Figma для начинающих","creative","https://www.figma.com/community","Новичок"),
                ("Навыки коммуникации","social","https://coursera.org","Новичок"),
                ("Введение в менеджмент продуктов","business","https://coursera.org","Новичок"),
            ]
            cur.executemany("""
                INSERT INTO courses (title, category, link, level)
                VALUES (?, ?, ?, ?)
            """, courses)

# Users DAO
def add_user(user_id:int, name:str, age_group:Optional[str]=None)->None:
    with closing(db_connect()) as conn, conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (user_id, name, age_group)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET name=excluded.name
        """,(user_id,name,age_group))

def set_age(user_id:int, age_group:str)->None:
    with closing(db_connect()) as conn, conn:
        conn.execute("UPDATE users SET age_group=? WHERE user_id=?", (age_group,user_id))

def set_interest(user_id:int, interest:str)->None:
    with closing(db_connect()) as conn, conn:
        conn.execute("UPDATE users SET interest=? WHERE user_id=?", (interest,user_id))

def save_test_scores(user_id:int, scores:str)->None:
    with closing(db_connect()) as conn, conn:
        conn.execute("UPDATE users SET test_scores=? WHERE user_id=?", (scores,user_id))

def get_user(user_id:int)->Optional[Tuple]:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, name, age_group, interest, test_scores
            FROM users WHERE user_id=?""",(user_id,))
        return cur.fetchone()

# Content DAO
def prof_by_cat(category:str)->List[Tuple[str,str,str,str]]:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT name, description, skills, link
            FROM professions WHERE category=? ORDER BY name
        """,(category,))
        return cur.fetchall()

def courses_by_cat(category:str)->List[Tuple[str,str,str]]:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT title, link, level
            FROM courses WHERE category=?
        """,(category,))
        return cur.fetchall()

def random_tip()->str:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT text FROM tips ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else "Делай маленькие шаги каждый день."
