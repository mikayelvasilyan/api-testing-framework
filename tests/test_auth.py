"""Security tests: every non-public endpoint requires a valid token."""

import pytest

from framework.client import ApiClient

PROTECTED = [
    ("GET", "/tasks"),
    ("POST", "/tasks"),
    ("GET", "/tasks/1"),
    ("PATCH", "/tasks/1"),
    ("DELETE", "/tasks/1"),
]


@pytest.mark.parametrize("method, path", PROTECTED)
def test_requests_without_token_are_rejected(anon_client, method, path):
    assert anon_client.request(method, path, json={}).status_code == 401


@pytest.mark.parametrize("bad_token", ["wrong", "", "Bearer test-token-123"])
def test_requests_with_wrong_token_are_rejected(base_url, bad_token):
    client = ApiClient(base_url, token=bad_token or None)
    assert client.get("/tasks").status_code == 401
