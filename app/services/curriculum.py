"""Навчальний план англійської A1–A2.

Кожен юніт — це структурований урок: лексика, граматика, комунікативні фрази,
цілі та банк питань для перевірки знань. Контент статичний (офлайн, детерміновано),
а прогрес користувача та результати тестів зберігаються в SQLite (див. db.py).
"""

UNITS: list[dict] = [
    {
        "id": "a1_01_greetings",
        "level": "A1",
        "order": 1,
        "title": "Greetings & Introductions",
        "title_uk": "Вітання та знайомство",
        "topic": "Meeting people, saying hello and goodbye, telling your name and country.",
        "topic_uk": "Знайомство, привітання та прощання, як сказати своє ім'я та країну.",
        "goals": ["Greet and say goodbye", "Tell and ask names", "Say where you are from"],
        "goals_uk": ["Вітатися та прощатися", "Назвати і запитати ім'я", "Сказати, звідки ти"],
        "grammar": "Verb 'to be' (am / is / are); subject pronouns (I, you, he, she, it, we, they).",
        "grammar_uk": "Дієслово 'to be' (am / is / are); особові займенники.",
        "vocabulary": [
            {"en": "hello", "uk": "привіт"}, {"en": "good morning", "uk": "доброго ранку"},
            {"en": "good night", "uk": "надобраніч"}, {"en": "goodbye", "uk": "до побачення"},
            {"en": "name", "uk": "ім'я"}, {"en": "country", "uk": "країна"},
            {"en": "friend", "uk": "друг"}, {"en": "please", "uk": "будь ласка"},
            {"en": "thank you", "uk": "дякую"},
            {"en": "nice to meet you", "uk": "приємно познайомитись"},
        ],
        "phrases": [
            {"en": "Hello! My name is Anna.", "uk": "Привіт! Мене звуть Анна."},
            {"en": "What is your name?", "uk": "Як тебе звати?"},
            {"en": "I am from Ukraine.", "uk": "Я з України."},
            {"en": "Where are you from?", "uk": "Звідки ти?"},
            {"en": "Goodbye, see you tomorrow!", "uk": "До побачення, до завтра!"},
        ],
        "quiz": [
            {"type": "mc", "q": "Choose the correct form: 'I ___ from Kyiv.'",
             "options": ["am", "is", "are", "be"], "answer": 0,
             "explain_uk": "З займенником 'I' завжди вживаємо 'am'."},
            {"type": "mc", "q": "What does 'How are you?' mean?",
             "options": ["Як тебе звати?", "Як справи?", "Звідки ти?", "Скільки тобі років?"], "answer": 1,
             "explain_uk": "'How are you?' — це 'Як справи?'."},
            {"type": "fill", "q": "She ___ my friend. (be)",
             "answer": "is", "explain_uk": "З 'he/she/it' вживаємо 'is'."},
            {"type": "translate_uk_en", "q": "До побачення!",
             "answer": "goodbye", "explain_uk": "'До побачення' — 'goodbye' або 'bye'."},
            {"type": "translate_en_uk", "q": "Good morning",
             "answer": "доброго ранку", "explain_uk": "'Good morning' — 'Доброго ранку'."},
        ],
    },
    {
        "id": "a1_02_numbers_family",
        "level": "A1",
        "order": 2,
        "title": "Numbers, Age & Family",
        "title_uk": "Числа, вік і родина",
        "topic": "Counting, saying your age, and talking about family members.",
        "topic_uk": "Лічба, як сказати свій вік і розповісти про членів родини.",
        "goals": ["Count and say numbers", "Say your age", "Name family members"],
        "goals_uk": ["Рахувати й називати числа", "Сказати свій вік", "Назвати членів родини"],
        "grammar": "Verb 'have got' / 'have'; possessive adjectives (my, your, his, her); question 'How old'.",
        "grammar_uk": "Have/have got (мати); присвійні займенники; питання 'How old' (про вік).",
        "vocabulary": [
            {"en": "one", "uk": "один"}, {"en": "two", "uk": "два"}, {"en": "three", "uk": "три"},
            {"en": "ten", "uk": "десять"}, {"en": "twenty", "uk": "двадцять"},
            {"en": "mother", "uk": "мати"}, {"en": "father", "uk": "батько"},
            {"en": "sister", "uk": "сестра"}, {"en": "brother", "uk": "брат"},
            {"en": "family", "uk": "родина"}, {"en": "old", "uk": "вік / старий"},
        ],
        "phrases": [
            {"en": "I am twenty-five years old.", "uk": "Мені двадцять п'ять років."},
            {"en": "How old are you?", "uk": "Скільки тобі років?"},
            {"en": "I have got one brother.", "uk": "У мене один брат."},
            {"en": "This is my mother.", "uk": "Це моя мама."},
            {"en": "My family is big.", "uk": "Моя родина велика."},
        ],
        "quiz": [
            {"type": "mc", "q": "'How old are you?' asks about…",
             "options": ["your name", "your age", "your country", "your job"], "answer": 1,
             "explain_uk": "'How old' — питання про вік."},
            {"type": "fill", "q": "I ___ got a sister. (have)",
             "answer": "have", "explain_uk": "З 'I' — 'I have got'."},
            {"type": "fill", "q": "This is ___ father. (він)",
             "answer": "his", "explain_uk": "'his' = його."},
            {"type": "translate_uk_en", "q": "сестра",
             "answer": "sister", "explain_uk": "'сестра' — 'sister'."},
            {"type": "mc", "q": "Choose: 'She ___ ten years old.'",
             "options": ["have", "has", "is", "are"], "answer": 2,
             "explain_uk": "Для віку вживаємо 'to be': 'She is ten'."},
            {"type": "translate_en_uk", "q": "twenty",
             "answer": "двадцять", "explain_uk": "'twenty' = 20, 'двадцять'."},
        ],
    },
    {
        "id": "a1_03_things_colors",
        "level": "A1",
        "order": 3,
        "title": "Everyday Things & Colors",
        "title_uk": "Побутові речі та кольори",
        "topic": "Naming objects around you, colors, this/that and plurals.",
        "topic_uk": "Назви предметів навколо, кольори, this/that та множина.",
        "goals": ["Name objects and colors", "Use this/that", "Form plurals"],
        "goals_uk": ["Називати предмети та кольори", "Вживати this/that", "Утворювати множину"],
        "grammar": "Demonstratives (this/that/these/those); plural nouns (-s / -es).",
        "grammar_uk": "Вказівні займенники this/that/these/those; множина іменників (-s/-es).",
        "vocabulary": [
            {"en": "book", "uk": "книга"}, {"en": "phone", "uk": "телефон"},
            {"en": "table", "uk": "стіл"}, {"en": "chair", "uk": "стілець"},
            {"en": "door", "uk": "двері"}, {"en": "window", "uk": "вікно"},
            {"en": "red", "uk": "червоний"}, {"en": "blue", "uk": "синій"},
            {"en": "green", "uk": "зелений"}, {"en": "white", "uk": "білий"},
        ],
        "phrases": [
            {"en": "What is this?", "uk": "Що це?"},
            {"en": "This is a book.", "uk": "Це книга."},
            {"en": "That is my phone.", "uk": "То мій телефон."},
            {"en": "The door is white.", "uk": "Двері білі."},
            {"en": "These are my books.", "uk": "Це мої книги."},
        ],
        "quiz": [
            {"type": "mc", "q": "Plural of 'book':",
             "options": ["bookes", "books", "bookies", "book"], "answer": 1,
             "explain_uk": "Множина: просто додаємо -s → books."},
            {"type": "fill", "q": "___ is a table. (цей, близько)",
             "answer": "this", "explain_uk": "'this' — для близького одного предмета."},
            {"type": "fill", "q": "The apple is ___. (червоний)",
             "answer": "red", "explain_uk": "'red' — червоний."},
            {"type": "translate_en_uk", "q": "window",
             "answer": "вікно", "explain_uk": "'window' — вікно."},
            {"type": "mc", "q": "'These are…' відповідає за:",
             "options": ["один предмет близько", "багато предметів близько", "один далеко", "багато далеко"],
             "answer": 1, "explain_uk": "'these' — багато предметів поруч."},
            {"type": "translate_uk_en", "q": "стілець",
             "answer": "chair", "explain_uk": "'стілець' — 'chair'."},
        ],
    },
    {
        "id": "a1_04_food_drink",
        "level": "A1",
        "order": 4,
        "title": "Food & Drink",
        "title_uk": "Їжа та напої",
        "topic": "Ordering food and drinks, likes and dislikes, a/an, some.",
        "topic_uk": "Замовлення їжі та напоїв, уподобання, артиклі a/an, some.",
        "goals": ["Order food and drinks", "Say what you like", "Use a/an correctly"],
        "goals_uk": ["Замовляти їжу та напої", "Сказати, що тобі подобається", "Правильно вживати a/an"],
        "grammar": "Articles a/an; 'I like / I don't like'; 'I'd like' for ordering; countable/uncountable basics.",
        "grammar_uk": "Артиклі a/an; 'I like / I don't like'; 'I'd like' для замовлення.",
        "vocabulary": [
            {"en": "water", "uk": "вода"}, {"en": "coffee", "uk": "кава"},
            {"en": "tea", "uk": "чай"}, {"en": "bread", "uk": "хліб"},
            {"en": "apple", "uk": "яблуко"}, {"en": "milk", "uk": "молоко"},
            {"en": "chicken", "uk": "курка"}, {"en": "rice", "uk": "рис"},
            {"en": "I'd like", "uk": "я б хотів"}, {"en": "menu", "uk": "меню"},
        ],
        "phrases": [
            {"en": "I'd like a coffee, please.", "uk": "Я б хотів каву, будь ласка."},
            {"en": "I like tea, but I don't like milk.", "uk": "Я люблю чай, але не люблю молоко."},
            {"en": "Can I have the menu?", "uk": "Можна меню?"},
            {"en": "An apple, please.", "uk": "Одне яблуко, будь ласка."},
            {"en": "I am hungry.", "uk": "Я голодний."},
        ],
        "quiz": [
            {"type": "mc", "q": "Choose: 'I'd like ___ sandwich.'",
             "options": ["a", "an", "some", "the"], "answer": 0,
             "explain_uk": "'a' перед приголосним звуком: a sandwich."},
            {"type": "fill", "q": "I'd like ___ orange juice. (an)",
             "answer": "some", "explain_uk": "Необчислювані рідини: 'some orange juice'."},
            {"type": "fill", "q": "I ___ like coffee. (не любити)",
             "answer": "don't", "explain_uk": "Заперечення: 'I don't like'."},
            {"type": "translate_en_uk", "q": "bread",
             "answer": "хліб", "explain_uk": "'bread' — хліб."},
            {"type": "mc", "q": "'I am thirsty' means:",
             "options": ["я голодний", "я хочу спати", "я хочу пити", "я втомився"], "answer": 2,
             "explain_uk": "'thirsty' — хоче пити, 'hungry' — голодний."},
            {"type": "translate_uk_en", "q": "вода",
             "answer": "water", "explain_uk": "'вода' — 'water'."},
        ],
    },
    {
        "id": "a2_01_daily_routine",
        "level": "A2",
        "order": 5,
        "title": "Daily Routine & Time",
        "title_uk": "Щоденна рутина та час",
        "topic": "Talking about your day, telling the time, adverbs of frequency.",
        "topic_uk": "Розповідь про свій день, як називати час, прислівники частоти.",
        "goals": ["Describe your daily routine", "Tell the time", "Use present simple with he/she"],
        "goals_uk": ["Описати щоденну рутину", "Називати час", "Вживати present simple з he/she"],
        "grammar": "Present Simple (3rd person -s); adverbs of frequency (always, usually, often, never); prepositions of time (at, on, in).",
        "grammar_uk": "Present Simple (3-я особа -s); прислівники частоти; прийменники часу (at, on, in).",
        "vocabulary": [
            {"en": "morning", "uk": "ранок"}, {"en": "evening", "uk": "вечір"},
            {"en": "usually", "uk": "зазвичай"}, {"en": "never", "uk": "ніколи"},
            {"en": "sometimes", "uk": "іноді"}, {"en": "always", "uk": "завжди"},
            {"en": "wake up", "uk": "прокидатися"}, {"en": "go to work", "uk": "йти на роботу"},
            {"en": "every day", "uk": "щодня"}, {"en": "o'clock", "uk": "година"},
        ],
        "phrases": [
            {"en": "I usually wake up at seven o'clock.", "uk": "Я зазвичай прокидаюся о сьомій."},
            {"en": "She works in an office.", "uk": "Вона працює в офісі."},
            {"en": "He doesn't like coffee.", "uk": "Він не любить каву."},
            {"en": "I never watch TV in the morning.", "uk": "Я ніколи не дивлюся ТВ вранці."},
            {"en": "What time is it?", "uk": "Котра година?"},
        ],
        "quiz": [
            {"type": "mc", "q": "Choose: 'He ___ to school every day.'",
             "options": ["go", "goes", "going", "gone"], "answer": 1,
             "explain_uk": "З he/she/it додаємо -s: goes."},
            {"type": "fill", "q": "She ___ (not/like) fish. (doesn't)",
             "answer": "doesn't like", "explain_uk": "Заперечення в 3-й особі: doesn't + дієслово."},
            {"type": "fill", "q": "I get up ___ 7 o'clock. (прийменник часу)",
             "answer": "at", "explain_uk": "Для точного часу вживаємо 'at'."},
            {"type": "translate_en_uk", "q": "always",
             "answer": "завжди", "explain_uk": "'always' — завжди."},
            {"type": "mc", "q": "'Sometimes' означає частоту:",
             "options": ["ніколи", "завжди", "іноді", "рідко"], "answer": 2,
             "explain_uk": "'sometimes' — іноді."},
            {"type": "translate_uk_en", "q": "прокидатися",
             "answer": "wake up", "explain_uk": "'прокидатися' — 'wake up'."},
        ],
    },
    {
        "id": "a2_02_past_simple",
        "level": "A2",
        "order": 6,
        "title": "Past Simple (My Weekend)",
        "title_uk": "Past Simple (мої вихідні)",
        "topic": "Talking about finished actions in the past; regular and irregular verbs.",
        "topic_uk": "Розповідь про завершені дії в минулому; правильні та неправильні дієслова.",
        "goals": ["Talk about the past", "Use past simple (was/were, -ed)", "Use common irregular verbs"],
        "goals_uk": ["Розповідати про минуле", "Вживати past simple (was/were, -ed)", "Вживати неправильні дієслова"],
        "grammar": "Past Simple: regular verbs + -ed; was/were; irregular verbs (go→went, see→saw, have→had); negatives with didn't.",
        "grammar_uk": "Past Simple: правильні дієслова + -ed; was/were; неправильні (go→went, see→saw); заперечення з didn't.",
        "vocabulary": [
            {"en": "yesterday", "uk": "вчора"}, {"en": "last week", "uk": "минулого тижня"},
            {"en": "went", "uk": "пішов / поїхав"}, {"en": "saw", "uk": "бачив / побачив"},
            {"en": "visited", "uk": "відвідав"}, {"en": "was", "uk": "був"},
            {"en": "were", "uk": "були"}, {"en": "watched", "uk": "дивився"},
            {"en": "had", "uk": "мав"}, {"en": "weekend", "uk": "вихідні"},
        ],
        "phrases": [
            {"en": "Yesterday I went to the park.", "uk": "Вчора я пішов у парк."},
            {"en": "We were at home last weekend.", "uk": "Минулих вихідних ми були вдома."},
            {"en": "I didn't watch the film.", "uk": "Я не дивився фільм."},
            {"en": "She saw her friends on Friday.", "uk": "Вона бачила друзів у п'ятницю."},
            {"en": "What did you do last Sunday?", "uk": "Що ти робив минулої неділі?"},
        ],
        "quiz": [
            {"type": "mc", "q": "Past of 'go':",
             "options": ["goed", "went", "gone", "going"], "answer": 1,
             "explain_uk": "'go' — неправильне: went."},
            {"type": "fill", "q": "I ___ (watch) TV yesterday. (правильне -ed)",
             "answer": "watched", "explain_uk": "watch + ed = watched."},
            {"type": "fill", "q": "She ___ very happy yesterday. (was/were)",
             "answer": "was", "explain_uk": "З 'she' у минулому: was."},
            {"type": "fill", "q": "They ___ (not/go) to school. (заперечення)",
             "answer": "didn't go", "explain_uk": "Заперечення: didn't + початкова форма go."},
            {"type": "translate_en_uk", "q": "last week",
             "answer": "минулого тижня", "explain_uk": "'last week' — минулого тижня."},
            {"type": "mc", "q": "Past of 'see':",
             "options": ["seed", "saw", "seen", "sawed"], "answer": 1,
             "explain_uk": "'see' — неправильне: saw."},
        ],
    },
]




# ---------------------------------------------------------------------------
# Допоміжні функції навчального плану та перевірки знань
# ---------------------------------------------------------------------------

def _norm(text) -> str:
    """Нормалізація відповіді для порівняння: нижній регістр, без пунктуації,
    схлопнуті пробіли."""
    return " ".join(str(text).lower().strip().strip(".,!?;:\"'()«»").split())


def all_units() -> list[dict]:
    return sorted(UNITS, key=lambda u: u["order"])


def get_unit(unit_id: str) -> dict | None:
    for u in UNITS:
        if u["id"] == unit_id:
            return u
    return None


def units_by_level(level: str) -> list[dict]:
    lvl = level.upper()
    return [u for u in all_units() if u["level"].upper() == lvl]


def curriculum_overview() -> dict:
    """Список юнітів без повного контенту — для екрана «Навчання»."""
    return {
        "levels": ["A1", "A2"],
        "units": [
            {
                "id": u["id"],
                "level": u["level"],
                "order": u["order"],
                "title": u["title"],
                "title_uk": u["title_uk"],
                "topic_uk": u["topic_uk"],
                "goals_uk": u.get("goals_uk", []),
                "quiz_count": len(u.get("quiz", [])),
            }
            for u in all_units()
        ],
    }


def grade_question(q: dict, given) -> bool:
    """Перевірка однієї відповіді користувача на одне питання."""
    qtype = q.get("type", "mc")
    if qtype == "mc":
        try:
            return int(given) == int(q["answer"])
        except (TypeError, ValueError):
            return False
    # текстові типи: fill / translate_uk_en / translate_en_uk
    return _norm(given) == _norm(q["answer"])


def grade_quiz(unit_id: str, answers: list) -> dict | None:
    """Перевіряє тест юніта. answers — список відповідей (по одній на питання),
    у тому ж порядку, що й у unit['quiz']. Повертає детальний результат."""
    unit = get_unit(unit_id)
    if not unit:
        return None
    quiz = unit.get("quiz", [])
    per_question, correct = [], 0
    for i, q in enumerate(quiz):
        given = answers[i] if i < len(answers) else None
        ok = grade_question(q, given)
        correct += 1 if ok else 0
        item = {
            "index": i,
            "type": q.get("type", "mc"),
            "q": q.get("q", ""),
            "correct": ok,
            "given": given,
            "expected": q["answer"],
            "explain_uk": q.get("explain_uk", ""),
        }
        if q.get("type") == "mc":
            item["options"] = q.get("options", [])
        per_question.append(item)
    total = len(quiz)
    percent = round(100 * correct / total) if total else 0
    return {
        "unit_id": unit_id,
        "total": total,
        "correct": correct,
        "score_percent": percent,
        "passed": total > 0 and percent >= 80,
        "per_question": per_question,
    }


def quiz_payload(unit_id: str) -> dict | None:
    """Питання тесту БЕЗ правильних відповідей (щоб клієнт не бачив answer)."""
    unit = get_unit(unit_id)
    if not unit:
        return None
    return {
        "unit_id": unit_id,
        "level": unit["level"],
        "title": unit["title"],
        "title_uk": unit["title_uk"],
        "questions": [
            {
                "index": i,
                "type": q.get("type", "mc"),
                "q": q.get("q", ""),
                "options": q.get("options", []) if q.get("type") == "mc" else None,
            }
            for i, q in enumerate(unit.get("quiz", []))
        ],
    }




