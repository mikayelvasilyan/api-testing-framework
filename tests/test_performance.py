"""Basic performance checks: response time limits and concurrent writes."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from framework.factories import task_payload

pytestmark = pytest.mark.performance

MAX_RESPONSE_MS = 500


def test_list_responds_within_limit(tasks):
    resp = tasks.list()
    assert resp.status_code == 200
    assert resp.elapsed_ms < MAX_RESPONSE_MS, f"took {resp.elapsed_ms:.0f} ms"


def test_concurrent_creates_get_unique_ids(tasks):
    with ThreadPoolExecutor(max_workers=10) as pool:
        responses = list(pool.map(lambda _: tasks.create(**task_payload()), range(30)))
    assert all(r.status_code == 201 for r in responses)
    ids = [r.json()["id"] for r in responses]
    assert len(set(ids)) == len(ids), "IDs must be unique under concurrent load"
