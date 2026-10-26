"""Демо-данные для /styleguide/: витрина блоков и макеты главной и страницы услуги.

Тексты и цифры — заглушки для проверки вёрстки, не данные компании.
"""


def link(text, url):
    return {"text": text, "page": None, "url": url}


def rich(*paragraphs):
    return "".join(f"<p>{p}</p>" for p in paragraphs)


HERO_HOME = {
    "eyebrow": "Кладовые и машино-места",
    "title": "Инвестиции в малую недвижимость под ключ",
    "text": "Подберём объект под ваш бюджет, сдадим в аренду и возьмём управление на себя. "
    "Или научим делать это самостоятельно.",
    "image": None,
    "buttons": [link("Бесплатная консультация", "#consultation"), link("Обучение", "/obuchenie/")],
    "facts": [
        {"value": "от 500 тыс. ₽", "label": "порог входа"},
        {"value": "12–18 %", "label": "доходность годовых"},
        {"value": "4 региона", "label": "СПб, ЛО, Москва, МО"},
        {"value": "100+", "label": "подобранных объектов"},
    ],
}

DIRECTIONS = {
    "eyebrow": "Направления",
    "title": "Чем помогаем инвестору",
    "intro": "",
    "background": "white",
    "anchor": "",
    "columns": "3",
    "items": [
        {
            "icon": "search",
            "title": "Инвестиционный подбор",
            "text": "Найдём кладовую или машино-место под задачу: аренда или перепродажа.",
        },
        {
            "icon": "key",
            "title": "Управление",
            "text": "Приёмка, поиск арендаторов, договоры и контроль оплат — целиком "
            "или по задачам.",
        },
        {
            "icon": "graduation",
            "title": "Обучение",
            "text": "Практический курс: как самому выбирать объекты и считать доходность.",
        },
    ],
}

BENEFITS = {
    "eyebrow": "",
    "title": "Почему кладовые и машино-места",
    "intro": "Низкий порог входа и понятный спрос в новостройках крупных городов.",
    "background": "surface",
    "anchor": "",
    "columns": "4",
    "items": [
        {"icon": "wallet", "title": "Низкий порог входа", "text": "Дешевле квартиры в разы."},
        {"icon": "chart", "title": "Стабильный спрос", "text": "Жильцы новостроек ищут место."},
        {"icon": "shield", "title": "Минимум рисков", "text": "Нет ремонта и износа мебели."},
        {"icon": "clock", "title": "Мало времени", "text": "Управление можно передать нам."},
    ],
}

STEPS = {
    "eyebrow": "Как работаем",
    "title": "Этапы подбора",
    "intro": "",
    "background": "white",
    "anchor": "",
    "items": [
        {"title": "Знакомство", "text": "Обсуждаем бюджет, цели и сроки."},
        {"title": "Анализ рынка", "text": "Отбираем объекты, считаем доходность каждого."},
        {"title": "Сделка", "text": "Проверяем документы и сопровождаем покупку."},
        {"title": "Сдача в аренду", "text": "Находим арендатора или передаём объект вам."},
    ],
}

PRICING = {
    "eyebrow": "Стоимость",
    "title": "Тарифы на подбор",
    "intro": "",
    "background": "surface",
    "anchor": "tarify",
    "plans": [
        {
            "name": "Консультация",
            "price": "5 000 ₽",
            "old_price": "",
            "note": "60 минут онлайн",
            "description": "Разберём вашу ситуацию и ответим на вопросы.",
            "features": ["Разбор бюджета и целей", "Оценка 1–2 объектов", "Запись встречи"],
            "highlighted": False,
            "badge": "",
            "button": link("Записаться", "#consultation"),
        },
        {
            "name": "Подбор объекта",
            "price": "от 40 000 ₽",
            "old_price": "50 000 ₽",
            "note": "за объект",
            "description": "Найдём и проверим объект, сопроводим сделку.",
            "features": [
                "Подборка 5–10 объектов",
                "Расчёт доходности",
                "Проверка документов",
                "Сопровождение сделки",
            ],
            "highlighted": True,
            "badge": "Популярный",
            "button": link("Оставить заявку", "#consultation"),
        },
        {
            "name": "Подбор + управление",
            "price": "по запросу",
            "old_price": "",
            "note": "",
            "description": "Под ключ: от выбора объекта до ежемесячного дохода.",
            "features": ["Всё из «Подбора»", "Поиск арендатора", "Контроль оплат"],
            "highlighted": False,
            "badge": "",
            "button": link("Обсудить", "#consultation"),
        },
    ],
}


def case(title, city, budget, yield_text, term):
    return {
        "image": None,
        "title": title,
        "city": city,
        "budget": budget,
        "yield_text": yield_text,
        "term": term,
        "link": link("Подробнее", "/kejsy/"),
    }


CASES = {
    "eyebrow": "Кейсы",
    "title": "Объекты, которые мы подобрали",
    "intro": "",
    "background": "white",
    "anchor": "",
    "cases": [
        case("Кладовая 4 м² в ЖК бизнес-класса", "Санкт-Петербург", "620 000 ₽", "14 %", "3 нед."),
        case("Машино-место в паркинге у метро", "Москва", "1 900 000 ₽", "11 %", "1 мес."),
        case("Две кладовые под перепродажу", "Ленинградская обл.", "980 000 ₽", "+32 %", "8 мес."),
    ],
    "more": link("Все кейсы", "/kejsy/"),
}

FAQ = {
    "eyebrow": "",
    "title": "Вопросы и ответы",
    "intro": "",
    "background": "surface",
    "anchor": "faq",
    "items": [
        {
            "question": "Сколько нужно денег, чтобы начать?",
            "answer": rich("Кладовые в новостройках начинаются примерно от 500 тысяч рублей."),
        },
        {
            "question": "Можно ли купить объект в ипотеку?",
            "answer": rich(
                "Да, часть банков кредитует нежилые помещения.",
                "Подскажем, где условия лучше.",
            ),
        },
        {
            "question": "Кто будет искать арендатора?",
            "answer": rich("Можем взять это на себя в рамках услуги «Управление»."),
        },
    ],
}

CTA = {
    "title": "Не знаете, с чего начать?",
    "text": "Расскажите о бюджете и целях — предложим подходящий формат.",
    "button": link("Получить консультацию", "#consultation"),
    "style": "accent",
}

CTA_DARK = {**CTA, "title": "Хотите разобраться сами?", "style": "dark"}
CTA_DARK["button"] = link("Смотреть программу курса", "/obuchenie/")

LEAD_FORM = {
    "eyebrow": "Консультация",
    "title": "Обсудим вашу задачу",
    "intro": "Оставьте контакты — перезвоним и ответим на вопросы. Это бесплатно.",
    "background": "surface",
    "anchor": "consultation",
    "lead_type": "consultation",
    "bullets": [
        "Оценим, подходит ли вам этот формат инвестиций",
        "Подскажем реалистичную доходность в вашем бюджете",
        "Расскажем, как устроена работа с нами",
    ],
    "button_text": "Получить консультацию",
}

TEXT = {
    "eyebrow": "",
    "title": "Об услуге",
    "intro": "",
    "background": "white",
    "anchor": "",
    "body": "<p>Инвестиционный подбор — это поиск объекта под вашу задачу. "
    "Мы анализируем рынок, считаем доходность и проверяем документы.</p>"
    "<h3>Что вы получаете</h3><ul><li>Подборку объектов с расчётами</li>"
    "<li>Проверку застройщика и документов</li><li>Сопровождение сделки</li></ul>",
}

HERO_SERVICE = {
    **HERO_HOME,
    "eyebrow": "Услуги",
    "title": "Инвестиционный подбор кладовых и машино-мест",
    "text": "Найдём объект под ваш бюджет и цель: стабильная аренда или перепродажа.",
    "buttons": [link("Оставить заявку", "#consultation"), link("Тарифы", "#tarify")],
    "facts": [],
}


def stream(*blocks):
    return [{"type": name, "value": value} for name, value in blocks]


PAGES = {
    "blocks": (
        "Все блоки",
        stream(
            ("hero", HERO_HOME),
            ("benefits", DIRECTIONS),
            ("benefits", BENEFITS),
            ("steps", STEPS),
            ("pricing", PRICING),
            ("cases", CASES),
            ("text", TEXT),
            ("faq", FAQ),
            ("cta", CTA),
            ("cta", CTA_DARK),
            ("lead_form", LEAD_FORM),
        ),
    ),
    "home": (
        "Макет: главная",
        stream(
            ("hero", HERO_HOME),
            ("benefits", DIRECTIONS),
            ("benefits", BENEFITS),
            ("cases", {**CASES, "background": "white"}),
            ("cta", CTA_DARK),
            ("faq", FAQ),
            ("lead_form", LEAD_FORM),
        ),
    ),
    "service": (
        "Макет: страница услуги",
        stream(
            ("hero", HERO_SERVICE),
            ("text", TEXT),
            ("steps", {**STEPS, "background": "surface"}),
            ("pricing", {**PRICING, "background": "white"}),
            ("cases", {**CASES, "background": "surface"}),
            ("cta", CTA),
            ("faq", {**FAQ, "background": "white"}),
            ("lead_form", LEAD_FORM),
        ),
    ),
}
