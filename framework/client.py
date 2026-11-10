"""Thin, reusable HTTP client for API tests.

Wraps `requests.Session` with a base URL, default auth, timeouts and request
logging, so tests read like business steps instead of HTTP plumbing.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import requests

log = logging.getLogger("api")


@dataclass
class TimedResponse:
    response: requests.Response
    elapsed_ms: float

    def __getattr__(self, name):
        return getattr(self.response, name)


class ApiClient:
    def __init__(self, base_url: str, token: str | None = None, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/json"
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def request(self, method: str, path: str, **kwargs) -> TimedResponse:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        start = time.perf_counter()
        response = self.session.request(method, url, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        log.info("%s %s -> %s (%.1f ms)", method, path, response.status_code, elapsed)
        return TimedResponse(response, elapsed)

    def get(self, path: str, **kw) -> TimedResponse:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw) -> TimedResponse:
        return self.request("POST", path, **kw)

    def patch(self, path: str, **kw) -> TimedResponse:
        return self.request("PATCH", path, **kw)

    def delete(self, path: str, **kw) -> TimedResponse:
        return self.request("DELETE", path, **kw)


class TasksApi:
    """Domain-level helpers on top of ApiClient (a simple API 'page object')."""

    def __init__(self, client: ApiClient):
        self.client = client

    def create(self, **fields) -> TimedResponse:
        return self.client.post("/tasks", json=fields)

    def get(self, task_id: int) -> TimedResponse:
        return self.client.get(f"/tasks/{task_id}")

    def list(self, **params) -> TimedResponse:
        return self.client.get("/tasks", params=params)

    def update(self, task_id: int, **fields) -> TimedResponse:
        return self.client.patch(f"/tasks/{task_id}", json=fields)

    def delete(self, task_id: int) -> TimedResponse:
        return self.client.delete(f"/tasks/{task_id}")
