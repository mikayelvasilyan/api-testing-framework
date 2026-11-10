"""Test data builders: unique, readable payloads with sensible defaults."""

import uuid


def task_payload(**overrides) -> dict:
    payload = {
        "title": f"Task {uuid.uuid4().hex[:8]}",
        "status": "todo",
        "priority": "medium",
    }
    payload.update(overrides)
    return payload
