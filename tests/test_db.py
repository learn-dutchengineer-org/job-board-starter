import pytest


class TestDatabaseConnection:
    def test_connection(self):
        """get_connection should return a valid psycopg2 connection.

        Requires PostgreSQL running via docker compose.
        """
        pytest.skip("Implement in Lesson 1")

    def test_create_listing(self):
        """Should be able to insert a company and listing, then query it back.

        Steps:
            1. Insert a company
            2. Insert a listing referencing that company
            3. SELECT the listing and verify the title matches
        """
        pytest.skip("Implement in Lesson 1")
