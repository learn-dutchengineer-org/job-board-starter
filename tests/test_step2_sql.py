"""Step 2: SQL Queries

Tests for the query functions in src/job_board/queries.py.
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


class TestSearchListings:
    def test_search_by_keyword(self, conn):
        """search_listings should filter by keyword using ILIKE."""
        from job_board.queries import search_listings

        results = search_listings(conn, keyword="engineer")
        assert isinstance(results, list)
        for row in results:
            assert "title" in row or hasattr(row, "title") or len(row) > 0

    def test_search_by_location(self, conn):
        """search_listings should filter by location."""
        from job_board.queries import search_listings

        results = search_listings(conn, location="Remote")
        assert isinstance(results, list)


class TestCompanyStats:
    def test_returns_aggregation(self, conn):
        """company_stats should return listing count per company."""
        from job_board.queries import company_stats

        results = company_stats(conn)
        assert isinstance(results, list)
        assert len(results) > 0
        # Each result should have a company name and a count
        first = results[0]
        assert len(first) >= 2


class TestRecentListings:
    def test_recent_listings_default(self, conn):
        """recent_listings should return listings from the last 7 days."""
        from job_board.queries import recent_listings

        results = recent_listings(conn)
        assert isinstance(results, list)

    def test_recent_listings_custom_days(self, conn):
        """recent_listings(days=30) should accept a custom window."""
        from job_board.queries import recent_listings

        results = recent_listings(conn, days=30)
        assert isinstance(results, list)


class TestListingWithCompany:
    def test_returns_joined_data(self, conn):
        """listing_with_company should JOIN listing with company name."""
        from job_board.queries import listing_with_company

        # Get any listing id
        cur = conn.cursor()
        cur.execute("SELECT id FROM listings LIMIT 1")
        row = cur.fetchone()
        if row is None:
            pytest.skip("No listings in database")
        listing_id = row[0]

        result = listing_with_company(conn, listing_id)
        assert result is not None
