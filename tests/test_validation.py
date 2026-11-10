"""Negative tests: the API must reject bad input with clear, correct errors."""

import pytest

from framework.factories import task_payload


@pytest.mark.parametrize(
    "payload, field",
    [
        ({}, "title"),
        ({"title": ""}, "title"),
        ({"title": "   "}, "title"),
        ({"title": 123}, "title"),
        ({"title": "x" * 121}, "title"),
        ({"title": "ok", "status": "archived"}, "status"),
        ({"title": "ok", "priority": "urgent"}, "priority"),
    ],
    ids=["missing", "empty", "blank", "not-string", "too-long", "bad-status", "bad-priority"],
)
def test_create_rejects_invalid_fields(tasks, payload, field):
    resp = tasks.create(**payload)
    assert resp.status_code == 422
    assert field in resp.json()["details"]


def test_title_at_max_length_is_accepted(tasks):
    """Boundary value: 120 chars is the limit, so it must pass."""
    assert tasks.create(title="x" * 120).status_code == 201


def test_create_rejects_non_json_body(client):
    resp = client.post("/tasks", data="not json", headers={"Content-Type": "text/plain"})
    assert resp.status_code == 400


def test_update_rejects_unknown_fields(tasks):
    task = tasks.create(**task_payload()).json()
    resp = tasks.update(task["id"], id=999)
    assert resp.status_code == 422
    assert tasks.get(task["id"]).json()["id"] == task["id"], "id must not change"


@pytest.mark.parametrize("method", ["get", "delete"])
def test_missing_task_returns_404(tasks, method):
    resp = getattr(tasks, method)(987654)
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "params",
    [{"page": 0}, {"size": 0}, {"size": 51}, {"page": "abc"}],
    ids=["page-zero", "size-zero", "size-too-big", "page-not-int"],
)
def test_list_rejects_bad_pagination(tasks, params):
    assert tasks.list(**params).status_code == 400
