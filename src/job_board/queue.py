"""Message queue helpers using Redis."""

import json
import time

QUEUE_KEY = "job_board:events"
DEAD_LETTER_KEY = "job_board:dead_letters"


def publish_event(r, event_type: str, payload: dict) -> None:
    """Push a JSON-encoded event onto the queue.

    Args:
        r: Redis client
        event_type: Event name (e.g. "listing_created")
        payload: Event data dict. Include max_retries to control retry behaviour.
    """
    # TODO: build the event dict with type, payload, and timestamp
    # TODO: JSON-encode it and LPUSH onto QUEUE_KEY
    raise NotImplementedError


def get_dead_letters(r) -> list[dict]:
    """Return all events in the dead letter queue.

    Args:
        r: Redis client

    Returns:
        List of decoded event dicts.
    """
    # TODO: use LRANGE to read all items from DEAD_LETTER_KEY
    # TODO: JSON-decode each item and return as a list
    raise NotImplementedError
