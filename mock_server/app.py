"""A small in-memory Task Manager REST API used as the system under test.

It is intentionally simple but realistic: token auth, CRUD, validation errors,
pagination and filtering. Tests run against it locally and in CI, so the suite
is fast and never flaky because of a third-party service being down.
"""

from __future__ import annotations

import itertools
import threading
from datetime import datetime, timezone

from flask import Flask, jsonify, request

API_TOKEN = "test-token-123"
VALID_STATUSES = {"todo", "in_progress", "done"}
VALID_PRIORITIES = {"low", "medium", "high"}


def create_app() -> Flask:
    app = Flask(__name__)
    tasks: dict[int, dict] = {}
    ids = itertools.count(1)
    lock = threading.Lock()

    def error(status: int, message: str, details: dict | None = None):
        body = {"error": message}
        if details:
            body["details"] = details
        return jsonify(body), status

    def validate(payload: dict, partial: bool = False) -> dict:
        problems = {}
        if not partial or "title" in payload:
            title = payload.get("title")
            if not isinstance(title, str) or not title.strip():
                problems["title"] = "required, non-empty string"
            elif len(title) > 120:
                problems["title"] = "max length is 120"
        if "status" in payload and payload["status"] not in VALID_STATUSES:
            problems["status"] = f"must be one of {sorted(VALID_STATUSES)}"
        if "priority" in payload and payload["priority"] not in VALID_PRIORITIES:
            problems["priority"] = f"must be one of {sorted(VALID_PRIORITIES)}"
        return problems

    @app.before_request
    def check_auth():
        if request.path == "/health":
            return None
        header = request.headers.get("Authorization", "")
        if header != f"Bearer {API_TOKEN}":
            return error(401, "unauthorized")
        return None

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/tasks")
    def list_tasks():
        status = request.args.get("status")
        try:
            page = int(request.args.get("page", 1))
            size = int(request.args.get("size", 10))
        except ValueError:
            return error(400, "page and size must be integers")
        if page < 1 or not 1 <= size <= 50:
            return error(400, "page must be >= 1 and size between 1 and 50")
        items = sorted(tasks.values(), key=lambda t: t["id"])
        if status:
            items = [t for t in items if t["status"] == status]
        start = (page - 1) * size
        return jsonify(
            {"items": items[start : start + size], "page": page, "size": size, "total": len(items)}
        )

    @app.post("/tasks")
    def create_task():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return error(400, "body must be a JSON object")
        problems = validate(payload)
        if problems:
            return error(422, "validation failed", problems)
        with lock:
            task_id = next(ids)
            task = {
                "id": task_id,
                "title": payload["title"].strip(),
                "status": payload.get("status", "todo"),
                "priority": payload.get("priority", "medium"),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            tasks[task_id] = task
        return jsonify(task), 201

    @app.get("/tasks/<int:task_id>")
    def get_task(task_id: int):
        task = tasks.get(task_id)
        return jsonify(task) if task else error(404, "task not found")

    @app.patch("/tasks/<int:task_id>")
    def update_task(task_id: int):
        task = tasks.get(task_id)
        if not task:
            return error(404, "task not found")
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return error(400, "body must be a JSON object")
        unknown = set(payload) - {"title", "status", "priority"}
        if unknown:
            return error(422, "validation failed", {f: "unknown field" for f in sorted(unknown)})
        problems = validate(payload, partial=True)
        if problems:
            return error(422, "validation failed", problems)
        with lock:
            task.update(payload)
            if "title" in payload:
                task["title"] = payload["title"].strip()
        return jsonify(task)

    @app.delete("/tasks/<int:task_id>")
    def delete_task(task_id: int):
        with lock:
            if tasks.pop(task_id, None) is None:
                return error(404, "task not found")
        return "", 204

    return app


if __name__ == "__main__":
    create_app().run(port=5000, debug=False)
