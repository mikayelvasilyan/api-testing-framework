# API Testing Framework (Python + pytest)

![tests](https://github.com/mikayelvasilyan/api-testing-framework/actions/workflows/tests.yml/badge.svg)

A clean, reusable REST API test framework built with **Python, pytest, requests and JSON Schema**, running in **GitHub Actions** on every push.

> Personal portfolio project by **Mikayel Vasilyan**, QA / Software Automation Engineer.
> It shows how I structure API test automation for real projects.

## What this shows

| Area | What's covered |
|---|---|
| **Functional** | Create / read / update / delete flows and an end-to-end user story |
| **Negative & boundary** | 7 invalid-input cases, max-length boundary, bad JSON, unknown fields, 404s, bad pagination |
| **Security** | Every protected endpoint rejects missing or wrong tokens |
| **Contract** | Every response is validated against a JSON Schema (catches breaking API changes) |
| **Performance** | Response-time limit and 30 concurrent writes with unique IDs |
| **CI/CD** | GitHub Actions on Python 3.11–3.13, HTML report saved as a build artifact |

**37 tests, run in under a second.** Each test cleans up the data it creates, so tests are independent and can run in any order.

## Design

```
framework/
  client.py      ApiClient (session, auth, timeouts, timing, logging) + TasksApi helpers
  schemas.py     JSON Schemas for the API contract
  factories.py   Test data builders with unique values
mock_server/
  app.py         Small Flask "Task Manager" API used as the system under test
tests/
  conftest.py    Fixtures: starts the API, clients, automatic cleanup
  test_*.py      Tests grouped by type (crud, validation, auth, contract, performance)
```

- **Layered:** tests call `tasks.create(...)`, not raw HTTP, so they read like business steps and survive URL changes.
- **Self-contained:** the API under test starts automatically on a free port, so the suite never fails because an outside service is down.
- **Reusable:** point it at any environment with environment variables:

```bash
API_BASE_URL=https://staging.example.com API_TOKEN=... pytest
```

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                                   # all tests
pytest -m smoke                          # only main flows
pytest --html=report.html --self-contained-html   # HTML report
```

## Proof the tests catch bugs

I injected two bugs into the API (titles not trimmed, length limit raised to 200). The suite failed on exactly the right tests:

```
FAILED tests/test_tasks_crud.py::test_create_task_returns_201_with_defaults
FAILED tests/test_validation.py::test_create_rejects_invalid_fields[too-long]
2 failed, 35 passed
```

## Tech

Python · pytest · requests · jsonschema · Flask · GitHub Actions · pytest-html

## License

MIT
