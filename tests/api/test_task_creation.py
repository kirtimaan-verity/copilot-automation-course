"""POST /tasks endpoint tests."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, Optional

import pytest
import requests

from tests.fixtures.data_factory import TaskFactory


def _delete_task_if_created(api_base_url: str, auth_headers: Dict[str, str], task_id: Optional[int]) -> None:
    """Delete a created task to keep tests independent."""
    if task_id is None:
        return
    delete_response = requests.delete(f"{api_base_url}/tasks/{task_id}", headers=auth_headers, timeout=10)
    assert delete_response.status_code in (204, 404), (
        f"Expected cleanup delete to return 204 or 404, got {delete_response.status_code}"
    )


def test_create_task_returns_201(
    api_base_url: str,
    auth_headers: Dict[str, str],
) -> None:
    """POST /tasks should create a valid task and return HTTP 201."""
    created_task_id: Optional[int] = None
    payload = TaskFactory.valid_task()
    response = requests.post(f"{api_base_url}/tasks", json=payload, headers=auth_headers, timeout=10)

    try:
        assert response.status_code == 201, f"Expected 201 for valid task creation, got {response.status_code}"
        body = response.json()
        created_task_id = body.get("id")
        assert body["title"] == payload["title"], f"Expected title '{payload['title']}', got {body['title']}"
    finally:
        _delete_task_if_created(api_base_url, auth_headers, created_task_id)


def test_create_task_response_contains_id(
    api_base_url: str,
    auth_headers: Dict[str, str],
) -> None:
    """POST /tasks response should include a positive integer id for the new task."""
    created_task_id: Optional[int] = None
    payload = TaskFactory.valid_task()
    response = requests.post(f"{api_base_url}/tasks", json=payload, headers=auth_headers, timeout=10)

    try:
        assert response.status_code == 201, f"Expected 201 for valid task creation, got {response.status_code}"
        body = response.json()
        created_task_id = body.get("id")
        assert isinstance(created_task_id, int), f"Expected response id to be int, got {type(created_task_id)}"
        assert created_task_id > 0, f"Expected response id to be > 0, got {created_task_id}"
    finally:
        _delete_task_if_created(api_base_url, auth_headers, created_task_id)


def test_create_task_default_priority_is_medium(
    api_base_url: str,
    auth_headers: Dict[str, str],
) -> None:
    """POST /tasks should default priority to medium when priority is not provided."""
    created_task_id: Optional[int] = None
    payload = TaskFactory.valid_task()
    payload.pop("priority", None)
    response = requests.post(f"{api_base_url}/tasks", json=payload, headers=auth_headers, timeout=10)

    try:
        assert response.status_code == 201, f"Expected 201 when creating task without priority, got {response.status_code}"
        body = response.json()
        created_task_id = body.get("id")
        assert body["priority"] == "medium", f"Expected default priority 'medium', got {body['priority']}"
    finally:
        _delete_task_if_created(api_base_url, auth_headers, created_task_id)


def test_create_task_with_all_fields(
    api_base_url: str,
    auth_headers: Dict[str, str],
) -> None:
    """POST /tasks should persist and return all provided task fields."""
    created_task_id: Optional[int] = None
    payload = TaskFactory.valid_task()
    payload["status"] = "active"
    # user_id is nullable but must reference an existing users.id when non-null.
    # Use explicit null to keep "all fields" coverage without FK dependency on seed data.
    payload["user_id"] = None
    response = requests.post(f"{api_base_url}/tasks", json=payload, headers=auth_headers, timeout=10)

    try:
        assert response.status_code == 201, f"Expected 201 for full payload task creation, got {response.status_code}"
        body = response.json()
        created_task_id = body.get("id")
        assert body["title"] == payload["title"], f"Expected title '{payload['title']}', got {body['title']}"
        assert body["description"] == payload["description"], "Expected response description to match request description"
        assert body["due_date"] == payload["due_date"], f"Expected due_date '{payload['due_date']}', got {body['due_date']}"
        assert body["priority"] == payload["priority"], f"Expected priority '{payload['priority']}', got {body['priority']}"
        assert body["status"] == payload["status"], f"Expected status '{payload['status']}', got {body['status']}"
        assert body["user_id"] == payload["user_id"], f"Expected user_id {payload['user_id']}, got {body['user_id']}"
    finally:
        _delete_task_if_created(api_base_url, auth_headers, created_task_id)


@pytest.mark.parametrize(
    ("payload_override", "expected_error_substring"),
    [
        ({"title": None}, "Title is required"),
        ({"title": "x" * 201}, "Title must not exceed 200 characters"),
        ({"due_date": (date.today() - timedelta(days=1)).isoformat()}, "Due date must be today or in the future"),
        ({"priority": "urgent"}, "Priority must be one of: low, medium, high"),
    ],
)
def test_create_task_validation_errors_return_400(
    api_base_url: str,
    auth_headers: Dict[str, str],
    payload_override: Dict[str, Any],
    expected_error_substring: str,
) -> None:
    """POST /tasks should return 400 with validation details for invalid payload variants."""
    payload = TaskFactory.valid_task()
    payload.update(payload_override)
    if payload_override.get("title", "__unchanged__") is None:
        payload.pop("title", None)

    response = requests.post(f"{api_base_url}/tasks", json=payload, headers=auth_headers, timeout=10)

    assert response.status_code == 400, f"Expected 400 for invalid task payload, got {response.status_code}"
    body = response.json()
    assert "error" in body, "Expected validation response body to contain 'error' field"
    assert "errors" in body, "Expected validation response body to contain 'errors' field"
    assert isinstance(body["errors"], list), f"Expected 'errors' to be a list, got {type(body['errors'])}"
    assert expected_error_substring in body["error"], (
        f"Expected error text to include '{expected_error_substring}', got '{body['error']}'"
    )
