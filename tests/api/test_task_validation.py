"""
Validation tests for POST /tasks.

Verifies that invalid task-creation payloads are rejected with HTTP 400
and a descriptive error message, per the rules enforced in
api/routes/tasks.js (validateTask).
"""
import os
from datetime import date, timedelta
from typing import Any, Dict

import pytest
import requests


def test_create_task_missing_title_returns_400(auth_headers: Dict[str, str]) -> None:
    """A task without a title must be rejected with a 400 and a 'Title is required' error."""
    api_base_url = os.environ.get("API_BASE_URL", "http://localhost:3001")
    payload: Dict[str, Any] = {
        "description": "Task missing its title",
        "priority": "medium",
    }

    response = requests.post(f"{api_base_url}/tasks", json=payload, headers=auth_headers, timeout=10)

    assert response.status_code == 400, f"Expected 400 for missing title, got {response.status_code}"
    body = response.json()
    assert "Title is required" in body["error"], f"Expected missing-title error, got: {body['error']}"


def test_create_task_title_too_long_returns_400(auth_headers: Dict[str, str]) -> None:
    """A title exceeding 200 characters must be rejected with a 400 and a length error message."""
    api_base_url = os.environ.get("API_BASE_URL", "http://localhost:3001")
    payload: Dict[str, Any] = {
        "title": "x" * 201,
        "priority": "medium",
    }

    response = requests.post(f"{api_base_url}/tasks", json=payload, headers=auth_headers, timeout=10)

    assert response.status_code == 400, f"Expected 400 for oversized title, got {response.status_code}"
    body = response.json()
    assert "Title must not exceed 200 characters" in body["error"], (
        f"Expected title-length error, got: {body['error']}"
    )


def test_create_task_past_due_date_returns_400(auth_headers: Dict[str, str]) -> None:
    """A due_date in the past must be rejected with a 400 and a due-date error message."""
    api_base_url = os.environ.get("API_BASE_URL", "http://localhost:3001")
    past_due_date = (date.today() - timedelta(days=1)).isoformat()
    payload: Dict[str, Any] = {
        "title": "Task with a past due date",
        "due_date": past_due_date,
    }

    response = requests.post(f"{api_base_url}/tasks", json=payload, headers=auth_headers, timeout=10)

    assert response.status_code == 400, f"Expected 400 for past due date, got {response.status_code}"
    body = response.json()
    assert "Due date must be today or in the future" in body["error"], (
        f"Expected past-due-date error, got: {body['error']}"
    )


def test_create_task_invalid_priority_returns_400(auth_headers: Dict[str, str]) -> None:
    """A priority outside low|medium|high must be rejected with a 400 and a priority error message."""
    api_base_url = os.environ.get("API_BASE_URL", "http://localhost:3001")
    payload: Dict[str, Any] = {
        "title": "Task with an invalid priority",
        "priority": "urgent",
    }

    response = requests.post(f"{api_base_url}/tasks", json=payload, headers=auth_headers, timeout=10)

    assert response.status_code == 400, f"Expected 400 for invalid priority, got {response.status_code}"
    body = response.json()
    assert "Priority must be one of" in body["error"], f"Expected invalid-priority error, got: {body['error']}"
