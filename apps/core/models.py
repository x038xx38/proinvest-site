from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting


@register_setting(icon="cog")
class SiteSettings(BaseGenericSetting):
    """Контакты, соцсети и счётчики — редактируются в CMS, выводятся в шапке и подвале."""

    phone = models.CharField("Телефон", max_length=32, blank=True)
    email = models.EmailField("E-mail", blank=True)
    telegram_url = models.URLField("Telegram", blank=True)
    max_url = models.URLField("MAX", blank=True)
    youtube_url = models.URLField("YouTube", blank=True)
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
            [FieldPanel("phone"), FieldPanel("email"), FieldPanel("regions")], "Контакты"
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
