"""Shared fixtures.

By default a fresh copy of the mock API is started in a background thread for
the test session. Set API_BASE_URL (and API_TOKEN) to run the same suite
against a deployed environment instead.
"""

from __future__ import annotations

import os
import threading

import pytest
from werkzeug.serving import make_server

from framework.client import ApiClient, TasksApi
from mock_server.app import API_TOKEN, create_app


@pytest.fixture(scope="session")
def base_url():
    external = os.getenv("API_BASE_URL")
    if external:
        yield external
        return
    server = make_server("127.0.0.1", 0, create_app())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="session")
def token():
    return os.getenv("API_TOKEN", API_TOKEN)


@pytest.fixture
def client(base_url, token):
    return ApiClient(base_url, token=token)


@pytest.fixture
def anon_client(base_url):
    return ApiClient(base_url)


@pytest.fixture
def tasks(client):
    """Tasks API that deletes everything a test created, even if the test fails."""
    api = TasksApi(client)
    created: list[int] = []
    original_create = api.create

    def tracking_create(**fields):
        resp = original_create(**fields)
        if resp.status_code == 201:
            created.append(resp.json()["id"])
        return resp

    api.create = tracking_create
    yield api
    for task_id in created:
        api.delete(task_id)
