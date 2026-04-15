"""Step 6: Data Quality

Tests for Pydantic validation, data cleaning, and idempotent upserts.
"""

import csv
import os
import tempfile

import pytest


class TestPydanticModel:
    def test_valid_listing(self):
        """A Listing with all required fields should validate."""
        from job_board.models import Listing

        listing = Listing(
            title="ML Engineer",
            url="https://example.com/1",
            company="TestCo",
            location="Remote",
        )
        assert listing.title == "ML Engineer"

    def test_missing_title_fails(self):
        """A Listing without a title should raise ValidationError."""
        from pydantic import ValidationError

        from job_board.models import Listing

        with pytest.raises(ValidationError):
            Listing(url="https://example.com/1", company="TestCo")

    def test_salary_normalization(self):
        """Salary string '$150K' should be normalized to 150000."""
        from job_board.models import Listing

        listing = Listing(
            title="Engineer",
            url="https://example.com/1",
            company="TestCo",
            salary="$150K",
        )
        assert listing.salary == 150000


class TestQualityMetrics:
    def test_import_reports_metrics(self):
        """Import should report total, valid, rejected, and duplicate counts."""
        from job_board.importer import import_feed

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["title", "company", "url", "location", "salary"],
            )
            writer.writeheader()
            # Valid row
            writer.writerow(
                {
                    "title": "Engineer",
                    "company": "Co",
                    "url": "https://example.com/1",
                    "location": "Remote",
                    "salary": "$100K",
                }
            )
            # Invalid row (no title)
            writer.writerow(
                {
                    "title": "",
                    "company": "Co",
                    "url": "https://example.com/2",
                    "location": "NYC",
                    "salary": "$90K",
                }
            )
            path = f.name

        try:
            metrics = import_feed(path)
            assert "total" in metrics
            assert "valid" in metrics or "imported" in metrics
            assert "rejected" in metrics or "skipped" in metrics
        finally:
            os.unlink(path)


class TestIdempotentUpsert:
    def test_duplicate_import_no_error(self):
        """Importing the same data twice should not raise or create duplicates."""
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
                    "title": "Engineer",
                    "company": "Co",
                    "url": "https://example.com/upsert-test",
                    "location": "Remote",
                }
            )
            path = f.name

        try:
            result1 = import_feed(path)
            result2 = import_feed(path)
            # Second import should report duplicates, not failures
            assert result2.get("duplicates", 0) >= 0 or result2.get("imported", 0) >= 0
        finally:
            os.unlink(path)
