"""Step 1: Database Setup

Tests for PostgreSQL connection, schema, and seed data.
Requires: docker compose up -d (PostgreSQL running)
"""

import os

import pytest

psycopg2 = pytest.importorskip("psycopg2")

DATABASE_URL = os.environ.get("DATABASE_URL", "")


@pytest.fixture
def conn():
    """Return a psycopg2 connection, rolling back after each test."""
    if not DATABASE_URL:
        pytest.skip("DATABASE_URL not set")
    connection = psycopg2.connect(DATABASE_URL)
    yield connection
    connection.rollback()
    connection.close()


class TestSchema:
    def test_companies_table_exists(self, conn):
        """The companies table should exist after running the migration."""
        cur = conn.cursor()
        cur.execute(
            "SELECT EXISTS ("
            "  SELECT FROM information_schema.tables "
            "  WHERE table_name = 'companies'"
            ")"
        )
        assert cur.fetchone()[0] is True

    def test_listings_table_exists(self, conn):
        """The listings table should exist after running the migration."""
        cur = conn.cursor()
        cur.execute(
            "SELECT EXISTS ("
            "  SELECT FROM information_schema.tables "
            "  WHERE table_name = 'listings'"
            ")"
        )
        assert cur.fetchone()[0] is True


class TestSeedData:
    def test_companies_seeded(self, conn):
        """There should be at least 3 companies after running seed.py."""
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM companies")
        count = cur.fetchone()[0]
        assert count >= 3, f"Expected at least 3 companies, got {count}"

    def test_listings_seeded(self, conn):
        """There should be at least 5 listings after running seed.py."""
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM listings")
        count = cur.fetchone()[0]
        assert count >= 5, f"Expected at least 5 listings, got {count}"

    def test_listings_reference_companies(self, conn):
        """Every listing should reference a valid company."""
        cur = conn.cursor()
        cur.execute(
            "SELECT l.id FROM listings l "
            "LEFT JOIN companies c ON l.company_id = c.id "
            "WHERE c.id IS NULL"
        )
        orphans = cur.fetchall()
        assert len(orphans) == 0, f"Found orphan listings: {orphans}"
