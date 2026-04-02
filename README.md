# job-board

Build a job board data system step by step. Each step applies concepts from the corresponding lesson in the [Data Systems](https://dutchengineer.com/foundations/data-systems/) module.

## Setup

```bash
docker compose up -d
cp .env.example .env
uv sync --all-extras
psql $DATABASE_URL -f migrations/001_create_tables.sql
uv run pytest tests/ -v
```

Run `docker compose up -d` to start PostgreSQL and Redis.

## Steps

| Step | Topic | Test file | Command |
|------|-------|-----------|---------|
| 1 | Database Setup | `tests/test_step1_databases.py` | `uv run pytest tests/test_step1_databases.py` |
| 2 | SQL Queries | `tests/test_step2_sql.py` | `uv run pytest tests/test_step2_sql.py` |
| 3 | Document & KV Storage | `tests/test_step3_doc_kv.py` | `uv run pytest tests/test_step3_doc_kv.py` |
| 4 | Vector Search | `tests/test_step4_vectors.py` | `uv run pytest tests/test_step4_vectors.py` |
| 5 | Data Files | `tests/test_step5_files.py` | `uv run pytest tests/test_step5_files.py` |
| 6 | Data Quality | `tests/test_step6_quality.py` | `uv run pytest tests/test_step6_quality.py` |

## Workflow

1. Read the step instructions on the [project page](https://dutchengineer.com/foundations/data-systems/project-job-board/)
2. Implement the step
3. Run the tests for that step
4. Commit and push
5. CI runs all tests — green checks mean the step passes

## Project structure

```
src/job_board/
├── __init__.py
├── db.py            # Database connection (provided)
├── queries.py       # SQL query functions (Step 2)
├── cache.py         # Redis caching (Step 3)
├── semantic.py      # Vector search (Step 4)
├── models.py        # Pydantic models (Step 6)
└── importer.py      # CSV import + validation (Steps 5-6)
scripts/
├── seed.py          # Seed data (Step 1)
├── import_feed.py   # CSV import script (Step 5)
└── export_parquet.py # Parquet export (Step 5)
migrations/
├── 001_create_tables.sql    # Initial schema (provided)
├── 002_add_profiles.sql     # JSONB profiles (Step 3)
└── 003_vector_search.sql    # pgvector + embeddings (Step 4)
```
