from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page

from apps.pages.mixins import BlocksPageMixin


class CoursePage(BlocksPageMixin, Page):
    """Страница курса из блоков. Потоки, тарифы и оплата добавятся на этапе 4."""

    intro = models.TextField(
        "Подзаголовок", blank=True, help_text="Показывается, если страница начинается не с обложки"
    )

    content_panels = [*Page.content_panels, FieldPanel("intro"), FieldPanel("body")]

    max_count = 1
    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = "Обучение"
