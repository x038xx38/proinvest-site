#!/usr/bin/env bash
# Первичная подготовка сервера под ProInvest. Запускается ОДИН раз от root.
#
#   Без домена (стенд на отдельном порту, HTTP):
#     bash bootstrap.sh 80.87.198.107
#   С доменом (порт 80/443, сертификат Let's Encrypt):
#     bash bootstrap.sh new.example.ru admin@example.ru
#
# Существующие сервисы (StoreParking, почта, MySQL, Apache, ISPmanager) не трогает:
# в режиме IP nginx слушает только отдельный порт и не влияет на выбор сайтов на 80/443.
set -euo pipefail

HOST=${1:?Укажите IP или домен}
CERT_EMAIL=${2:-}
IP_PORT=8090
REPO=git@github.com:x038xx38/proinvest-site.git
TAILWIND_VERSION=v4.3.3
DEPLOY_USER=codex-deploy
GUARD_URL=https://storeparking.ru/

HOME_DIR=/opt/proinvest
APP=$HOME_DIR/app

[[ $EUID -eq 0 ]] || { echo "Запустите от root"; exit 1; }

if [[ $HOST =~ ^[0-9.]+$ ]]; then
    MODE=ip
    LISTEN=$IP_PORT
    SERVER_NAME=_
    SITE_URL=http://$HOST:$IP_PORT
    USE_HTTPS=false
    NGINX_CONF=proinvest-ip.conf
else
    MODE=domain
    [[ -n $CERT_EMAIL ]] || { echo "Для домена укажите email для SSL-сертификата вторым аргументом"; exit 1; }
    LISTEN=80
    SERVER_NAME=$HOST
    SITE_URL=https://$HOST
    USE_HTTPS=true
    NGINX_CONF=$HOST.conf
fi

guard_status() { curl -s -o /dev/null -m 10 -w '%{http_code}' "$GUARD_URL" || true; }
GUARD_BEFORE=$(guard_status)
echo "==> $GUARD_URL до изменений отвечает: $GUARD_BEFORE"

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
    sudo -u proinvest bash -c "ssh-keyscan -t ed25519 github.com >> $HOME_DIR/.ssh/known_hosts 2>/dev/null"
fi

echo "==> Tailwind"
mkdir -p "$HOME_DIR/bin"
curl -fsSL -o "$HOME_DIR/bin/tailwindcss" \
    "https://github.com/tailwindlabs/tailwindcss/releases/download/$TAILWIND_VERSION/tailwindcss-linux-x64"
chmod +x "$HOME_DIR/bin/tailwindcss"
chown -R proinvest:proinvest "$HOME_DIR/bin"

echo "==> Пароль тестового стенда"
STAGE_PASSWORD=$(openssl rand -base64 12 | tr -d '/+=')
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

if [[ ! -d $APP/.git ]]; then
    cat <<EOF

================================================================
Добавьте этот ключ в GitHub как Deploy key (только чтение):
https://github.com/x038xx38/proinvest-site/settings/keys/new

$(cat "$HOME_DIR/.ssh/id_ed25519.pub")
================================================================
EOF
    read -rp "Ключ добавлен? Нажмите Enter, чтобы продолжить… "
    echo "==> Клонирование"
    sudo -u proinvest git clone -q "$REPO" "$APP"
fi

if [[ ! -f $APP/.env ]]; then
    [[ ${NEW_DB:-0} == 1 ]] || { echo "Роль БД уже была, а .env нет — пропишите DATABASE_URL вручную"; exit 1; }
    cat > "$APP/.env" <<EOF
DJANGO_SECRET_KEY=$(openssl rand -base64 48 | tr -d '\n/+=')
DJANGO_DEBUG=false
DJANGO_USE_HTTPS=$USE_HTTPS
DJANGO_ALLOWED_HOSTS=$HOST
DJANGO_CSRF_TRUSTED_ORIGINS=$SITE_URL
SITE_URL=$SITE_URL
DATABASE_URL=postgres://proinvest:$DB_PASSWORD@127.0.0.1:5432/proinvest
REDIS_URL=redis://127.0.0.1:6379/5
EMAIL_URL=consolemail://
DEFAULT_FROM_EMAIL=ПроИнвест <noreply@proinvest.local>
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
sed -e "s/{{LISTEN}}/$LISTEN/" -e "s/{{SERVER_NAME}}/$SERVER_NAME/" \
    "$APP/deploy/nginx.conf.template" > "/etc/nginx/sites-available/$NGINX_CONF"
ln -sf "/etc/nginx/sites-available/$NGINX_CONF" "/etc/nginx/sites-enabled/$NGINX_CONF"

rollback_nginx() {
    echo "!!! Откатываю конфиг nginx ProInvest"
    rm -f "/etc/nginx/sites-enabled/$NGINX_CONF"
    nginx -t && systemctl reload nginx
    exit 1
}

nginx -t || rollback_nginx
systemctl reload nginx
sleep 2
GUARD_AFTER=$(guard_status)
echo "==> $GUARD_URL после изменений отвечает: $GUARD_AFTER"
[[ $GUARD_AFTER == "$GUARD_BEFORE" ]] || rollback_nginx

if [[ $MODE == ip ]]; then
    if ufw status 2>/dev/null | grep -q "Status: active"; then
        ufw allow "$IP_PORT/tcp"
    fi
    echo "Если сайт не откроется снаружи — откройте порт $IP_PORT/tcp в файрволе ISPmanager."
else
    SERVER_IP=$(curl -fsS https://api.ipify.org || true)
    if [[ $(getent hosts "$HOST" | awk '{print $1}' | head -1) == "$SERVER_IP" ]]; then
        certbot --nginx -n --agree-tos -m "$CERT_EMAIL" -d "$HOST" --redirect
    else
        echo "DNS $HOST ещё не указывает на $SERVER_IP — сертификат выпустите позже:"
        echo "  certbot --nginx -n --agree-tos -m $CERT_EMAIL -d $HOST --redirect"
    fi
fi

cat <<EOF

Готово.
  Сайт:   $SITE_URL   (логин proinvest, пароль $STAGE_PASSWORD)
  Админку создаст разработчик или:
    sudo -u proinvest bash -c 'cd $APP && DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py createsuperuser'
EOF
