from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page

from apps.core.blocks import ICON_CHOICES
from apps.pages.mixins import BlocksPageMixin


class ServiceIndexPage(BlocksPageMixin, Page):
    """Раздел «Услуги»: карточки дочерних услуг, ниже — секции."""

    intro = models.TextField("Подзаголовок", blank=True)

    content_panels = [*Page.content_panels, FieldPanel("intro"), FieldPanel("body")]

    max_count = 1
    parent_page_types = ["pages.HomePage"]
    subpage_types = ["services.ServicePage"]

    class Meta:
        verbose_name = "Раздел услуг"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["services"] = ServicePage.objects.child_of(self).live()
        return context


class ServicePage(BlocksPageMixin, Page):
    """Направление или услуга. Внутри направления могут быть отдельные услуги."""

    short_description = models.TextField(
        "Краткое описание", blank=True, help_text="Для карточки в списке услуг"
    )
    icon = models.CharField("Иконка", max_length=20, choices=ICON_CHOICES, default="check")
    card_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Картинка для карточки",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = [
        *Page.content_panels,
        MultiFieldPanel(
            [FieldPanel("short_description"), FieldPanel("icon"), FieldPanel("card_image")],
            "Карточка",
        ),
        FieldPanel("body"),
    ]

    parent_page_types = ["services.ServiceIndexPage", "services.ServicePage"]
    subpage_types = ["services.ServicePage"]

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["subservices"] = ServicePage.objects.child_of(self).live()
        return context
