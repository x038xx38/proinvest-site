"""Библиотека блоков для страниц из StreamField: главная, услуги, лендинги.

Каждый блок — отдельная секция страницы со своим шаблоном в templates/blocks/.
"""

from django.core.exceptions import ValidationError
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.images.blocks import ImageChooserBlock

ICON_CHOICES = [
    ("check", "Галочка"),
    ("shield", "Защита"),
    ("chart", "Рост"),
    ("wallet", "Деньги"),
    ("percent", "Процент"),
    ("key", "Ключ"),
    ("clock", "Время"),
    ("document", "Документ"),
    ("users", "Люди"),
    ("building", "Здание"),
    ("box", "Кладовая"),
    ("car", "Машино-место"),
    ("search", "Поиск"),
    ("map-pin", "Локация"),
    ("graduation", "Обучение"),
]

BACKGROUND_CHOICES = [("white", "Белый"), ("surface", "Серый")]

LEAD_TYPE_CHOICES = [
    ("consultation", "Консультация"),
    ("analysis", "Платный анализ объекта"),
    ("course_waitlist", "Предзапись на обучение"),
    ("contact", "Контакт"),
]


class LinkValue(blocks.StructValue):
    @property
    def href(self):
        page = self.get("page")
        if page:
            return page.url
        return self.get("url") or ""


class LinkBlock(blocks.StructBlock):
    """Ссылка на страницу сайта или произвольный адрес (/путь/, https://…, #форма, tel:…)."""

    text = blocks.CharBlock(label="Текст", max_length=80)
    page = blocks.PageChooserBlock(label="Страница", required=False)
    url = blocks.CharBlock(
        label="Или адрес",
        required=False,
        max_length=255,
        help_text="Если страница не выбрана: /uslugi/, https://…, #consultation, tel:+7…",
    )

    def clean(self, value):
        value = super().clean(value)
        if not value.get("page") and not value.get("url"):
            raise StructBlockValidationError(
                block_errors={"url": ValidationError("Выберите страницу или укажите адрес")}
            )
        return value

    class Meta:
        icon = "link"
        value_class = LinkValue
        form_classname = "struct-block link-block"


class OptionalLinkBlock(LinkBlock):
    """Ссылка, которую можно оставить пустой целиком."""

    text = blocks.CharBlock(label="Текст", max_length=80, required=False)

    def clean(self, value):
        if not value.get("text"):
            return blocks.StructBlock.clean(self, value)
        return super().clean(value)


class SectionBlock(blocks.StructBlock):
    """Общие поля секции: заголовок, подзаголовок, фон, якорь."""

    eyebrow = blocks.CharBlock(label="Надзаголовок", required=False, max_length=80)
    title = blocks.CharBlock(label="Заголовок", required=False, max_length=160)
    intro = blocks.TextBlock(label="Подзаголовок", required=False)
    background = blocks.ChoiceBlock(
        label="Фон", choices=BACKGROUND_CHOICES, default="white", required=True
    )
    anchor = blocks.RegexBlock(
        label="Якорь",
        regex=r"^[a-z0-9-]*$",
        required=False,
        error_messages={"invalid": "Только латиница в нижнем регистре, цифры и дефис"},
        help_text="Для ссылок вида #tarify. Латиница, цифры, дефис",
    )


class HeroBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(label="Надзаголовок", required=False, max_length=80)
    title = blocks.CharBlock(label="Заголовок", max_length=160)
    text = blocks.TextBlock(label="Текст", required=False)
    image = ImageChooserBlock(label="Изображение", required=False)
    buttons = blocks.ListBlock(LinkBlock(), label="Кнопки", max_num=2, default=[])
    facts = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("value", blocks.CharBlock(label="Значение", max_length=24)),
                ("label", blocks.CharBlock(label="Подпись", max_length=80)),
            ]
        ),
        label="Цифры",
        max_num=4,
        default=[],
    )

    class Meta:
        icon = "pick"
        label = "Обложка"
        template = "blocks/hero.html"


class BenefitsBlock(SectionBlock):
    columns = blocks.ChoiceBlock(
        label="Колонок", choices=[("2", "2"), ("3", "3"), ("4", "4")], default="3"
    )
    items = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("icon", blocks.ChoiceBlock(label="Иконка", choices=ICON_CHOICES, default="check")),
                ("title", blocks.CharBlock(label="Заголовок", max_length=120)),
                ("text", blocks.TextBlock(label="Текст", required=False)),
            ]
        ),
        label="Пункты",
        min_num=1,
    )

    class Meta:
        icon = "tick-inverse"
        label = "Выгоды"
        template = "blocks/benefits.html"


class StepsBlock(SectionBlock):
    items = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("title", blocks.CharBlock(label="Этап", max_length=120)),
                ("text", blocks.TextBlock(label="Описание", required=False)),
            ]
        ),
        label="Этапы",
        min_num=1,
    )

    class Meta:
        icon = "list-ol"
        label = "Этапы работы"
        template = "blocks/steps.html"


class PricingBlock(SectionBlock):
    plans = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("name", blocks.CharBlock(label="Название", max_length=80)),
                ("price", blocks.CharBlock(label="Цена", max_length=40, help_text="от 30 000 ₽")),
                ("old_price", blocks.CharBlock(label="Старая цена", max_length=40, required=False)),
                ("note", blocks.CharBlock(label="Пояснение к цене", max_length=80, required=False)),
                ("description", blocks.TextBlock(label="Описание", required=False)),
                ("features", blocks.ListBlock(blocks.CharBlock(label="Пункт"), label="Что входит")),
                ("highlighted", blocks.BooleanBlock(label="Выделить", required=False)),
                ("badge", blocks.CharBlock(label="Плашка", max_length=40, required=False)),
                ("button", OptionalLinkBlock(label="Кнопка")),
            ]
        ),
        label="Тарифы",
        min_num=1,
        max_num=4,
    )

    class Meta:
        icon = "doc-full"
        label = "Цены"
        template = "blocks/pricing.html"


class FaqBlock(SectionBlock):
    items = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("question", blocks.CharBlock(label="Вопрос", max_length=255)),
                (
                    "answer",
                    blocks.RichTextBlock(
                        label="Ответ", features=["bold", "italic", "link", "ol", "ul"]
                    ),
                ),
            ]
        ),
        label="Вопросы",
        min_num=1,
    )

    class Meta:
        icon = "help"
        label = "Вопросы и ответы"
        template = "blocks/faq.html"


class CasesBlock(SectionBlock):
    # Этап 2: карточки начнут подтягиваться из страниц кейсов; ручной ввод останется запасным
    cases = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("image", ImageChooserBlock(label="Фото", required=False)),
                ("title", blocks.CharBlock(label="Объект", max_length=120)),
                ("city", blocks.CharBlock(label="Город", max_length=80, required=False)),
                ("budget", blocks.CharBlock(label="Бюджет", max_length=40, required=False)),
                ("yield_text", blocks.CharBlock(label="Доходность", max_length=40, required=False)),
                ("term", blocks.CharBlock(label="Срок", max_length=40, required=False)),
                ("link", OptionalLinkBlock(label="Ссылка")),
            ]
        ),
        label="Кейсы",
        min_num=1,
    )
    more = OptionalLinkBlock(label="Кнопка «Все кейсы»")

    class Meta:
        icon = "folder-open-inverse"
        label = "Кейсы"
        template = "blocks/cases.html"


class RichTextSectionBlock(SectionBlock):
    body = blocks.RichTextBlock(
        label="Текст", features=["h2", "h3", "bold", "italic", "link", "ol", "ul", "hr"]
    )

    class Meta:
        icon = "doc-full-inverse"
        label = "Текст"
        template = "blocks/rich_text.html"


class CtaBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Заголовок", max_length=160)
    text = blocks.TextBlock(label="Текст", required=False)
    button = LinkBlock(label="Кнопка")
    style = blocks.ChoiceBlock(
        label="Оформление", choices=[("accent", "Жёлтый"), ("dark", "Тёмный")], default="accent"
    )

    class Meta:
        icon = "pick"
        label = "Призыв к действию"
        template = "blocks/cta.html"


class LeadFormBlock(SectionBlock):
    lead_type = blocks.ChoiceBlock(
        label="Тип заявки", choices=LEAD_TYPE_CHOICES, default="consultation"
    )
    bullets = blocks.ListBlock(
        blocks.CharBlock(label="Пункт"), label="Что получит клиент", default=[]
    )
    button_text = blocks.CharBlock(label="Текст кнопки", default="Отправить заявку", max_length=40)

    class Meta:
        icon = "form"
        label = "Форма заявки"
        template = "blocks/lead_form.html"


class SectionsBlock(blocks.StreamBlock):
    hero = HeroBlock()
    benefits = BenefitsBlock()
    steps = StepsBlock()
    pricing = PricingBlock()
    cases = CasesBlock()
    faq = FaqBlock()
    text = RichTextSectionBlock()
    cta = CtaBlock()
    lead_form = LeadFormBlock()


# Меню сайта (настройка «Навигация»)


class NavItemBlock(LinkBlock):
    children = blocks.ListBlock(LinkBlock(), label="Подпункты", default=[])

    class Meta:
        icon = "list-ul"
        label = "Пункт меню"


class FooterColumnBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Заголовок", max_length=60, required=False)
    links = blocks.ListBlock(LinkBlock(), label="Ссылки")

    class Meta:
        icon = "list-ul"
        label = "Колонка"
