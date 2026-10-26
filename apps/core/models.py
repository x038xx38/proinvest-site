from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.fields import StreamField

from .blocks import FooterColumnBlock, LinkBlock, NavItemBlock


@register_setting(icon="cog")
class SiteSettings(BaseGenericSetting):
    """Контакты, соцсети и счётчики — редактируются в CMS, выводятся в шапке и подвале."""

    phone = models.CharField("Телефон", max_length=32, blank=True)
    email = models.EmailField("E-mail", blank=True)
    telegram_url = models.URLField("Telegram", blank=True)
    max_url = models.URLField("MAX", blank=True)
    youtube_url = models.URLField("YouTube", blank=True)
    address = models.CharField("Адрес офиса", max_length=255, blank=True)
    work_hours = models.CharField("Часы работы", max_length=120, blank=True)
    map_embed_url = models.URLField(
        "Карта (адрес для встраивания)",
        max_length=500,
        blank=True,
        help_text='Конструктор Яндекс Карт → «Получить код» → адрес из src="…" в коде iframe',
    )
    regions = models.CharField(
        "География",
        max_length=255,
        blank=True,
        default="Санкт-Петербург, Ленинградская область, Москва и Московская область",
    )
    yandex_metrika_id = models.CharField("ID Яндекс.Метрики", max_length=32, blank=True)
    google_analytics_id = models.CharField("ID Google Analytics (G-…)", max_length=32, blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("phone"),
                FieldPanel("email"),
                FieldPanel("address"),
                FieldPanel("work_hours"),
                FieldPanel("map_embed_url"),
                FieldPanel("regions"),
            ],
            "Контакты",
        ),
        MultiFieldPanel(
            [FieldPanel("telegram_url"), FieldPanel("max_url"), FieldPanel("youtube_url")],
            "Соцсети",
        ),
        MultiFieldPanel(
            [FieldPanel("yandex_metrika_id"), FieldPanel("google_analytics_id")], "Аналитика"
        ),
    ]

    class Meta:
        verbose_name = "Настройки сайта"


@register_setting(icon="list-ul")
class Navigation(BaseGenericSetting):
    """Меню шапки и подвала. Начальные пункты создаёт миграция 0003_navigation_defaults."""

    header_menu = StreamField([("item", NavItemBlock())], verbose_name="Меню в шапке", blank=True)
    header_button = StreamField(
        [("link", LinkBlock())],
        verbose_name="Кнопка в шапке",
        blank=True,
        max_num=1,
        help_text="Ссылка #consultation открывает форму консультации",
    )
    footer_columns = StreamField(
        [("column", FooterColumnBlock())], verbose_name="Колонки подвала", blank=True
    )
    legal_links = StreamField(
        [("link", LinkBlock())], verbose_name="Юридические ссылки в подвале", blank=True
    )

    panels = [
        FieldPanel("header_menu"),
        FieldPanel("header_button"),
        FieldPanel("footer_columns"),
        FieldPanel("legal_links"),
    ]

    class Meta:
        verbose_name = "Навигация"
