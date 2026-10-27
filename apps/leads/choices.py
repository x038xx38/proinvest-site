"""Типы заявок. Отдельно от моделей: их импортирует библиотека блоков (apps.core.blocks)."""

from django.db import models


class LeadType(models.TextChoices):
    CONSULTATION = "consultation", "Консультация"
    ANALYSIS = "analysis", "Платный анализ объекта"
    COURSE_WAITLIST = "course_waitlist", "Предзапись на обучение"
    CONTACT = "contact", "Контакт"
