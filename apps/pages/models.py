from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

# Временная заглушка: на этапе 2 карточки строятся из страниц услуг
DIRECTIONS = [
    (
        "Инвестиционный подбор",
        "Подберём кладовую или машино-место под ваш бюджет и задачу: аренда или перепродажа.",
        "/uslugi/podbor/",
    ),
    (
        "Управление",
        "Приёмка, сдача в аренду, поиск арендаторов и контроль оплат — целиком или по задачам.",
        "/uslugi/upravlenie/",
    ),
    (
        "Обучение",
        "Практический курс по подбору объектов малой недвижимости для аренды и перепродажи.",
        "/obuchenie/",
    ),
]


class HomePage(Page):
    """Главная. Блоки направлений и прочие секции появятся на этапе 2."""

    intro = RichTextField("Вступление", blank=True)

    content_panels = [*Page.content_panels, FieldPanel("intro")]

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]

    class Meta:
        verbose_name = "Главная"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["directions"] = DIRECTIONS
        return context
