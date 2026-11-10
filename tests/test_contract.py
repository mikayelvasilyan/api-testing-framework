"""Contract tests: response bodies must match the JSON Schemas."""

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from framework import schemas
from framework.factories import task_payload


def assert_matches(instance, schema):
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=str)
    assert not errors, "\n".join(e.message for e in errors)


pytestmark = pytest.mark.contract


def test_task_schema(tasks):
    assert_matches(tasks.create(**task_payload()).json(), schemas.TASK)


def test_task_list_schema(tasks):
    tasks.create(**task_payload())
    assert_matches(tasks.list().json(), schemas.TASK_PAGE)


@pytest.mark.parametrize(
    "call",
    [lambda t: t.get(999999), lambda t: t.create(title="")],
    ids=["not-found", "validation"],
)
def test_error_schema(tasks, call):
    assert_matches(call(tasks).json(), schemas.ERROR)


def test_pagination_returns_requested_page(tasks):
    marker = "page-test"
    for i in range(5):
        tasks.create(title=f"{marker} {i}", status="in_progress")
    page = tasks.list(status="in_progress", page=2, size=2).json()
    assert page["page"] == 2 and page["size"] == 2
    assert len(page["items"]) <= 2
    assert page["total"] >= 5
