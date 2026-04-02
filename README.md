# job-board

A job board data system you will build step by step through the [Data Systems](https://dutchengineer.com/foundations/data-systems/) module. Each step applies concepts from the corresponding lesson — SQL, document stores, vector search, file formats, and data quality.

## Getting started

```bash
docker compose up -d
cp .env.example .env
uv sync --all-extras
psql $DATABASE_URL -f migrations/001_create_tables.sql
uv run pytest tests/ -v
```

This starts PostgreSQL and Redis, runs the initial migration, and shows you the test results. Everything starts failing — that is expected.

## How it works

The [project page](https://dutchengineer.com/foundations/data-systems/project-job-board/) walks you through 6 steps. After each step, run the tests, commit, and push. CI validates your work automatically — green checks mean the step passes.

**Step 1 — Database Setup** gets PostgreSQL running, creates the schema, and seeds it with companies and listings. Run `uv run pytest tests/test_step1_databases.py` to verify.

**Step 2 — SQL Queries** builds the core query functions — keyword search, company stats, recent listings, and JOINs. Run `uv run pytest tests/test_step2_sql.py`.

**Step 3 — Document & KV Storage** adds JSONB company profiles and Redis caching for search results. You will write a new migration (`002_add_profiles.sql`) and build the cache layer. Run `uv run pytest tests/test_step3_doc_kv.py`.

**Step 4 — Vector Search** enables pgvector, adds embeddings to listings, and implements semantic search with cosine distance. Another migration (`003_vector_search.sql`) and an HNSW index. Run `uv run pytest tests/test_step4_vectors.py`.

**Step 5 — Data Files** builds import and export pipelines — reading partner CSV feeds into PostgreSQL and exporting to Parquet for analytics. Run `uv run pytest tests/test_step5_files.py`.

**Step 6 — Data Quality** hardens the import pipeline with Pydantic validation, data cleaning, quality metrics, and idempotent upserts. Run `uv run pytest tests/test_step6_quality.py`.

## Project structure

As you work through the steps, you will create these files:

```
src/job_board/
├── __init__.py
├── db.py            # Database connection (provided)
├── queries.py       # SQL query functions (Step 2)
├── cache.py         # Redis caching (Step 3)
├── semantic.py      # Vector search (Step 4)
├── models.py        # Pydantic models (Step 6)
├── importer.py      # CSV import + validation (Steps 5-6)
└── exporter.py      # Parquet export (Step 5)
scripts/
├── seed.py          # Seed data (Step 1)
├── import_feed.py   # CSV import script (Step 5)
└── export_parquet.py # Parquet export (Step 5)
migrations/
├── 001_create_tables.sql    # Initial schema (provided)
├── 002_add_profiles.sql     # JSONB profiles (Step 3)
└── 003_vector_search.sql    # pgvector + embeddings (Step 4)
```
