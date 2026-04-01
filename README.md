# job-board

Starter repo for the Data Systems module. Fork this repo and follow the lessons.

## Setup

```bash
docker compose up -d
cp .env.example .env
uv sync --all-extras
psql $DATABASE_URL -f migrations/001_create_tables.sql
uv run pytest tests/ -v
```

Run `docker compose up -d` to start PostgreSQL and Redis.
