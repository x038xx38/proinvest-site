#!/usr/bin/env bash
# Первичная подготовка сервера под ProInvest. Запускается ОДИН раз от root:
#   bash bootstrap.sh <домен> <email-для-letsencrypt>
# Существующие сервисы (StoreParking, почта, MySQL, Apache) не трогает.
set -euo pipefail

DOMAIN=${1:?Укажите домен, например: bash bootstrap.sh new.example.ru admin@example.ru}
CERT_EMAIL=${2:?Укажите email для SSL-сертификата}
REPO=git@github.com:x038xx38/proinvest-site.git
TAILWIND_VERSION=v4.3.3
DEPLOY_USER=codex-deploy

HOME_DIR=/opt/proinvest
APP=$HOME_DIR/app

[[ $EUID -eq 0 ]] || { echo "Запустите от root"; exit 1; }

echo "==> Пакеты"
apt-get update -qq
apt-get install -y -qq postgresql python3.12-venv

echo "==> Пользователь proinvest"
id proinvest &>/dev/null || useradd --system --create-home --home-dir "$HOME_DIR" --shell /bin/bash proinvest
chmod 750 "$HOME_DIR"
# nginx должен читать static/media
usermod -aG proinvest www-data

echo "==> PostgreSQL"
DB_PASSWORD=$(openssl rand -hex 24)
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='proinvest'" | grep -q 1; then
    sudo -u postgres psql -qc "CREATE ROLE proinvest LOGIN PASSWORD '$DB_PASSWORD'"
    sudo -u postgres psql -qc "CREATE DATABASE proinvest OWNER proinvest"
    NEW_DB=1
fi

echo "==> Deploy-ключ GitHub"
if [[ ! -f $HOME_DIR/.ssh/id_ed25519 ]]; then
    sudo -u proinvest mkdir -p "$HOME_DIR/.ssh"
    sudo -u proinvest ssh-keygen -q -t ed25519 -N "" -C "proinvest@$(hostname)" -f "$HOME_DIR/.ssh/id_ed25519"
    sudo -u proinvest ssh-keyscan -t ed25519 github.com >> "$HOME_DIR/.ssh/known_hosts" 2>/dev/null
fi

echo "==> Tailwind"
mkdir -p "$HOME_DIR/bin"
curl -fsSL -o "$HOME_DIR/bin/tailwindcss" \
    "https://github.com/tailwindlabs/tailwindcss/releases/download/$TAILWIND_VERSION/tailwindcss-linux-x64"
chmod +x "$HOME_DIR/bin/tailwindcss"
chown -R proinvest:proinvest "$HOME_DIR/bin"

echo "==> Пароль тестового стенда"
STAGE_PASSWORD=$(openssl rand -base64 12)
htpasswd -bc "$HOME_DIR/htpasswd" proinvest "$STAGE_PASSWORD" >/dev/null
chown root:www-data "$HOME_DIR/htpasswd"
chmod 640 "$HOME_DIR/htpasswd"

echo "==> Права для $DEPLOY_USER (только деплой и рестарт этих сервисов)"
cat > /etc/sudoers.d/proinvest-deploy <<EOF
$DEPLOY_USER ALL=(proinvest) NOPASSWD: $APP/deploy/deploy.sh, $APP/.venv/bin/python
$DEPLOY_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart proinvest-web, /usr/bin/systemctl restart proinvest-worker, /usr/bin/systemctl restart proinvest-web proinvest-worker, /usr/bin/systemctl status proinvest-web, /usr/bin/systemctl status proinvest-worker, /usr/bin/journalctl -u proinvest-web *, /usr/bin/journalctl -u proinvest-worker *
EOF
chmod 440 /etc/sudoers.d/proinvest-deploy
visudo -cf /etc/sudoers.d/proinvest-deploy

cat <<EOF

================================================================
Добавьте этот ключ в GitHub как Deploy key (только чтение):
https://github.com/x038xx38/proinvest-site/settings/keys/new

$(cat "$HOME_DIR/.ssh/id_ed25519.pub")
================================================================
EOF
read -rp "Ключ добавлен? Нажмите Enter, чтобы продолжить… "

echo "==> Клонирование"
if [[ ! -d $APP/.git ]]; then
    sudo -u proinvest git clone -q "$REPO" "$APP"
fi

if [[ ! -f $APP/.env ]]; then
    [[ ${NEW_DB:-0} == 1 ]] || { echo "Роль БД уже была, а .env нет — пропишите DATABASE_URL вручную"; exit 1; }
    cat > "$APP/.env" <<EOF
DJANGO_SECRET_KEY=$(openssl rand -base64 48 | tr -d '\n/+=')
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=$DOMAIN
DJANGO_CSRF_TRUSTED_ORIGINS=https://$DOMAIN
SITE_URL=https://$DOMAIN
DATABASE_URL=postgres://proinvest:$DB_PASSWORD@127.0.0.1:5432/proinvest
REDIS_URL=redis://127.0.0.1:6379/5
EMAIL_URL=consolemail://
DEFAULT_FROM_EMAIL=ПроИнвест <noreply@$DOMAIN>
LEADS_NOTIFY_EMAILS=
ALLOW_INDEXING=false
EOF
    chown proinvest:proinvest "$APP/.env"
    chmod 600 "$APP/.env"
fi
mkdir -p "$APP/media" && chown proinvest:proinvest "$APP/media"

echo "==> Первый деплой"
sudo -u proinvest "$APP/deploy/deploy.sh"

echo "==> systemd"
cp "$APP/deploy/proinvest-web.service" "$APP/deploy/proinvest-worker.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now proinvest-web proinvest-worker

echo "==> nginx"
sed "s/{{DOMAIN}}/$DOMAIN/g" "$APP/deploy/nginx.conf.template" > "/etc/nginx/sites-available/$DOMAIN.conf"
ln -sf "/etc/nginx/sites-available/$DOMAIN.conf" "/etc/nginx/sites-enabled/$DOMAIN.conf"
nginx -t
systemctl reload nginx

echo "==> HTTPS"
SERVER_IP=$(curl -fsS https://api.ipify.org || true)
if [[ $(getent hosts "$DOMAIN" | awk '{print $1}' | head -1) == "$SERVER_IP" ]]; then
    certbot --nginx -n --agree-tos -m "$CERT_EMAIL" -d "$DOMAIN" --redirect
else
    echo "DNS $DOMAIN ещё не указывает на $SERVER_IP — сертификат выпустите позже:"
    echo "  certbot --nginx -n --agree-tos -m $CERT_EMAIL -d $DOMAIN --redirect"
fi

cat <<EOF

Готово.
  Сайт:   https://$DOMAIN   (логин proinvest, пароль $STAGE_PASSWORD)
  Админка Django: создайте пользователя командой
    sudo -u proinvest bash -c 'cd $APP && DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py createsuperuser'
EOF
