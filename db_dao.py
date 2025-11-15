# db_dao.py
import os
import sqlite3
from contextlib import closing
from typing import List, Tuple, Optional, Dict

DB_PATH = os.getenv("CAREER_BOT_DB", "career_bot.db")


def db_connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def _has_col(cur, table: str, col: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return col in [r[1] for r in cur.fetchall()]


def init_db() -> None:
    """Создание/миграции схемы (идемпотентно)."""
    with closing(db_connect()) as conn, conn:
        cur = conn.cursor()

        # users
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            name TEXT,
            age_group TEXT,
            interest TEXT,
            test_scores TEXT,
            lang TEXT
        )"""
        )

        # professions
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS professions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            description TEXT,
            skills TEXT,
            link TEXT,
            domain TEXT,
            name_en TEXT,
            description_en TEXT,
            skills_en TEXT
        )"""
        )

        # tips
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT
        )"""
        )

        # courses
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            link TEXT,
            level TEXT,
            title_en TEXT
        )"""
        )

        # favorites
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            entity_type TEXT,
            entity_id INTEGER,
            UNIQUE (user_id, entity_type, entity_id)
        )"""
        )

        # questions
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_idx INTEGER,
            text TEXT
        )"""
        )

        # answers
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            text TEXT,
            weight_creative INTEGER DEFAULT 0,
            weight_tech INTEGER DEFAULT 0,
            weight_social INTEGER DEFAULT 0,
            weight_business INTEGER DEFAULT 0,
            weight_green INTEGER DEFAULT 0
        )"""
        )

        # --- миграции (добавляем недостающие колонки) ---
        for tbl, col in [
            ("users", "test_scores"),
            ("users", "lang"),
            ("professions", "skills"),
            ("professions", "link"),
            ("professions", "domain"),
            ("professions", "name_en"),
            ("professions", "description_en"),
            ("professions", "skills_en"),
            ("courses", "level"),
            ("courses", "title_en"),
            ("questions", "text_en"),
            ("questions", "text_az"),
            ("answers", "text_en"),
            ("answers", "text_az"),
            ("tips", "text_en"),
            ("tips", "text_az"),
        ]:
            if not _has_col(cur, tbl, col):
                cur.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} TEXT")


def seed_data() -> None:
    """Начальные данные + переводы, если пусто."""
    with closing(db_connect()) as conn, conn:
        cur = conn.cursor()

        # Профессии (если пусто)
        cur.execute("SELECT COUNT(*) FROM professions")
        if cur.fetchone()[0] == 0:
            profs = [
                (
                    "tech",
                    "Python-разработчик",
                    "Пишет ботов и веб-сервисы на Python.",
                    "Python, SQL, Git, API",
                    "https://stepik.org/",
                    "backend",
                    "Python Developer",
                    "Builds bots & web services with Python.",
                    "Python, SQL, Git, API",
                ),
                (
                    "tech",
                    "Data Analyst / BI",
                    "Аналитика данных и дашборды.",
                    "SQL, Python, BI",
                    "https://stepik.org/",
                    "data",
                    "Data Analyst / BI",
                    "Data analysis and dashboards.",
                    "SQL, Python, BI",
                ),
                (
                    "tech",
                    "ML Engineer",
                    "Модели, обучение, MLOps.",
                    "Python, PyTorch, MLOps",
                    "https://www.coursera.org/",
                    "ai_ml",
                    "ML Engineer",
                    "Models, training, MLOps.",
                    "Python, PyTorch, MLOps",
                ),
                (
                    "tech",
                    "QA Automation",
                    "Автотесты и CI/CD.",
                    "PyTest, Selenium, CI/CD",
                    "https://docs.pytest.org/",
                    "qa",
                    "QA Automation",
                    "Test automation & CI/CD.",
                    "PyTest, Selenium, CI/CD",
                ),
                (
                    "tech",
                    "Cybersecurity Analyst",
                    "Инциденты и уязвимости.",
                    "Network, SIEM, Security",
                    "https://www.coursera.org/",
                    "cyber",
                    "Cybersecurity Analyst",
                    "Incidents and vulnerabilities.",
                    "Network, SIEM, Security",
                ),
                (
                    "creative",
                    "UX/UI Designer",
                    "Проектирует сценарии и интерфейсы.",
                    "Figma, Research, Prototyping",
                    "https://www.figma.com/",
                    "ux_ui",
                    "UX/UI Designer",
                    "Designs flows & interfaces.",
                    "Figma, Research, Prototyping",
                ),
                (
                    "business",
                    "Product Manager",
                    "Гипотезы, метрики, рост.",
                    "Analytics, CJM, A/B",
                    "https://www.coursera.org/",
                    "pm_ba",
                    "Product Manager",
                    "Hypotheses, metrics, growth.",
                    "Analytics, CJM, A/B",
                ),
                (
                    "business",
                    "Business Analyst",
                    "Требования, диаграммы, SQL.",
                    "BPMN, BRD, SQL",
                    "https://www.coursera.org/",
                    "pm_ba",
                    "Business Analyst",
                    "Requirements, diagrams, SQL.",
                    "BPMN, BRD, SQL",
                ),
                (
                    "social",
                    "Customer Success Manager",
                    "Онбординг, удержание, NPS.",
                    "Onboarding, CRM, Empathy",
                    "https://successhub.com/",
                    "",
                    "Customer Success Manager",
                    "Onboarding, retention, NPS.",
                    "Onboarding, CRM, Empathy",
                ),
                (
                    "green",
                    "Sustainability Specialist",
                    "ESG-инициативы и отчётность.",
                    "ESG, Reporting, Analytics",
                    "https://www.coursera.org/",
                    "",
                    "Sustainability Specialist",
                    "ESG initiatives & reporting.",
                    "ESG, Reporting, Analytics",
                ),
            ]
            cur.executemany(
                """
                INSERT INTO professions
                (category, name, description, skills, link, domain, name_en, description_en, skills_en)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                profs,
            )

        # Советы
        cur.execute("SELECT COUNT(*) FROM tips")
        if cur.fetchone()[0] == 0:
            tips = [
                (
                    "Начни с малого: 20 минут в день, но ежедневно.",
                    "Start small: 20 minutes a day, but every day.",
                    "Kiçik başla: günə 20 dəqiqə, amma hər gün.",
                ),
                (
                    "Не сравнивай свой старт с чужой серединой.",
                    "Don’t compare your start to someone else’s middle.",
                    "Başlanğıcını başqasının ortası ilə müqayisə etmə.",
                ),
                (
                    "Контроль — в привычках. Навык — в практике.",
                    "Control lives in habits. Skill lives in practice.",
                    "Nəzarət vərdişlərdədir. Bacarıq təcrübədədir.",
                ),
                (
                    "Вопросы важнее ответов — будь любопытным.",
                    "Questions are more important than answers — stay curious.",
                    "Sual cavabdan daha vacibdir — maraqlı ol.",
                ),
            ]
            cur.executemany(
                "INSERT INTO tips (text, text_en, text_az) VALUES (?, ?, ?)", tips
            )

        # Курсы (free)
        cur.execute("SELECT COUNT(*) FROM courses")
        if cur.fetchone()[0] == 0:
            courses = [
                (
                    "freeCodeCamp: Python",
                    "tech",
                    "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
                    "free",
                    "freeCodeCamp: Python",
                ),
                (
                    "CS50x (Harvard) — вводный курс CS",
                    "tech",
                    "https://cs50.harvard.edu/x/",
                    "free",
                    "CS50x — Intro CS",
                ),
                (
                    "Kaggle Microcourses — практическая аналитика данных",
                    "tech",
                    "https://www.kaggle.com/learn",
                    "free",
                    "Kaggle Microcourses",
                ),
                (
                    "Intro to SQL (Mode) — основы SQL",
                    "tech",
                    "https://mode.com/sql-tutorial/",
                    "free",
                    "Intro to SQL",
                ),
                (
                    "PyTest Docs (официальная документация)",
                    "tech",
                    "https://docs.pytest.org/",
                    "free",
                    "PyTest Docs",
                ),
                (
                    "Figma Learn — основы дизайна интерфейсов",
                    "creative",
                    "https://help.figma.com/hc/en-us/articles/360040528973-Learn-design-with-Figma",
                    "free",
                    "Figma Learn",
                ),
                (
                    "Google UX Basics (Coursera, аудит)",
                    "creative",
                    "https://www.coursera.org/professional-certificates/google-ux-design",
                    "free",
                    "Google UX Basics",
                ),
                (
                    "Product School Blog — продуктовый менеджмент",
                    "business",
                    "https://productschool.com/blog",
                    "free",
                    "Product School Blog",
                ),
                (
                    "PMBOK Overview (free) — основы проектного управления",
                    "business",
                    "https://www.pmi.org/pmbok-guide-standards",
                    "free",
                    "PMBOK Overview",
                ),
                (
                    "Customer Success Fundamentals",
                    "social",
                    "https://successhub.com/",
                    "free",
                    "Customer Success Fundamentals",
                ),
                (
                    "ESG Basics (UN) — устойчивое развитие",
                    "green",
                    "https://sdgs.un.org/",
                    "free",
                    "ESG Basics (UN)",
                ),
            ]
            cur.executemany(
                """
                INSERT INTO courses (title, category, link, level, title_en)
                VALUES (?, ?, ?, ?, ?)
            """,
                courses,
            )

        # Вопросы/ответы теста с переводами
        cur.execute("SELECT COUNT(*) FROM questions")
        if cur.fetchone()[0] == 0:
            questions = [
                (
                    0,
                    "Что тебе интереснее всего делать в проекте?",
                    "What is most interesting for you in a project?",
                    "Layihədə ən çox nə maraqlıdır?",
                ),
                (
                    1,
                    "Какой тип задач тебя заряжает?",
                    "What type of tasks energize you?",
                    "Səni hansı tapşırıqlar ruhlandırır?",
                ),
                (
                    2,
                    "Что проще начать сегодня?",
                    "What is easier to start today?",
                    "Bu gün nədən başlamaq asandır?",
                ),
                (
                    3,
                    "Какой формат команды комфортнее?",
                    "What team format is more comfortable?",
                    "Hansı komanda formatı rahatdır?",
                ),
                (
                    4,
                    "Что для тебя успех через 6 месяцев?",
                    "What is a success for you in 6 months?",
                    "6 ay sonra uğur sənin üçün nə deməkdir?",
                ),
                (
                    5,
                    "Какая среда/инструмент ближе?",
                    "Which environment/tool is closer to you?",
                    "Hansə mühit/alət sənə yaxındır?",
                ),
                (
                    6,
                    "Что легче давалось в школе/вузе?",
                    "What was easier for you at school/university?",
                    "Məktəbdə/universitetdə nə daha asan idi?",
                ),
                (
                    7,
                    "Как относишься к экспериментам и риску?",
                    "How do you feel about experiments and risk?",
                    "Eksperiment və riskə münasibətin necədir?",
                ),
                (
                    8,
                    "Что важнее: влияние или глубина экспертизы?",
                    "What is more important: impact or depth of expertise?",
                    "Daha vacib nədir: təsir yoxsa ekspertiza dərinliyi?",
                ),
                (
                    9,
                    "С чем точно не хочется работать?",
                    "What do you definitely not want to work with?",
                    "Nə ilə işləmək istəmirsən?",
                ),
            ]
            cur.executemany(
                """
                INSERT INTO questions (order_idx, text, text_en, text_az)
                VALUES (?, ?, ?, ?)
            """,
                questions,
            )

            def add_ans(
                order_idx,
                text,
                text_en,
                text_az,
                c=0,
                t=0,
                s=0,
                b=0,
                g=0,
            ):
                cur.execute(
                    "SELECT id FROM questions WHERE order_idx=?", (order_idx,)
                )
                qid = cur.fetchone()[0]
                cur.execute(
                    """
                    INSERT INTO answers
                    (question_id, text, text_en, text_az,
                     weight_creative, weight_tech, weight_social, weight_business, weight_green)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (qid, text, text_en, text_az, c, t, s, b, g),
                )

            add_ans(
                0,
                "Создавать визуально убедительное",
                "Create visual concepts",
                "Vizual konseptlər yaratmaq",
                2,
                0,
                0,
                0,
                0,
            )
            add_ans(
                0,
                "Решать логические/тех. задачи",
                "Solve logical/tech tasks",
                "Məntiqi/texniki tapşırıqları həll etmək",
                0,
                2,
                0,
                0,
                0,
            )
            add_ans(
                0,
                "Помогать людям и общаться",
                "Help people and communicate",
                "İnsanlara kömək və ünsiyyət",
                0,
                0,
                2,
                0,
                0,
            )
            add_ans(
                0,
                "Организовывать и влиять",
                "Organize and influence",
                "Təşkil etmək və təsir göstərmək",
                0,
                0,
                0,
                2,
                0,
            )

            add_ans(
                1,
                "Дизайн-процесс и история",
                "Design process & storytelling",
                "Dizayn prosesi və hekayəçilik",
                2,
                0,
                0,
                0,
                0,
            )
            add_ans(
                1,
                "Код/данные/автоматизация",
                "Code/data/automation",
                "Kod/məlumat/avtomatlaşdırma",
                0,
                2,
                0,
                0,
                0,
            )
            add_ans(
                1,
                "Коммуникации/поддержка",
                "Comms/support",
                "Kommunikasiya/dəstək",
                0,
                0,
                2,
                0,
                0,
            )
            add_ans(
                1,
                "Метрики/рост/управление",
                "Metrics/growth/management",
                "Metriklər/artım/idarəetmə",
                0,
                0,
                0,
                2,
                0,
            )

            add_ans(
                2,
                "Сделать обложку/ролик",
                "Make a cover/video",
                "Obloşka/rolik hazırlamaq",
                2,
                0,
                0,
                0,
                0,
            )
            add_ans(
                2,
                "Написать бота/скрипт",
                "Write a bot/script",
                "Bot/skipt yazmaq",
                0,
                2,
                0,
                0,
                0,
            )
            add_ans(
                2,
                "Помочь/разобрать кейс",
                "Help/analyze a case",
                "Kömək/keisi təhlil etmək",
                0,
                0,
                2,
                0,
                0,
            )
            add_ans(
                2,
                "Составить план и дедлайны",
                "Plan & deadlines",
                "Plan və deadline tərtib etmək",
                0,
                0,
                0,
                2,
                0,
            )

            add_ans(
                3,
                "Малая креативная команда",
                "Small creative team",
                "Kiçik kreativ komanda",
                2,
                0,
                0,
                0,
                0,
            )
            add_ans(
                3,
                "Инженерная команда",
                "Engineering team",
                "Mühəndislik komanda",
                0,
                2,
                0,
                0,
                0,
            )
            add_ans(
                3,
                "Поддержка/сообщество",
                "Support/community",
                "Dəstək/icma",
                0,
                0,
                2,
                0,
                0,
            )
            add_ans(
                3,
                "Кросс-функциональная",
                "Cross-functional",
                "Çoxfunksiyalı",
                0,
                0,
                0,
                2,
                0,
            )

            add_ans(
                4,
                "Портфолио из 3 работ",
                "Portfolio of 3 works",
                "3 işdən ibarət portfel",
                2,
                0,
                0,
                0,
                0,
            )
            add_ans(
                4,
                "Автопайплайн/скрипты",
                "Auto-pipelines/scripts",
                "Auto-pipeline/skriptlər",
                0,
                2,
                0,
                0,
                0,
            )
            add_ans(
                4,
                "Высокие оценки людей",
                "Great feedback from people",
                "İnsanlardan yüksək rəy",
                0,
                0,
                2,
                0,
                0,
            )
            add_ans(
                4,
                "Рост метрик проекта",
                "Project metrics growth",
                "Layihə metriklərinin artması",
                0,
                0,
                0,
                2,
                0,
            )

            add_ans(
                5,
                "Figma/монтаж/презентации",
                "Figma/editing/presentations",
                "Figma/montaj/prezentasiyalar",
                2,
                0,
                0,
                0,
                0,
            )
            add_ans(
                5,
                "Python/SQL/IDE",
                "Python/SQL/IDE",
                "Python/SQL/IDE",
                0,
                2,
                0,
                0,
                0,
            )
            add_ans(
                5,
                "CRM/чат/звонки",
                "CRM/chat/calls",
                "CRM/söhbət/zənglər",
                0,
                0,
                2,
                0,
                0,
            )
            add_ans(
                5,
                "Kanban/метрики",
                "Kanban/metrics",
                "Kanban/metriklər",
                0,
                0,
                0,
                2,
                0,
            )

            add_ans(
                6,
                "Искусство/литература",
                "Arts/literature",
                "İncəsənət/ədəbiyyat",
                2,
                0,
                0,
                0,
                0,
            )
            add_ans(
                6,
                "Математика/информатика",
                "Math/CS",
                "Riyaziyyat/İT",
                0,
                2,
                0,
                0,
                0,
            )
            add_ans(
                6,
                "Обществознание/психология",
                "Social science/psychology",
                "Cəmiyyət/psixologiya",
                0,
                0,
                2,
                0,
                0,
            )
            add_ans(
                6,
                "Экономика/менеджмент",
                "Economics/management",
                "İqtisadiyyat/menecment",
                0,
                0,
                0,
                2,
                0,
            )

            add_ans(
                7,
                "Люблю пробовать новое",
                "I like trying new things",
                "Yenilikləri sevirəm",
                1,
                1,
                1,
                1,
                0,
            )
            add_ans(
                7,
                "Предпочитаю стабильность",
                "Prefer stability",
                "Sabitliyi üstün tuturam",
                0,
                0,
                0,
                1,
                0,
            )
            add_ans(
                7,
                "Готов рисковать ради результата",
                "Ready to risk for result",
                "Nəticə üçün riskə hazıram",
                0,
                1,
                0,
                1,
                0,
            )
            add_ans(
                7,
                "Эксперименты в экотеме",
                "Green experiments",
                "Yaşıl eksperimentlər",
                0,
                0,
                0,
                0,
                2,
            )

            add_ans(
                8,
                "Глубина экспертизы важнее",
                "Depth > impact",
                "Dərinlik > təsir",
                0,
                1,
                0,
                1,
                0,
            )
            add_ans(
                8,
                "Влияние на опыт людей важнее",
                "Impact > depth",
                "Təsir > dərinlik",
                1,
                0,
                1,
                0,
                0,
            )
            add_ans(
                8,
                "Баланс: продукт и экспертиза",
                "Balance: product & expertise",
                "Balans: məhsul və ekspertiza",
                1,
                1,
                1,
                1,
                0,
            )
            add_ans(
                8,
                "Проекты устойчивого развития",
                "Sustainability projects",
                "Dayanıqlı layihələr",
                0,
                0,
                0,
                0,
                2,
            )

            add_ans(
                9,
                "Долгие excel-отчёты",
                "Long excel reports",
                "Uzun excel hesabatları",
                1,
                0,
                1,
                0,
                0,
            )
            add_ans(
                9,
                "Глубокая backend-нагрузка",
                "Heavy backend load",
                "Ağır backend yükləri",
                0,
                1,
                0,
                0,
                0,
            )
            add_ans(
                9,
                "Плотные продажи и скрипты",
                "Hard sales & scripts",
                "Sıx satışlar və skriptlər",
                0,
                0,
                1,
                0,
                0,
            )
            add_ans(
                9,
                "Проекты без смысла для планеты",
                "No-purpose for planet",
                "Planet üçün mənasız layihələr",
                0,
                0,
                0,
                0,
                2,
            )


# ---------- USERS ----------

def add_user(user_id: int, name: str, age_group: Optional[str] = None) -> None:
    with closing(db_connect()) as conn, conn:
        conn.execute(
            """
            INSERT INTO users (user_id, name, age_group)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET name=excluded.name
        """,
            (user_id, name, age_group),
        )


def set_age(user_id: int, age_group: str) -> None:
    with closing(db_connect()) as conn, conn:
        conn.execute(
            "UPDATE users SET age_group=? WHERE user_id=?", (age_group, user_id)
        )


def set_interest(user_id: int, interest: str) -> None:
    with closing(db_connect()) as conn, conn:
        conn.execute(
            "UPDATE users SET interest=? WHERE user_id=?", (interest, user_id)
        )


def save_test_scores(user_id: int, scores: str) -> None:
    with closing(db_connect()) as conn, conn:
        conn.execute(
            "UPDATE users SET test_scores=? WHERE user_id=?", (scores, user_id)
        )


def reset_user(user_id: int) -> None:
    with closing(db_connect()) as conn, conn:
        conn.execute(
            "UPDATE users SET age_group=NULL, interest=NULL, test_scores=NULL WHERE user_id=?",
            (user_id,),
        )
        conn.execute("DELETE FROM favorites WHERE user_id=?", (user_id,))


def get_user(user_id: int) -> Optional[Tuple]:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT user_id, name, age_group, interest, test_scores, lang
            FROM users WHERE user_id=?""",
            (user_id,),
        )
        return cur.fetchone()


def get_lang(user_id: int) -> str:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        return row[0] if row and row[0] else "ru"


def set_lang(user_id: int, lang: str) -> None:
    with closing(db_connect()) as conn, conn:
        conn.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))


# ---------- CONTENT ----------

def prof_by_cat(category: str) -> List[Tuple]:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, name, description, skills, link, name_en, description_en, skills_en
            FROM professions WHERE category=? ORDER BY name
        """,
            (category,),
        )
        return cur.fetchall()


def prof_by_domain(domain: str) -> List[Tuple]:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, name, description, skills, link, name_en, description_en, skills_en
            FROM professions WHERE domain=? ORDER BY name
        """,
            (domain,),
        )
        return cur.fetchall()


def courses_by_cat(category: str) -> List[Tuple]:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, title, link, level, title_en
            FROM courses WHERE category=?
        """,
            (category,),
        )
        return cur.fetchall()


def free_courses_by_cat(
    category: str, limit: int = 3
) -> List[Tuple[int, str, str, str, str]]:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, title, link, level, title_en
            FROM courses
            WHERE category=? AND LOWER(level) IN ('бесплатно','free')
            ORDER BY id LIMIT ?
        """,
            (category, limit),
        )
        return cur.fetchall()


def random_tip(lang: str = "ru") -> str:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT text, text_en, text_az FROM tips ORDER BY RANDOM() LIMIT 1"
            )
            row = cur.fetchone()
        except sqlite3.OperationalError:
            # старые базы, где ещё нет колонок text_en/text_az
            cur.execute("SELECT text FROM tips ORDER BY RANDOM() LIMIT 1")
            r = cur.fetchone()
            return r[0] if r else "Делай маленькие шаги каждый день."
        if not row:
            return "Делай маленькие шаги каждый день."
        ru, en, az = row
        if lang == "en" and en:
            return en
        if lang == "az" and az:
            return az
        return ru or en or az or "Делай маленькие шаги каждый день."


# ---------- FAVORITES ----------

def toggle_favorite(user_id: int, entity_type: str, entity_id: int) -> bool:
    with closing(db_connect()) as conn, conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO favorites (user_id, entity_type, entity_id)
                VALUES (?, ?, ?)
            """,
                (user_id, entity_type, entity_id),
            )
            return True
        except sqlite3.IntegrityError:
            cur.execute(
                """
                DELETE FROM favorites WHERE user_id=? AND entity_type=? AND entity_id=?
            """,
                (user_id, entity_type, entity_id),
            )
            return False


def list_favorites(user_id: int) -> Dict[str, List[Tuple]]:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        res: Dict[str, List[Tuple]] = {"profession": [], "course": []}

        cur.execute(
            """
            SELECT p.id, p.name, p.category, p.link
            FROM favorites f
            JOIN professions p ON p.id=f.entity_id
            WHERE f.user_id=? AND f.entity_type='profession'
            ORDER BY p.name
        """,
            (user_id,),
        )
        res["profession"] = cur.fetchall()

        cur.execute(
            """
            SELECT c.id, c.title, c.category, c.link
            FROM favorites f
            JOIN courses c ON c.id=f.entity_id
            WHERE f.user_id=? AND f.entity_type='course'
            ORDER BY c.title
        """,
            (user_id,),
        )
        res["course"] = cur.fetchall()
        return res


def list_fav_courses_only(user_id: int) -> List[Tuple[int, str, str, str]]:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT c.id, c.title, c.category, c.link
            FROM favorites f
            JOIN courses c ON c.id=f.entity_id
            WHERE f.user_id=? AND f.entity_type='course'
            ORDER BY c.title
        """,
            (user_id,),
        )
        return cur.fetchall()


# ---------- TEST (локализация) ----------

def questions_count() -> int:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM questions")
        row = cur.fetchone()
        return row[0] if row and row[0] is not None else 0


def get_question_by_index(order_idx: int, lang: str = "ru") -> Optional[Tuple[int, str]]:
    """Возвращает (id, локализованный текст)."""
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, text, text_en, text_az FROM questions WHERE order_idx=?",
            (order_idx,),
        )
        row = cur.fetchone()
        if not row:
            return None
        qid, ru, en, az = row
        txt = ru
        if lang == "en" and en:
            txt = en
        elif lang == "az" and az:
            txt = az
        return (qid, txt)


def get_answers_for_question(
    question_id: int, lang: str = "ru"
) -> List[Tuple[int, str, int, int, int, int, int]]:
    """Возвращает локализованные ответы с весами."""
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, text, text_en, text_az,
                   weight_creative, weight_tech, weight_social, weight_business, weight_green
            FROM answers WHERE question_id=? ORDER BY id
        """,
            (question_id,),
        )
        rows = cur.fetchall()
        out = []
        for rid, ru, en, az, wc, wt, ws, wb, wg in rows:
            txt = ru
            if lang == "en" and en:
                txt = en
            elif lang == "az" and az:
                txt = az
            out.append((rid, txt, wc, wt, ws, wb, wg))
        return out


def get_answer_weights(answer_id: int) -> Optional[Dict[str, int]]:
    with closing(db_connect()) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT weight_creative, weight_tech, weight_social, weight_business, weight_green
            FROM answers WHERE id=?
        """,
            (answer_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "creative": row[0],
            "tech": row[1],
            "social": row[2],
            "business": row[3],
            "green": row[4],
        }
