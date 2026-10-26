from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from .mixins import BlocksPageMixin


class HomePage(BlocksPageMixin, Page):
    content_panels = [*Page.content_panels, FieldPanel("body")]

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]

    class Meta:
        verbose_name = "Главная"


class ContentPage(BlocksPageMixin, Page):
    """Произвольная страница из блоков: «О проекте», лендинги."""

    intro = models.TextField(
        "Подзаголовок", blank=True, help_text="Показывается, если страница начинается не с обложки"
    )

    content_panels = [*Page.content_panels, FieldPanel("intro"), FieldPanel("body")]

    class Meta:
        verbose_name = "Страница из блоков"
        verbose_name_plural = "Страницы из блоков"


class ContactPage(BlocksPageMixin, Page):
    """Контакты из «Настроек сайта» и карта; ниже — секции (обычно форма заявки)."""

    intro = models.TextField("Подзаголовок", blank=True)

    content_panels = [*Page.content_panels, FieldPanel("intro"), FieldPanel("body")]

    max_count = 1
    parent_page_types = ["pages.HomePage"]

    class Meta:
        verbose_name = "Контакты"


class LegalPage(Page):
    """Политика конфиденциальности, оферта, согласие на обработку данных."""

    updated_at = models.DateField("Редакция от", null=True, blank=True)
    body = RichTextField(
        "Текст",
        features=["h2", "h3", "h4", "bold", "italic", "link", "ol", "ul", "hr", "document-link"],
    )

    content_panels = [*Page.content_panels, FieldPanel("updated_at"), FieldPanel("body")]

    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = "Юридическая страница"
        verbose_name_plural = "Юридические страницы"
