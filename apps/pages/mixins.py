from django.db import models
from wagtail.fields import StreamField

from apps.core.blocks import SectionsBlock


class BlocksPageMixin(models.Model):
    """Тело страницы из секций библиотеки блоков."""

    body = StreamField(SectionsBlock(), verbose_name="Секции", blank=True)

    class Meta:
        abstract = True

    @property
    def starts_with_hero(self):
        return bool(self.body) and self.body[0].block_type == "hero"
