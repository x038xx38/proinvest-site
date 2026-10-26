from .base import *  # noqa: F403
from .base import env

DEBUG = False

# HTTPS-настройки отключаются через .env, пока стенд работает по IP без сертификата
USE_HTTPS = env.bool("DJANGO_USE_HTTPS", default=True)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = USE_HTTPS
SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS
SECURE_HSTS_SECONDS = env.int("DJANGO_HSTS_SECONDS", default=60 * 60 * 24 * 30) if USE_HTTPS else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = USE_HTTPS
SECURE_CONTENT_TYPE_NOSNIFF = True
