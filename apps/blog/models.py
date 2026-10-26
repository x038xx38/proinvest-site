from django.core.paginator import Paginator
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from apps.core.blocks import ArticleBlock


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField("Название", max_length=80)
    slug = models.SlugField("Адрес", max_length=80, unique=True, allow_unicode=False)
    description = models.TextField("Описание", blank=True)
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)

    panels = [FieldPanel("name"), FieldPanel("slug"), FieldPanel("description")]

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Рубрика"
        verbose_name_plural = "Рубрики"

    def __str__(self):
        return self.name


class BlogIndexPage(RoutablePageMixin, Page):
    """Список статей; рубрики открываются по адресу /stati/rubrika/<slug>/."""

    intro = models.TextField("Подзаголовок", blank=True)

    content_panels = [*Page.content_panels, FieldPanel("intro")]

    max_count = 1
    parent_page_types = ["pages.HomePage"]
    subpage_types = ["blog.ArticlePage"]
    per_page = 12

    class Meta:
        verbose_name = "Раздел статей"

    def articles(self):
        return (
            ArticlePage.objects.child_of(self)
            .live()
            .select_related("cover_image", "category")
            .order_by("-date", "-pk")
        )

    def render_list(self, request, articles, category=None):
        page_obj = Paginator(articles, self.per_page).get_page(request.GET.get("page"))
        if category and not page_obj.object_list and page_obj.number == 1:
            raise Http404
        return self.render(
            request,
            context_overrides={
                "page_obj": page_obj,
                "categories": BlogCategory.objects.filter(articles__in=self.articles()).distinct(),
                "current_category": category,
            },
        )

    @path("")
    def index(self, request):
        return self.render_list(request, self.articles())

    @path("rubrika/<slug:slug>/")
    def category(self, request, slug):
        category = get_object_or_404(BlogCategory, slug=slug)
        return self.render_list(request, self.articles().filter(category=category), category)


class ArticlePage(Page):
    date = models.DateField("Дата публикации", default=timezone.localdate)
    category = models.ForeignKey(
        BlogCategory,
        verbose_name="Рубрика",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="articles",
    )
    excerpt = models.TextField("Анонс", blank=True, help_text="Для карточки в списке статей")
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Обложка",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(ArticleBlock(), verbose_name="Текст")

    content_panels = [
        *Page.content_panels,
        FieldPanel("date"),
        FieldPanel("category"),
        FieldPanel("excerpt"),
        FieldPanel("cover_image"),
        FieldPanel("body"),
    ]

    search_fields = [
        *Page.search_fields,
        index.SearchField("excerpt"),
        index.SearchField("body"),
    ]

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["related"] = (
            ArticlePage.objects.live()
            .sibling_of(self, inclusive=False)
            .filter(category=self.category)
            .select_related("cover_image")
            .order_by("-date")[:3]
            if self.category
            else []
        )
        return context
