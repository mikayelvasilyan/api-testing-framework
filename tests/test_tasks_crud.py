"""Functional tests: the main create / read / update / delete flows."""

import pytest

from framework.factories import task_payload

pytestmark = pytest.mark.smoke


def test_health_is_public(anon_client):
    resp = anon_client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_task_returns_201_with_defaults(tasks):
    resp = tasks.create(title="  Write release notes  ")
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Write release notes", "title should be trimmed"
    assert body["status"] == "todo"
    assert body["priority"] == "medium"


def test_created_task_can_be_fetched(tasks):
    created = tasks.create(**task_payload(priority="high")).json()
    fetched = tasks.get(created["id"])
    assert fetched.status_code == 200
    assert fetched.json() == created


def test_partial_update_changes_only_given_fields(tasks):
    created = tasks.create(**task_payload()).json()
    resp = tasks.update(created["id"], status="done")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "done"
    assert body["title"] == created["title"]
    assert body["priority"] == created["priority"]


def test_delete_task_then_it_is_gone(tasks):
    created = tasks.create(**task_payload()).json()
    assert tasks.delete(created["id"]).status_code == 204
    assert tasks.get(created["id"]).status_code == 404


def test_end_to_end_task_lifecycle(tasks):
    """A user story: create -> start -> finish -> appears in 'done' list."""
    task = tasks.create(**task_payload(title="Prepare demo")).json()
    tasks.update(task["id"], status="in_progress")
    tasks.update(task["id"], status="done")
    done_ids = [t["id"] for t in tasks.list(status="done", size=50).json()["items"]]
    assert task["id"] in done_ids
