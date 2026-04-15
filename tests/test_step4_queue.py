"""Step 4: Message Queue

Tests for Redis-backed event queue, worker dispatch, and dead letter queue.
"""

import json
import time

import pytest


@pytest.fixture
def redis_client():
    redis_mod = pytest.importorskip("redis")
    try:
        r = redis_mod.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
    except redis_mod.ConnectionError:
        pytest.skip("Redis not running")
    # Clean up test keys before each test
    r.delete("job_board:events", "job_board:dead_letters")
    yield r
    r.delete("job_board:events", "job_board:dead_letters")


class TestPublishEvent:
    def test_publish_adds_to_queue(self, redis_client):
        """publish_event should push a JSON event onto job_board:events."""
        from job_board.queue import publish_event

        publish_event(redis_client, "listing_created", {"listing_id": 42})
        length = redis_client.llen("job_board:events")
        assert length == 1

    def test_published_event_is_valid_json(self, redis_client):
        """Published event should be valid JSON with type and payload fields."""
        from job_board.queue import publish_event

        publish_event(redis_client, "listing_created", {"listing_id": 99})
        raw = redis_client.lindex("job_board:events", -1)
        event = json.loads(raw)
        assert event["type"] == "listing_created"
        assert event["payload"]["listing_id"] == 99

    def test_publish_multiple_events(self, redis_client):
        """Multiple events should all be queued."""
        from job_board.queue import publish_event

        for i in range(3):
            publish_event(redis_client, "listing_created", {"listing_id": i})
        assert redis_client.llen("job_board:events") == 3


class TestWorkerDispatch:
    def test_worker_processes_listing_created(self, redis_client):
        """Worker should consume a listing_created event without error."""
        from job_board.queue import publish_event
        from job_board.worker import process_next_event

        publish_event(redis_client, "listing_created", {"listing_id": 1})
        result = process_next_event(redis_client, timeout=1)
        assert result is not None
        assert redis_client.llen("job_board:events") == 0

    def test_worker_returns_none_on_empty_queue(self, redis_client):
        """process_next_event should return None when the queue is empty."""
        from job_board.worker import process_next_event

        result = process_next_event(redis_client, timeout=1)
        assert result is None

    def test_worker_handles_unknown_event_type(self, redis_client):
        """Worker should not crash on an unknown event type."""
        from job_board.queue import publish_event
        from job_board.worker import process_next_event

        publish_event(redis_client, "unknown_event", {"data": "something"})
        # Should not raise
        process_next_event(redis_client, timeout=1)


class TestDeadLetterQueue:
    def test_failed_event_goes_to_dead_letters(self, redis_client):
        """An event that exhausts retries should land in job_board:dead_letters."""
        from job_board.queue import get_dead_letters, publish_event
        from job_board.worker import process_next_event

        # Publish an event with a payload that will trigger a ValueError in the handler
        publish_event(
            redis_client,
            "listing_created",
            {"listing_id": None, "max_retries": 0},
        )
        process_next_event(redis_client, timeout=1)
        dead = get_dead_letters(redis_client)
        assert len(dead) >= 1

    def test_get_dead_letters_returns_list(self, redis_client):
        """get_dead_letters should always return a list."""
        from job_board.queue import get_dead_letters

        result = get_dead_letters(redis_client)
        assert isinstance(result, list)
