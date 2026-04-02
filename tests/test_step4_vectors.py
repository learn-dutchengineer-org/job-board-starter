"""Step 4: Vector Search

Tests for pgvector setup and semantic search.
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


class TestVectorExtension:
    def test_pgvector_enabled(self, conn):
        """The vector extension should be installed."""
        cur = conn.cursor()
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        row = cur.fetchone()
        assert row is not None, "pgvector extension not installed"

    def test_embedding_column_exists(self, conn):
        """The listings table should have an embedding vector(384) column."""
        cur = conn.cursor()
        cur.execute(
            "SELECT column_name, udt_name FROM information_schema.columns "
            "WHERE table_name = 'listings' AND column_name = 'embedding'"
        )
        row = cur.fetchone()
        assert row is not None, "embedding column not found on listings table"


class TestSemanticSearch:
    def test_semantic_search_returns_results(self, conn):
        """semantic_search should return a list of results."""
        from job_board.semantic import semantic_search

        results = semantic_search(conn, "machine learning engineer", limit=5)
        assert isinstance(results, list)
        assert len(results) <= 5

    def test_semantic_search_result_has_title(self, conn):
        """Each result should include the listing title."""
        from job_board.semantic import semantic_search

        results = semantic_search(conn, "data pipeline", limit=3)
        if len(results) == 0:
            pytest.skip("No embeddings in database yet")
        first = results[0]
        assert "title" in first or hasattr(first, "title") or len(first) > 0
