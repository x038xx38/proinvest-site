PY := .venv/bin/python
PORT ?= 8001

.PHONY: setup up down run css css-watch worker migrate superuser lint test

setup:            ## Первый запуск: venv, зависимости, сервисы, миграции, CSS
	test -d .venv || python3.12 -m venv .venv
	.venv/bin/pip install -r requirements/dev.txt
	npm install
	test -f .env || cp .env.example .env
	$(MAKE) up migrate css

up:               ## Поднять Postgres, Redis, Mailpit
	docker compose up -d --wait

down:
	docker compose down

run:              ## Django dev-сервер на http://localhost:8001
	$(PY) manage.py runserver $(PORT)

css:
	npm run build

css-watch:
	npm run dev

worker:           ## Celery worker (письма, интеграции)
	.venv/bin/celery -A config worker -l info

migrate:
	$(PY) manage.py migrate

superuser:
	$(PY) manage.py createsuperuser

lint:
	.venv/bin/ruff check . && .venv/bin/ruff format --check .

test:
	.venv/bin/pytest
