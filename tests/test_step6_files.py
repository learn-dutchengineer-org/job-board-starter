"""Step 5: Data Files

Tests for CSV import, Parquet export, and DuckDB queries.
"""

import csv
import os
import tempfile

import pytest


class TestCSVImport:
    def test_import_valid_csv(self):
        """import_feed should parse a valid CSV and return inserted count."""
        from job_board.importer import import_feed

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "title",
                    "company",
                    "url",
                    "location",
                    "salary",
                    "posted_date",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "title": "ML Engineer",
                    "company": "TestCo",
                    "url": "https://example.com/1",
                    "location": "Remote",
                    "salary": "$150K",
                    "posted_date": "2026-01-15",
                }
            )
            writer.writerow(
                {
                    "title": "Data Scientist",
                    "company": "TestCo",
                    "url": "https://example.com/2",
                    "location": "NYC",
                    "salary": "$120K",
                    "posted_date": "2026-02-01",
                }
            )
            path = f.name

        try:
            result = import_feed(path)
            assert result["total"] == 2
            assert result["imported"] >= 1
        finally:
            os.unlink(path)

    def test_skip_missing_required_fields(self):
        """Rows missing title or url should be skipped."""
        from job_board.importer import import_feed

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["title", "company", "url", "location"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "title": "",
                    "company": "TestCo",
                    "url": "https://example.com/1",
                    "location": "Remote",
                }
            )
            writer.writerow(
                {
                    "title": "Valid Job",
                    "company": "TestCo",
                    "url": "",
                    "location": "Remote",
                }
            )
            path = f.name

        try:
            result = import_feed(path)
            assert result["skipped"] >= 2
        finally:
            os.unlink(path)

    def test_salary_parsing(self):
        """Salary strings like '$150K' should be converted to integers."""
        from job_board.importer import parse_salary

        assert parse_salary("$150K") == 150000
        assert parse_salary("$80K") == 80000
        assert parse_salary("") is None


class TestParquetExport:
    def test_export_creates_file(self):
        """export_parquet should create a .parquet file."""
        pandas = pytest.importorskip("pandas")

        from job_board.exporter import export_parquet

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "listings.parquet")
            export_parquet(path)
            assert os.path.exists(path)
            df = pandas.read_parquet(path)
            assert len(df) > 0


class TestDuckDBQuery:
    def test_query_parquet(self):
        """DuckDB should be able to query the exported Parquet file."""
        duckdb = pytest.importorskip("duckdb")
        pandas = pytest.importorskip("pandas")

        from job_board.exporter import export_parquet

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "listings.parquet")
            export_parquet(path)

            result = duckdb.sql(
                f"SELECT count(*) as cnt FROM '{path}'"
            ).fetchone()
            assert result[0] > 0
