from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_GET


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
