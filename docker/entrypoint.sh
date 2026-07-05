#!/bin/sh
set -e

# Wait for Postgres, then apply migrations before serving.
echo "Waiting for database at ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}…"
python - <<'PY'
import os, time, psycopg
dsn = f"host={os.environ.get('POSTGRES_HOST','db')} port={os.environ.get('POSTGRES_PORT','5432')} " \
      f"dbname={os.environ.get('POSTGRES_DB','forum')} user={os.environ.get('POSTGRES_USER','forum')} " \
      f"password={os.environ.get('POSTGRES_PASSWORD','')}"
for _ in range(60):
    try:
        psycopg.connect(dsn, connect_timeout=2).close(); break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("database never came up")
PY

python manage.py migrate --noinput

# Create the admin from env on first boot (skips if it already exists).
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@localhost}" 2>/dev/null || true
fi

# First-boot demo content + a demo/demo login for kicking the tyres (no-op once the
# forum has content). Set SEED_DEMO=0 in .env for a clean production install.
if [ "${SEED_DEMO:-1}" != "0" ]; then
  python manage.py seed_demo || true
fi

# Anonymous install ping (a random UUID + version only). Opt out: FORUM_TELEMETRY=off
python manage.py ping_home || true

exec gunicorn config.wsgi --bind 0.0.0.0:8000 --workers "${GUNICORN_WORKERS:-3}"
