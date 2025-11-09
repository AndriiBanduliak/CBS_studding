# RentMaster CRM

Modern CRM for short‑term rentals. Backend powered by Django REST Framework; frontend is a React (Vite) SPA with Ant Design.

## Stack
- Backend: Django 5, DRF, drf-spectacular, django-cors-headers, django-filter, python-dotenv
- Frontend: React 18, Vite, Ant Design, React Router, Axios
- Database: SQLite (dev). Recommended: PostgreSQL (stage/prod)

## Features (WIP)
- Entities: Properties, Rates, Bookings, Customers, Tasks, Staff, Notes, Integrations, Reports, Audit
- API schema and docs via OpenAPI (drf-spectacular)
- SPA with Ant Design UI components

## Monorepo layout
```
accounts/ audit/ bookings/ customers/ integrations/ notes/ properties/ rates/ reports/ staff/ tasks/
  Django apps (models, views, migrations)
rentmaster/               # Django project settings and URL routing
frontend/                 # React SPA (Vite)
manage.py                 # Django management entrypoint
db.sqlite3                # Dev database
```

## Getting started

### Prerequisites
- Python 3.12+
- Node.js 18+

### Backend (Django)
1) Copy `.env` from the provided example and adjust values
```
copy .env.example .env   # on Windows (PowerShell: Copy-Item .env.example .env)
# In this repo, an "env.example" is provided if your system hides dotfiles
# copy env.example .env
```
2) Create venv and install deps
```
python -m venv .venv
. ./.venv/Scripts/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```
3) Apply migrations and run server
```
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Alternatively, with Makefile (Windows with `make` or via Git Bash):
```
make venv install migrate run
```

### Frontend (React + Vite)
```
cd frontend
npm install
npm run dev -- --host
```
The dev server runs on http://localhost:5173

Using Makefile:
```
make fe-install
make fe-dev
```

### API documentation
- OpenAPI docs: http://127.0.0.1:8000/api/docs/

### Generate TypeScript types from OpenAPI (frontend)
Requires backend running locally.
```
cd frontend
npm run types
# outputs: src/api/schema.d.ts
```
You can also use Makefile: `make fe-types`.

## Environment variables (.env)

| Name | Description | Example |
|------|-------------|---------|
| SECRET_KEY | Django secret key (mandatory in non-dev) | change-me-in-production |
| DEBUG | Enable debug mode | true/false |
| ALLOWED_HOSTS | Comma-separated hostnames | 127.0.0.1,localhost |
| CORS_ALLOW_ALL_ORIGINS | Allow all origins (dev only) | true |
| CORS_ALLOWED_ORIGINS | Comma-separated allowed origins | http://127.0.0.1:5173,http://localhost:5173 |
| CSRF_TRUSTED_ORIGINS | Comma-separated CSRF trusted origins | http://127.0.0.1:5173,http://localhost:5173 |
| SECURE_HSTS_SECONDS | HSTS seconds (prod) | 31536000 |
| SECURE_SSL_REDIRECT | Force HTTPS (prod) | true/false |
| SESSION_COOKIE_SECURE | Secure session cookie | true/false |
| CSRF_COOKIE_SECURE | Secure CSRF cookie | true/false |
| X_FRAME_OPTIONS | clickjacking protection | DENY/SAMEORIGIN |
| SENTRY_DSN | Sentry DSN to enable reporting |  |
| LOG_JSON | Enable JSON logs | true/false |
| GOOGLE_CLIENT_ID | Google OAuth client id |  |
| GOOGLE_CLIENT_SECRET | Google OAuth client secret |  |
| GOOGLE_REDIRECT_URI | OAuth redirect URL | http://localhost:8000/api/integrations/google/callback/ |
| GOOGLE_PROJECT_ID | Google project id |  |
| GOOGLE_WEBHOOK_VERIFICATION_TOKEN | Webhook verification token |  |

An example file is included: `.env.example` (or `env.example` depending on your OS visibility settings).

## Useful commands
- Django checks: `python manage.py check`
- Run tests: `make test` (pytest)
- Frontend lint: `cd frontend && npm run lint`
- Frontend build: `cd frontend && npm run build`

## Development notes
- CORS is open for development by default but becomes closed when `DEBUG=false`. Use `CORS_ALLOWED_ORIGINS` to whitelist your frontends.
- Default `LANGUAGE_CODE` is `uk` and `TIME_ZONE` is `Europe/Kyiv`.
- Pagination defaults to 25 items (DRF PageNumberPagination).

## Testing & QA
- Install dev deps: `make install` (includes requirements-dev.txt)
- Run tests: `make test`
- Lint/format check: `make lint`
- Pre-commit hooks: `make precommit-install`

## Troubleshooting
- OpenAPI docs do not load: ensure backend is running and `drf-spectacular` is installed; check `rentmaster/urls.py` exposes `/api/schema/`.
- Frontend gets 403 on API: log in first; verify CORS/CSRF in `rentmaster/settings.py` include `http://localhost:5173` and `http://127.0.0.1:5173`.
- Cookies/CSRF issues in dev: clear site data for `localhost:5173`; reload; ensure `ensureCsrfCookie()` is called on app start.
- `.env` missing: copy `env.example` to `.env` and restart.

## Docker (PostgreSQL + Django)
Quick start:
```
docker compose up --build
```
The app will run at `http://localhost:8000` with Postgres at `localhost:5432`.

Environment (override via `.env` or compose `environment`):
- `POSTGRES_DB` (default `rentmaster`)
- `POSTGRES_USER` (default `rentmaster`)
- `POSTGRES_PASSWORD` (default `rentmaster`)
- `DATABASE_URL` (auto-generated in compose)
- `DJANGO_SETTINGS_MODULE=rentmaster.settings_dev`

## FAQ
- How do I run everything quickly?
  - `make venv install migrate run` in project root, and `make fe-install fe-dev` in another terminal.
- How do I regenerate frontend API types?
  - Start backend, then `cd frontend && npm run types` (or `make fe-types`).
- Where are API docs?
  - Swagger UI at `/api/docs/`, JSON schema at `/api/schema/`.

## License
MIT

