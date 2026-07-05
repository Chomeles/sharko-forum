FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

# psycopg[binary] ships its own libpq, so no build deps needed.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static at build time. A throwaway key is fine — collectstatic needs no secrets.
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput

# Drop root: run migrations, ping_home and gunicorn as an unprivileged user.
RUN adduser --system --group --no-create-home app && chown -R app:app /app
USER app

EXPOSE 8000
ENTRYPOINT ["/app/docker/entrypoint.sh"]
