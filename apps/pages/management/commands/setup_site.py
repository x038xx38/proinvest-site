"""Создаёт дерево страниц сайта с начальным наполнением.

Повторный запуск безопасен: существующие страницы не трогаются, создаются только недостающие.
Тексты — черновики для замены материалами клиента.

    python manage.py setup_site           # структура и тексты
    python manage.py setup_site --demo    # плюс демо-кейсы и статьи с пометкой «Демо»
"""

import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.blog.models import ArticlePage, BlogCategory, BlogIndexPage
from apps.cases.models import CaseIndexPage, CasePage
from apps.pages.models import ContactPage, ContentPage, HomePage, LegalPage
from apps.services.models import ServiceIndexPage, ServicePage


def link(text, url):
    return {"text": text, "page": None, "url": url}


def section(**value):
    return {"eyebrow": "", "title": "", "intro": "", "background": "white", "anchor": "", **value}


def lead_form(lead_type="consultation", **value):
    defaults = {
        "eyebrow": "Консультация",
        "title": "Обсудим вашу задачу",
        "intro": "Оставьте контакты — свяжемся и ответим на вопросы. Консультация бесплатная.",
        "background": "surface",
        "anchor": "consultation",
        "bullets": [],
        "button_text": "Отправить заявку",
    }
    return "lead_form", section(**{**defaults, **value, "lead_type": lead_type})


def cases_block(**value):
    return (
        "cases",
        section(
            eyebrow="Кейсы",
            title="Объекты, которые мы подобрали",
            pages=[],
            limit=3,
            cases=[],
            more=link("Все кейсы", "/kejsy/"),
            **value,
        ),
    )


def faq(items, **value):
    return (
        "faq",
        section(
            title="Вопросы и ответы",
            anchor="faq",
            items=[{"question": q, "answer": f"<p>{a}</p>"} for q, a in items],
            **value,
        ),
    )


def stream(*blocks):
    return [{"type": name, "value": value} for name, value in blocks]


HOME_BODY = stream(
    (
        "hero",
        {
            "eyebrow": "Кладовые и машино-места",
            "title": "Инвестиции в малую недвижимость под ключ",
            "text": "Подберём объект под ваш бюджет, сдадим в аренду и возьмём управление на себя. "
            "Или научим делать это самостоятельно.",
            "image": None,
            "buttons": [
                link("Бесплатная консультация", "#consultation"),
                link("Обучение", "/obuchenie/"),
            ],
            "facts": [],
        },
    ),
    (
        "benefits",
        section(
            eyebrow="Направления",
            title="Чем помогаем инвестору",
            columns="3",
            items=[
                {
                    "icon": "search",
                    "title": "Инвестиционный подбор",
                    "text": "Найдём кладовую или машино-место под задачу: аренда или перепродажа.",
                    "link": link("Подробнее", "/uslugi/podbor/"),
                },
                {
                    "icon": "key",
                    "title": "Управление",
                    "text": "Приёмка, поиск арендаторов, договоры и контроль оплат.",
                    "link": link("Подробнее", "/uslugi/upravlenie/"),
                },
                {
                    "icon": "graduation",
                    "title": "Обучение",
                    "text": "Практический курс: как самому выбирать объекты и считать доходность.",
                    "link": link("Подробнее", "/obuchenie/"),
                },
            ],
        ),
    ),
    (
        "benefits",
        section(
            title="Почему кладовые и машино-места",
            intro="Низкий порог входа и устойчивый спрос в новостройках крупных городов.",
            background="surface",
            columns="4",
            items=[
                {"icon": "wallet", "title": "Низкий порог входа", "text": "", "link": link("", "")},
                {"icon": "chart", "title": "Стабильный спрос", "text": "", "link": link("", "")},
                {"icon": "shield", "title": "Простое владение", "text": "", "link": link("", "")},
                {"icon": "clock", "title": "Минимум времени", "text": "", "link": link("", "")},
            ],
        ),
    ),
    cases_block(),
    (
        "steps",
        section(
            eyebrow="Как работаем",
            title="От заявки до дохода",
            background="surface",
            items=[
                {"title": "Знакомство", "text": "Обсуждаем бюджет, цели и сроки."},
                {"title": "Подбор", "text": "Отбираем объекты и считаем доходность."},
                {"title": "Сделка", "text": "Проверяем документы и сопровождаем покупку."},
                {"title": "Доход", "text": "Сдаём объект или передаём его вам."},
            ],
        ),
    ),
    (
        "cta",
        {
            "title": "Хотите разобраться сами?",
            "text": "Курс о том, как выбирать кладовые и машино-места и считать доходность.",
            "button": link("Программа курса", "/obuchenie/"),
            "style": "dark",
        },
    ),
    faq(
        [
            (
                "Сколько нужно денег, чтобы начать?",
                "Зависит от города и объекта — подскажем на консультации.",
            ),
            (
                "Можно ли купить объект в ипотеку?",
                "Часть банков кредитует нежилые помещения — расскажем, где условия лучше.",
            ),
            (
                "Кто будет искать арендатора?",
                "Можем взять это на себя в рамках услуги «Управление».",
            ),
        ]
    ),
    lead_form(),
)


def service_body(title, text, steps, faq_items):
    return stream(
        (
            "hero",
            {
                "eyebrow": "Услуги",
                "title": title,
                "text": text,
                "image": None,
                "buttons": [link("Оставить заявку", "#consultation"), link("Стоимость", "#tarify")],
                "facts": [],
            },
        ),
        (
            "steps",
            section(
                eyebrow="Как работаем",
                title="Этапы",
                background="surface",
                items=[{"title": t, "text": d} for t, d in steps],
            ),
        ),
        (
            "pricing",
            section(
                eyebrow="Стоимость",
                title="Тарифы",
                anchor="tarify",
                plans=[
                    {
                        "name": "Консультация",
                        "price": "по запросу",
                        "old_price": "",
                        "note": "",
                        "description": "Разберём вашу ситуацию и ответим на вопросы.",
                        "features": ["Разбор бюджета и целей", "Ответы на вопросы"],
                        "highlighted": False,
                        "badge": "",
                        "button": link("Записаться", "#consultation"),
                    },
                    {
                        "name": "Под ключ",
                        "price": "по запросу",
                        "old_price": "",
                        "note": "",
                        "description": "Полное сопровождение от начала до результата.",
                        "features": ["Все этапы работы", "Отчёты и расчёты"],
                        "highlighted": True,
                        "badge": "",
                        "button": link("Оставить заявку", "#consultation"),
                    },
                ],
            ),
        ),
        cases_block(background="surface"),
        faq(faq_items),
        lead_form(),
    )


SERVICES = [
    {
        "title": "Инвестиционный подбор",
        "slug": "podbor",
        "icon": "search",
        "short_description": "Подберём кладовую или машино-место под ваш бюджет и задачу: "
        "аренда или перепродажа.",
        "body": service_body(
            "Инвестиционный подбор кладовых и машино-мест",
            "Найдём объект под ваш бюджет и цель: стабильная аренда или перепродажа.",
            [
                ("Знакомство", "Обсуждаем бюджет, цели и сроки."),
                ("Анализ рынка", "Отбираем объекты, считаем доходность каждого."),
                ("Сделка", "Проверяем документы и сопровождаем покупку."),
                ("Передача", "Передаём объект вам или в управление."),
            ],
            [
                (
                    "Сколько длится подбор?",
                    "Обычно от нескольких недель — зависит от бюджета и требований.",
                ),
                (
                    "Работаете с ипотекой?",
                    "Да, подскажем банки, которые кредитуют нежилые помещения.",
                ),
            ],
        ),
    },
    {
        "title": "Управление",
        "slug": "upravlenie",
        "icon": "key",
        "short_description": "Приёмка, сдача в аренду, поиск арендаторов и контроль оплат — "
        "целиком или по задачам.",
        "body": service_body(
            "Управление кладовыми и машино-местами",
            "Берём на себя приёмку, поиск арендаторов, договоры и контроль оплат.",
            [
                ("Приёмка", "Принимаем объект у застройщика, фиксируем недостатки."),
                ("Подготовка", "Готовим объект и объявление."),
                ("Аренда", "Ищем арендатора и заключаем договор."),
                ("Контроль", "Следим за оплатами и состоянием объекта."),
            ],
            [
                (
                    "Можно передать только часть задач?",
                    "Да, работаем целиком или по отдельным задачам.",
                ),
                ("Как я узнаю о поступлениях?", "Присылаем регулярные отчёты."),
            ],
        ),
    },
]

ABOUT_BODY = stream(
    (
        "text",
        section(
            title="Кто мы",
            body="<p>ПроИнвест помогает инвестировать в кладовые и машино-места: подбирает "
            "объекты, управляет ими и обучает инвесторов.</p>"
            "<p>Работаем в Санкт-Петербурге, Ленинградской области, Москве и Московской "
            "области.</p>",
        ),
    ),
    (
        "benefits",
        section(
            title="Наши принципы",
            background="surface",
            columns="3",
            items=[
                {
                    "icon": "document",
                    "title": "Прозрачные расчёты",
                    "text": "",
                    "link": link("", ""),
                },
                {"icon": "shield", "title": "Проверка объектов", "text": "", "link": link("", "")},
                {
                    "icon": "users",
                    "title": "Личное сопровождение",
                    "text": "",
                    "link": link("", ""),
                },
            ],
        ),
    ),
    lead_form(),
)

LEGAL_PLACEHOLDER = "<p>Текст документа будет опубликован после получения реквизитов.</p>"

DEMO_CASES = [
    (
        "Демо: кладовая в ЖК бизнес-класса",
        "kladovaya",
        "rent",
        "Санкт-Петербург",
        620000,
        "14",
        "3 недели",
        "podbor",
    ),
    (
        "Демо: машино-место у метро",
        "mashinomesto",
        "rent",
        "Москва",
        1900000,
        "11",
        "1 месяц",
        "podbor",
    ),
    (
        "Демо: две кладовые под перепродажу",
        "kladovaya",
        "resale",
        "Ленинградская область",
        980000,
        "32",
        "8 месяцев",
        "upravlenie",
    ),
]

DEMO_ARTICLES = [
    ("Демо: как выбрать кладовую для сдачи в аренду", "kladovye"),
    ("Демо: машино-место как инвестиция", "mashinomesta"),
    ("Демо: налоги при сдаче нежилых помещений", "investicii"),
]

CATEGORIES = [
    ("Кладовые", "kladovye"),
    ("Машино-места", "mashinomesta"),
    ("Инвестиции", "investicii"),
]


class Command(BaseCommand):
    help = "Создаёт структуру страниц сайта с начальным наполнением (повторный запуск безопасен)"

    def add_arguments(self, parser):
        parser.add_argument("--demo", action="store_true", help="Добавить демо-кейсы и статьи")

    @transaction.atomic
    def handle(self, *args, demo=False, **options):
        home = HomePage.objects.get()
        if not home.body:
            home.body = HOME_BODY
            home.save_revision().publish()
            self.log("Главная: секции")

        services = self.child(
            home,
            ServiceIndexPage,
            "uslugi",
            title="Услуги",
            intro="Помогаем на каждом этапе: от выбора объекта до ежемесячного дохода.",
            body=stream(lead_form()),
        )
        for data in SERVICES:
            self.child(
                services,
                ServicePage,
                data["slug"],
                **{k: v for k, v in data.items() if k != "slug"},
            )

        self.child(home, ContentPage, "o-proekte", title="О проекте", body=ABOUT_BODY)
        cases = self.child(
            home,
            CaseIndexPage,
            "kejsy",
            title="Кейсы",
            intro="Объекты, которые мы подобрали и сдали в аренду.",
        )
        blog = self.child(
            home,
            BlogIndexPage,
            "stati",
            title="Статьи",
            intro="О кладовых, машино-местах и инвестициях.",
        )
        self.child(
            home,
            ContactPage,
            "kontakty",
            title="Контакты",
            intro="Позвоните, напишите или оставьте заявку — ответим на вопросы.",
            body=stream(lead_form("contact", title="Напишите нам", eyebrow="", background="white")),
        )
        for slug, title in [
            ("politika", "Политика конфиденциальности"),
            ("oferta", "Договор оферты"),
        ]:
            self.child(home, LegalPage, slug, title=title, body=LEGAL_PLACEHOLDER)

        for order, (name, slug) in enumerate(CATEGORIES):
            BlogCategory.objects.get_or_create(
                slug=slug, defaults={"name": name, "sort_order": order}
            )

        if demo:
            self.create_demo(cases, blog)

    def create_demo(self, cases, blog):
        for i, (title, obj, strategy, city, budget, yld, term, service_slug) in enumerate(
            DEMO_CASES, 1
        ):
            self.child(
                cases,
                CasePage,
                f"demo-{i}",
                title=title,
                object_type=obj,
                strategy=strategy,
                city=city,
                budget=budget,
                yield_percent=yld,
                term=term,
                deal_date=datetime.date(2026, 1 + i, 1),
                service=ServicePage.objects.filter(slug=service_slug).first(),
                summary="Демонстрационный кейс для проверки вёрстки. Замените или удалите.",
            )
        for i, (title, category_slug) in enumerate(DEMO_ARTICLES, 1):
            self.child(
                blog,
                ArticlePage,
                f"demo-{i}",
                title=title,
                date=datetime.date(2026, 10, i),
                category=BlogCategory.objects.get(slug=category_slug),
                excerpt="Демонстрационная статья для проверки вёрстки. Замените или удалите.",
                body=stream(
                    (
                        "paragraph",
                        "<h2>Подзаголовок</h2><p>Текст статьи.</p><ul><li>Пункт</li></ul>",
                    ),
                    ("quote", {"text": "Пример цитаты.", "author": "Автор"}),
                ),
            )

    def child(self, parent, model, slug, **fields):
        existing = parent.get_children().filter(slug=slug).first()
        if existing:
            return existing.specific
        page = model(slug=slug, **fields)
        parent.add_child(instance=page)
        page.save_revision().publish()
        self.log(f"{page.url}: {page.title}")
        return page

    def log(self, message):
        self.stdout.write(f"  + {message}")
