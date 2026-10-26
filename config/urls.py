from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from apps.core.views import robots_txt

urlpatterns = [
    # Django Admin — заявки, заказы, тарифы, промокоды
    path("admin/", admin.site.urls),
    # Wagtail — страницы, услуги, кейсы, статьи
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap),
    path("robots.txt", robots_txt),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns = [path("__debug__/", include("debug_toolbar.urls")), *urlpatterns]

# Wagtail обрабатывает все остальные адреса — должен быть последним
urlpatterns += [path("", include(wagtail_urls))]
