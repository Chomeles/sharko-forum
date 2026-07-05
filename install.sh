#!/usr/bin/env bash
# One-command installer. Usage:
#   curl -fsSL https://raw.githubusercontent.com/Chomeles/sharko-forum/main/install.sh | bash
# Requires Docker + Docker Compose v2. Clones the repo, generates secrets, boots it.
set -euo pipefail

REPO="${FORUM_REPO:-https://github.com/Chomeles/sharko-forum.git}"
DIR="${FORUM_DIR:-forum}"
PORT="${WEB_PORT:-8000}"

command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required → https://docs.docker.com/get-docker/"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "❌ Docker Compose v2 is required"; exit 1; }

if [ ! -d "$DIR/.git" ]; then
  echo "→ Cloning into ./$DIR"
  git clone --depth 1 "$REPO" "$DIR"
fi
cd "$DIR"

gen() { python3 -c "import secrets;print(secrets.token_urlsafe($1))" 2>/dev/null || openssl rand -base64 "$1" | tr -d '\n/+='; }

if [ ! -f .env ]; then
  echo "→ Generating .env with fresh secrets"
  cp .env.example .env
  SECRET=$(gen 50); DBPASS=$(gen 24); ADMINPASS=$(gen 12)
  sed -i "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=${SECRET}|" .env
  sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${DBPASS}|" .env
  {
    echo "DJANGO_SUPERUSER_USERNAME=admin"
    echo "DJANGO_SUPERUSER_PASSWORD=${ADMINPASS}"
    echo "DJANGO_SUPERUSER_EMAIL=admin@localhost"
  } >> .env
  echo "──────────────────────────────────────────────"
  echo "  Admin login:  admin / ${ADMINPASS}"
  echo "  (also stored in ./$DIR/.env)"
  echo "──────────────────────────────────────────────"
fi

echo "→ Building and starting (first run pulls images, ~1–2 min)"
docker compose up -d --build

echo "✅ Forum is starting at http://localhost:${PORT}/  ·  admin panel at /admin/"
echo "   Logs: (cd $DIR && docker compose logs -f web)"
