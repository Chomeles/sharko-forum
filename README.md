# sharko-forum — a modern, self-hostable forum

A clean, dark, XenForo-style community forum you can stand up with **one command**.
Built on Django 5.2 LTS + Postgres. No build step, no Node, no JS framework — just a
fast server-rendered app you can actually read and maintain.

**Live demo:** https://sharko.icu/forum/

## Features

- **Categories → threads → posts**, grouped into sections with icons on the index
- **Accounts** — signup, login, password reset, per-post edit
- **Ranks** that climb with your message count (Newbie → Member → Active → Elite), with colored usernames
- **Reputation** — a ▲ Rep button on every post (AJAX, degrades to a normal POST without JS)
- **Generated gradient avatars** — no uploads, no storage, deterministic per user
- **Views, pinned & locked threads, search, pagination, a stats bar**
- **Django admin** as a full moderation backend out of the box
- **Dark theme**, responsive, accessible

## Quick start (one command)

Requires [Docker](https://docs.docker.com/get-docker/) with Compose v2.

```bash
curl -fsSL https://raw.githubusercontent.com/Chomeles/sharko-forum/main/install.sh | bash
```

This clones the repo, generates secrets + an admin password, and boots the app +
Postgres. When it finishes, open **http://localhost:8000/** — admin panel at `/admin/`.

Prefer to do it by hand?

```bash
git clone https://github.com/Chomeles/sharko-forum.git && cd sharko-forum
cp .env.example .env
# fill DJANGO_SECRET_KEY and POSTGRES_PASSWORD (any long random strings)
docker compose up -d --build
```

## Going to production

1. Point a domain at your server and put a reverse proxy (Caddy, nginx, Traefik) in
   front of port 8000 to terminate TLS. Caddy example:
   ```
   forum.example.com {
       reverse_proxy 127.0.0.1:8000
   }
   ```
2. In `.env` set your real host:
   ```
   ALLOWED_HOSTS=forum.example.com
   CSRF_TRUSTED_ORIGINS=https://forum.example.com
   ```
3. `docker compose up -d --build`

WhiteNoise serves the static files from the app itself, so no extra static-file config
is needed. Static filenames are content-hashed, so they cache forever safely.

### Configuration

Everything is env vars (see `.env.example`). The important ones:

| Variable | What it does |
|---|---|
| `DJANGO_SECRET_KEY` | Required. Any long random string. |
| `ALLOWED_HOSTS` | Comma-separated hostnames you serve on. |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated origins **with** scheme. |
| `POSTGRES_PASSWORD` | Database password. |
| `TIME_ZONE` | e.g. `Europe/Berlin`. Default `UTC`. |
| `FORCE_SCRIPT_NAME` | Set (e.g. `/forum`) to host under a sub-path; see `.env.example`. |

## Updating

```bash
cd sharko-forum
git pull
docker compose up -d --build   # runs migrations automatically on boot
```

Because it's on the Django **LTS** track, upgrades are `git pull` + rebuild. The app
lives in one self-contained `forum/` app so you can extend it without fighting the core.

## Develop locally (without Docker)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DJANGO_SECRET_KEY=dev DJANGO_DEBUG=1
python manage.py migrate
python manage.py runserver
```

## Tech stack

Django 5.2 LTS · PostgreSQL · gunicorn · WhiteNoise · server-rendered templates + a
sprinkle of vanilla JS. That's the whole list.

## License

MIT — see [LICENSE](LICENSE).
