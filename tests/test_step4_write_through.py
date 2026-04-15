"""Step 4: Write-Through Caching

Tests for view count caching in src/job_board/cache.py.
"""

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


@pytest.fixture
def redis_client():
    redis_mod = pytest.importorskip("redis")
    try:
        r = redis_mod.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
    except redis_mod.ConnectionError:
        pytest.skip("Redis not running")
    yield r


class TestViewCountColumn:
    def test_view_count_column_exists(self, conn):
        """The listings table should have a view_count column."""
        cur = conn.cursor()
        cur.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = 'listings' AND column_name = 'view_count'"
        )
        row = cur.fetchone()
        assert row is not None, "view_count column not found on listings table"
        assert row[1] == "integer"


class TestRecordView:
    def test_record_view_increments_db(self, conn, redis_client):
        """record_view should increment view_count in PostgreSQL."""
        from job_board.cache import record_view

        cur = conn.cursor()
        cur.execute("SELECT id, view_count FROM listings LIMIT 1")
        row = cur.fetchone()
        if row is None:
            pytest.skip("No listings in database")
        listing_id, initial_count = row[0], row[1] or 0

        record_view(conn, redis_client, listing_id)

        cur.execute("SELECT view_count FROM listings WHERE id = %s", (listing_id,))
        new_count = cur.fetchone()[0]
        assert new_count == initial_count + 1

    def test_record_view_increments_redis(self, conn, redis_client):
        """record_view should set or increment the view count in Redis."""
        from job_board.cache import record_view

        cur = conn.cursor()
        cur.execute("SELECT id FROM listings LIMIT 1")
        row = cur.fetchone()
        if row is None:
            pytest.skip("No listings in database")
        listing_id = row[0]

        key = f"view_count:{listing_id}"
        redis_client.delete(key)

        record_view(conn, redis_client, listing_id)
        count = redis_client.get(key)
        assert count is not None
        assert int(count) >= 1


class TestGetViewCount:
    def test_get_view_count_reads_redis_first(self, conn, redis_client):
        """get_view_count should return the Redis value when present."""
        from job_board.cache import get_view_count

        cur = conn.cursor()
        cur.execute("SELECT id FROM listings LIMIT 1")
        row = cur.fetchone()
        if row is None:
            pytest.skip("No listings in database")
        listing_id = row[0]

        key = f"view_count:{listing_id}"
        redis_client.set(key, 42)

        count = get_view_count(conn, redis_client, listing_id)
        assert count == 42

    def test_get_view_count_falls_back_to_db(self, conn, redis_client):
        """get_view_count should read from PostgreSQL on Redis cache miss."""
        from job_board.cache import get_view_count

        cur = conn.cursor()
        cur.execute("SELECT id, view_count FROM listings LIMIT 1")
        row = cur.fetchone()
        if row is None:
            pytest.skip("No listings in database")
        listing_id, db_count = row[0], row[1] or 0

        key = f"view_count:{listing_id}"
        redis_client.delete(key)

        count = get_view_count(conn, redis_client, listing_id)
        assert count == db_count
