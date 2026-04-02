"""Step 3: Document & KV Storage

Tests for JSONB company profiles and Redis caching.
"""

import json
import os

import pytest

psycopg2 = pytest.importorskip("psycopg2")

DATABASE_URL = os.environ.get("DATABASE_URL", "")


@pytest.fixture
def conn():
    if not DATABASE_URL:
        pytest.skip("DATABASE_URL not set")
    connection = psycopg2.connect(DATABASE_URL)
    yield connection
    connection.rollback()
    connection.close()


class TestJSONBProfile:
    def test_profile_column_exists(self, conn):
        """The companies table should have a 'profile' JSONB column."""
        cur = conn.cursor()
        cur.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = 'companies' AND column_name = 'profile'"
        )
        row = cur.fetchone()
        assert row is not None, "profile column not found on companies table"
        assert row[1] == "jsonb"

    def test_store_and_query_profile(self, conn):
        """Should store varying JSON profiles and query them."""
        cur = conn.cursor()
        profile = json.dumps({"perks": ["remote", "equity"], "tech_stack": ["Python"]})
        cur.execute(
            "INSERT INTO companies (name, profile) VALUES (%s, %s) RETURNING id",
            ("TestCo", profile),
        )
        company_id = cur.fetchone()[0]
        cur.execute(
            "SELECT profile->'perks' FROM companies WHERE id = %s", (company_id,)
        )
        perks = cur.fetchone()[0]
        assert "remote" in perks


class TestRedisCache:
    def test_cache_set_and_get(self):
        """Cache should store and retrieve search results."""
        redis_mod = pytest.importorskip("redis")
        try:
            r = redis_mod.Redis(host="localhost", port=6379, decode_responses=True)
            r.ping()
        except redis_mod.ConnectionError:
            pytest.skip("Redis not running")

        from job_board.cache import get_cached, set_cached

        key = "test:search:engineer"
        data = [{"title": "ML Engineer", "location": "Remote"}]
        set_cached(r, key, data, ttl=10)
        result = get_cached(r, key)
        assert result == data

    def test_cache_miss_returns_none(self):
        """Cache miss should return None."""
        redis_mod = pytest.importorskip("redis")
        try:
            r = redis_mod.Redis(host="localhost", port=6379, decode_responses=True)
            r.ping()
        except redis_mod.ConnectionError:
            pytest.skip("Redis not running")

        from job_board.cache import get_cached

        result = get_cached(r, "nonexistent:key")
        assert result is None
