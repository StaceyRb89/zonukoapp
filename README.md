# Zonuko

Zonuko is a STEAM project learning platform focused on hands-on activities, minimal screen time, and community showcases.

## Quickstart (Local Development)

### 1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Set environment variables

```bash
cp .env.example .env
```

Update `DJANGO_SECRET_KEY` before deploying to production.

### 4) Run migrations

```bash
python manage.py migrate
```

### 5) Start the server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

## Environment Variables

- `DJANGO_SECRET_KEY`: required in production.
- `DJANGO_DEBUG`: set to `False` in production.
- `DJANGO_ALLOWED_HOSTS`: space-delimited hosts.
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: database configuration (swap to Postgres later).

## Deployment Notes

- Use a managed Postgres database and update the `DB_*` environment variables.
- Set `DJANGO_DEBUG=False` and supply a secure `DJANGO_SECRET_KEY`.
- Collect static files if serving via a dedicated web server.

## Optional tooling

Pre-commit hooks are optional. If you use them, configure `.pre-commit-config.yaml` to match your workflow.
