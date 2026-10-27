from django.db import models

from .choices import LeadType


class Lead(models.Model):
    """Заявка с формы сайта. UTM, ответственный и история статусов — этап 3."""

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Обработана"
        SPAM = "spam", "Спам"

    lead_type = models.CharField(
        "Тип", max_length=20, choices=LeadType.choices, default=LeadType.CONSULTATION
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.NEW, db_index=True
    )
    name = models.CharField("Имя", max_length=100)
    contact = models.CharField("Телефон или Telegram", max_length=100)
    comment = models.TextField("Комментарий", max_length=2000, blank=True)
    page = models.ForeignKey(
        "wagtailcore.Page",
        verbose_name="Страница",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    page_url = models.CharField("Адрес страницы", max_length=500, blank=True)
    consent_at = models.DateTimeField("Согласие на обработку ПД получено")
    consent_document = models.CharField(
        "Текст согласия", max_length=500, blank=True, help_text="Адрес страницы согласия"
    )
    ip = models.GenericIPAddressField("IP-адрес", null=True, blank=True)
    user_agent = models.CharField("Браузер", max_length=300, blank=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"{self.name} — {self.get_lead_type_display()}"
