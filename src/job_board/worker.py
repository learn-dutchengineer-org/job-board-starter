"""Event worker that consumes from the Redis queue."""

import json
import logging

from job_board.queue import DEAD_LETTER_KEY, QUEUE_KEY

logger = logging.getLogger(__name__)


def handle_listing_created(r, payload: dict) -> None:
    """Handle a listing_created event.

    Args:
        r: Redis client
        payload: Event payload containing listing_id.

    Raises:
        ValueError: If listing_id is missing or None.
    """
    listing_id = payload.get("listing_id")
    if listing_id is None:
        raise ValueError("listing_id is required")
    logger.info("Updating search index for listing %s", listing_id)


def process_next_event(r, timeout: int = 5) -> dict | None:
    """Read and process one event from the queue.

    Uses BRPOP to block until an event arrives or the timeout expires.

    Args:
        r: Redis client
        timeout: Seconds to wait for an event before returning None.

    Returns:
        The processed event dict, or None if the queue was empty.
    """
    # TODO: use BRPOP to read one event from QUEUE_KEY with the given timeout
    # TODO: if nothing arrived, return None
    # TODO: JSON-decode the event
    # TODO: dispatch to the correct handler based on event["type"]
    #       - "listing_created" -> handle_listing_created(r, event["payload"])
    #       - unknown types -> log a warning and return the event
    # TODO: wrap the handler call in try/except:
    #       - on success: return the event
    #       - on failure: decrement max_retries in the payload
    #         - if max_retries > 0: re-queue with LPUSH and return the event
    #         - if max_retries <= 0: push to DEAD_LETTER_KEY and return the event
    raise NotImplementedError
