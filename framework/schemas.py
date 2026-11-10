"""JSON Schemas describing the API contract. Contract tests validate every
response shape against these, so breaking changes are caught early."""

TASK = {
    "type": "object",
    "required": ["id", "title", "status", "priority", "created_at"],
    "additionalProperties": False,
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "title": {"type": "string", "minLength": 1, "maxLength": 120},
        "status": {"enum": ["todo", "in_progress", "done"]},
        "priority": {"enum": ["low", "medium", "high"]},
        "created_at": {"type": "string", "format": "date-time"},
    },
}

TASK_PAGE = {
    "type": "object",
    "required": ["items", "page", "size", "total"],
    "properties": {
        "items": {"type": "array", "items": TASK},
        "page": {"type": "integer", "minimum": 1},
        "size": {"type": "integer", "minimum": 1},
        "total": {"type": "integer", "minimum": 0},
    },
}

ERROR = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": {"type": "string"},
        "details": {"type": "object", "additionalProperties": {"type": "string"}},
    },
}
