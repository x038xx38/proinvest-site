#!/usr/bin/env bash
# Обновление кода. Запускается от пользователя proinvest:
#   sudo -u proinvest /opt/proinvest/app/deploy/deploy.sh
# После него: sudo systemctl restart proinvest-web proinvest-worker
set -euo pipefail

APP=/opt/proinvest/app
cd "$APP"

# Сначала обновляем код и перезапускаем уже новую версию этого скрипта:
# bash дочитывает старый файл, если git заменил его во время выполнения
if [[ -z ${DEPLOY_CODE_UPDATED:-} ]]; then
    git fetch --quiet origin main
    git reset --hard origin/main
    DEPLOY_CODE_UPDATED=1 exec "$0" "$@"
fi

test -d .venv || python3.12 -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements/prod.txt

/opt/proinvest/bin/tailwindcss -i frontend/main.css -o static/dist/main.css --minify

export DJANGO_SETTINGS_MODULE=config.settings.prod
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput --verbosity 0
.venv/bin/python manage.py check --deploy --fail-level ERROR

echo "Deployed $(git rev-parse --short HEAD)"
