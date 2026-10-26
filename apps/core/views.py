from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .blocks import SectionsBlock
from .styleguide import PAGES


@require_GET
def robots_txt(request):
    # На тестовых стендах закрываем сайт от индексации целиком
    if settings.DEBUG or not getattr(settings, "ALLOW_INDEXING", False):
        lines = ["User-agent: *", "Disallow: /"]
    else:
        lines = [
            "User-agent: *",
            "Disallow: /admin/",
            "Disallow: /cms/",
            f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


@require_GET
def styleguide(request, slug="blocks"):
    """Витрина блоков и макеты страниц на демо-данных. Видна в разработке и сотрудникам."""
    if not (settings.DEBUG or request.user.is_staff) or slug not in PAGES:
        raise Http404
    title, raw = PAGES[slug]
    return render(
        request,
        "core/styleguide.html",
        {
            "title": title,
            "slug": slug,
            "pages": {key: value[0] for key, value in PAGES.items()},
            "sections": SectionsBlock().to_python(raw),
        },
    )
