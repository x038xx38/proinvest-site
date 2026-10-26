# ПроИнвест — сайт

Django 5.2 + Wagtail 7.4, PostgreSQL, Redis/Celery, Tailwind CSS 4.

- Сайт: http://localhost:8001
- CMS (страницы, услуги, кейсы, статьи): http://localhost:8001/cms/
- Админка (заявки, заказы, тарифы): http://localhost:8001/admin/
- Перехваченная почта (Mailpit): http://localhost:8025

Порт 8001 — потому что на 8000 работает старый сайт курса (`../proinvest-store`).

## Локальный запуск

Нужны Python 3.12, Node 20+, Docker Desktop.

```bash
make setup        # venv, зависимости, сервисы в Docker, миграции, сборка CSS
make superuser    # администратор
make run          # dev-сервер
make css-watch    # в соседнем терминале: пересборка CSS при правках шаблонов
make worker       # при необходимости: Celery (письма, интеграции)
```

Postgres, Redis и Mailpit работают в Docker (`make up` / `make down`), Django — на хосте из `.venv`.

## Структура

```
config/        настройки (base / dev / prod), urls, celery
apps/core      настройки сайта (контакты, соцсети, счётчики), robots.txt
apps/pages     главная и служебные страницы Wagtail
apps/services  направления и услуги (этап 2)
apps/cases     кейсы (этап 2)
apps/blog      статьи (этап 2)
apps/leads     заявки (этап 3)
apps/course    обучение: потоки, тарифы, заказы, оплата Т-Банк (этап 4)
templates/     шаблоны
static/src     исходники CSS/JS; сборка в static/dist
```

## Проверки

```bash
make lint
make test
```

## Известное

Django Debug Toolbar включается флагом `USE_DEBUG_TOOLBAR=true` в `.env`. Он подгружает GDAL;
если GDAL из Homebrew сломан (ошибка `libabsl_…dylib`), почините `brew reinstall re2` или не включайте флаг.
