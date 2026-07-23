"""Tests for GET /tasks, PUT /tasks/{id}, and DELETE /tasks/{id}."""

from __future__ import annotations

from typing import Any, Dict

import requests


def test_get_tasks_returns_200_and_list(api_base_url: str) -> None:
    """GET /tasks should return HTTP 200 with a JSON list response body."""
    response = requests.get(f"{api_base_url}/tasks", timeout=10)

    assert response.status_code == 200, f"Expected 200 for GET /tasks, got {response.status_code}"
    body = response.json()
    assert isinstance(body, list), f"Expected GET /tasks response body to be a list, got {type(body)}"


def test_get_tasks_filter_by_status_works(api_base_url: str, created_task: Dict[str, Any]) -> None:
    """GET /tasks?status=active should include the created active task and return only active tasks."""
    response = requests.get(f"{api_base_url}/tasks", params={"status": "active"}, timeout=10)

    assert response.status_code == 200, f"Expected 200 for status-filtered GET /tasks, got {response.status_code}"
    body = response.json()
    assert isinstance(body, list), f"Expected status-filtered response body to be a list, got {type(body)}"
    assert any(task["id"] == created_task["id"] for task in body), (
        f"Expected created task id {created_task['id']} to appear in status-filtered results"
    )
    assert all(task["status"] == "active" for task in body), "Expected every task in status-filtered results to be active"


def test_get_tasks_filter_by_priority_works(api_base_url: str, created_task: Dict[str, Any]) -> None:
    """GET /tasks?priority=medium should include the created medium-priority task and return only medium tasks."""
    response = requests.get(f"{api_base_url}/tasks", params={"priority": "medium"}, timeout=10)

    assert response.status_code == 200, f"Expected 200 for priority-filtered GET /tasks, got {response.status_code}"
    body = response.json()
    assert isinstance(body, list), f"Expected priority-filtered response body to be a list, got {type(body)}"
    assert any(task["id"] == created_task["id"] for task in body), (
        f"Expected created task id {created_task['id']} to appear in priority-filtered results"
    )
    assert all(task["priority"] == "medium" for task in body), (
        "Expected every task in priority-filtered results to have medium priority"
    )


def test_put_task_returns_200_with_updated_fields(
    api_base_url: str,
    auth_headers: Dict[str, str],
    created_task: Dict[str, Any],
) -> None:
    """PUT /tasks/{id} should return 200 and response body with updated fields."""
    update_payload = {
        "title": "Updated task title",
        "description": "Updated task description",
        "priority": "high",
        "status": "completed",
    }
    response = requests.put(
        f"{api_base_url}/tasks/{created_task['id']}",
        json=update_payload,
        headers=auth_headers,
        timeout=10,
    )

    assert response.status_code == 200, f"Expected 200 for valid task update, got {response.status_code}"
    body = response.json()
    assert body["id"] == created_task["id"], f"Expected updated task id {created_task['id']}, got {body['id']}"
    assert body["title"] == update_payload["title"], f"Expected updated title '{update_payload['title']}', got {body['title']}"
    assert body["description"] == update_payload["description"], (
        f"Expected updated description '{update_payload['description']}', got {body['description']}"
    )
    assert body["priority"] == update_payload["priority"], (
        f"Expected updated priority '{update_payload['priority']}', got {body['priority']}"
    )
    assert body["status"] == update_payload["status"], (
        f"Expected updated status '{update_payload['status']}', got {body['status']}"
    )


def test_put_task_non_existent_id_returns_404(
    api_base_url: str,
    auth_headers: Dict[str, str],
    test_task_data: Dict[str, Any],
) -> None:
    """PUT /tasks/{id} should return 404 when the target task does not exist."""
    non_existent_task_id = 9_999_999
    response = requests.put(
        f"{api_base_url}/tasks/{non_existent_task_id}",
        json=test_task_data,
        headers=auth_headers,
        timeout=10,
    )

    assert response.status_code == 404, f"Expected 404 for update of non-existent task id, got {response.status_code}"
    body = response.json()
    assert body["error"] == "Task not found", f"Expected 'Task not found' error, got {body.get('error')}"


def test_delete_task_returns_204_and_subsequent_get_returns_404(
    api_base_url: str,
    auth_headers: Dict[str, str],
    created_task: Dict[str, Any],
) -> None:
    """DELETE /tasks/{id} should return 204 and then GET /tasks/{id} should return 404."""
    delete_response = requests.delete(f"{api_base_url}/tasks/{created_task['id']}", headers=auth_headers, timeout=10)

    assert delete_response.status_code == 204, f"Expected 204 for task delete, got {delete_response.status_code}"
    assert delete_response.text == "", f"Expected empty body for 204 delete, got: {delete_response.text}"

    get_response = requests.get(f"{api_base_url}/tasks/{created_task['id']}", timeout=10)
    assert get_response.status_code == 404, f"Expected 404 for GET after delete, got {get_response.status_code}"
    get_body = get_response.json()
    assert get_body["error"] == "Task not found", f"Expected 'Task not found' after delete, got {get_body.get('error')}"
