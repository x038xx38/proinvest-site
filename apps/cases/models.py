from django.core.paginator import Paginator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from apps.core.blocks import ArticleBlock
from apps.core.templatetags.core_tags import rub


class CaseIndexPage(Page):
    """Список кейсов с фильтрами по услуге и типу объекта."""

    intro = models.TextField("Подзаголовок", blank=True)

    content_panels = [*Page.content_panels, FieldPanel("intro")]

    max_count = 1
    parent_page_types = ["pages.HomePage"]
    subpage_types = ["cases.CasePage"]
    per_page = 12

    class Meta:
        verbose_name = "Раздел кейсов"

    def get_context(self, request, *args, **kwargs):
        from apps.services.models import ServicePage

        context = super().get_context(request, *args, **kwargs)
        cases = (
            CasePage.objects.child_of(self)
            .live()
            .select_related("cover_image", "service")
            .order_by("-deal_date", "-pk")
        )
        object_type = request.GET.get("tip")
        if object_type in CasePage.ObjectType.values:
            cases = cases.filter(object_type=object_type)
        service_slug = request.GET.get("usluga")
        if service_slug:
            cases = cases.filter(service__slug=service_slug)

        used_services = CasePage.objects.child_of(self).live().values("service")
        context.update(
            page_obj=Paginator(cases, self.per_page).get_page(request.GET.get("page")),
            object_types=CasePage.ObjectType.choices,
            services=ServicePage.objects.live().filter(pk__in=used_services),
            current_type=object_type,
            current_service=service_slug,
        )
        return context


class CasePage(Page):
    class ObjectType(models.TextChoices):
        STORAGE = "kladovaya", "Кладовая"
        PARKING = "mashinomesto", "Машино-место"

    class Strategy(models.TextChoices):
        RENT = "rent", "Аренда"
        RESALE = "resale", "Перепродажа"

    object_type = models.CharField(
        "Тип объекта", max_length=20, choices=ObjectType.choices, default=ObjectType.STORAGE
    )
    strategy = models.CharField(
        "Стратегия", max_length=10, choices=Strategy.choices, default=Strategy.RENT
    )
    city = models.CharField("Город, район", max_length=120, blank=True)
    budget = models.PositiveIntegerField("Бюджет, ₽", null=True, blank=True)
    yield_percent = models.DecimalField(
        "Доходность, %",
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Для аренды — годовых, для перепродажи — прибыль за сделку",
    )
    term = models.CharField("Срок", max_length=40, blank=True, help_text="Например: 3 недели")
    deal_date = models.DateField("Дата сделки", null=True, blank=True)
    service = models.ForeignKey(
        "services.ServicePage",
        verbose_name="Услуга",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cases",
    )
    summary = models.TextField("Кратко", blank=True, help_text="Задача и результат в 1–2 абзацах")
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Обложка",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(ArticleBlock(), verbose_name="Подробности", blank=True)

    content_panels = [
        *Page.content_panels,
        MultiFieldPanel(
            [
                FieldRowPanel([FieldPanel("object_type"), FieldPanel("strategy")]),
                FieldRowPanel([FieldPanel("city"), FieldPanel("deal_date")]),
                FieldRowPanel([FieldPanel("budget"), FieldPanel("yield_percent")]),
                FieldPanel("term"),
                FieldPanel("service"),
            ],
            "Параметры",
        ),
        FieldPanel("cover_image"),
        FieldPanel("summary"),
        FieldPanel("body"),
        InlinePanel("gallery", label="Галерея"),
    ]

    search_fields = [
        *Page.search_fields,
        index.SearchField("city"),
        index.SearchField("summary"),
    ]

    parent_page_types = ["cases.CaseIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Кейс"
        verbose_name_plural = "Кейсы"

    @property
    def yield_display(self):
        if self.yield_percent is None:
            return ""
        value = f"{self.yield_percent.normalize():f}".replace(".", ",")
        if self.strategy == self.Strategy.RESALE:
            return f"+{value} %"
        return f"{value} % год."

    def as_card(self):
        """Данные для карточки кейса (шаблон blocks/_case_card.html)."""
        return {
            "url": self.url,
            "link_text": "Подробнее",
            "image": self.cover_image,
            "title": self.title,
            "city": self.city,
            "budget": rub(self.budget),
            "yield_text": self.yield_display,
            "term": self.term,
        }


class CaseGalleryImage(Orderable):
    page = ParentalKey(CasePage, on_delete=models.CASCADE, related_name="gallery")
    image = models.ForeignKey(
        "wagtailimages.Image", verbose_name="Фото", on_delete=models.CASCADE, related_name="+"
    )
    caption = models.CharField("Подпись", max_length=255, blank=True)

    panels = [FieldPanel("image"), FieldPanel("caption")]
