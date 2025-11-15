# patch_questions_localization.py
import sqlite3
import os

DB_PATH = os.getenv("CAREER_BOT_DB", "career_bot.db")

QUESTIONS = [
    # order_idx, ru, en, az
    (0,
     "Что тебе интереснее всего делать в проекте?",
     "What is most interesting for you in a project?",
     "Layihədə ən çox nə maraqlıdır?"),
    (1,
     "Какой тип задач тебя заряжает?",
     "What type of tasks energize you?",
     "Səni hansı tapşırıqlar ruhlandırır?"),
    (2,
     "Что проще начать сегодня?",
     "What is easier to start today?",
     "Bu gün nədən başlamaq asandır?"),
    (3,
     "Какой формат команды комфортнее?",
     "What team format is more comfortable?",
     "Hansı komanda formatı rahatdır?"),
    (4,
     "Что для тебя успех через 6 месяцев?",
     "What is a success for you in 6 months?",
     "6 ay sonra uğur sənin üçün nə deməkdir?"),
    (5,
     "Какая среда/инструмент ближе?",
     "Which environment/tool is closer to you?",
     "Hansə mühit/alət sənə yaxındır?"),
    (6,
     "Что легче давалось в школе/вузе?",
     "What was easier for you at school/university?",
     "Məktəbdə/universitetdə nə daha asan idi?"),
    (7,
     "Как относишься к экспериментам и риску?",
     "How do you feel about experiments and risk?",
     "Eksperiment və riskə münasibətin necədir?"),
    (8,
     "Что важнее: влияние или глубина экспертизы?",
     "What is more important: impact or depth of expertise?",
     "Daha vacib nədir: təsir yoxsa ekspertiza dərinliyi?"),
    (9,
     "С чем точно не хочется работать?",
     "What do you definitely not want to work with?",
     "Nə ilə işləmək istəmirsən?"),
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for order_idx, ru, en, az in QUESTIONS:
        # обновляем только если переводов нет или они пустые
        cur.execute(
            """
            UPDATE questions
            SET
              text_en = CASE
                          WHEN text_en IS NULL OR text_en = '' THEN ?
                          ELSE text_en
                        END,
              text_az = CASE
                          WHEN text_az IS NULL OR text_az = '' THEN ?
                          ELSE text_az
                        END
            WHERE order_idx = ?
            """,
            (en, az, order_idx),
        )

    conn.commit()
    conn.close()
    print("Done: questions text_en/text_az updated.")

if __name__ == "__main__":
    main()
