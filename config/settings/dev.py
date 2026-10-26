from .base import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE, env

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# Toolbar при импорте подгружает GDAL (django.contrib.gis), поэтому включается по флагу:
# на машинах без рабочего GDAL он роняет запуск
if env.bool("USE_DEBUG_TOOLBAR", default=False):
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]

# В разработке статика отдаётся без манифеста, чтобы не нужен был collectstatic
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Whitenoise в разработке берёт статику через finders, без collectstatic
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
