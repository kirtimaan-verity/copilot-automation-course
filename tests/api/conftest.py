"""Shared fixtures for API tests."""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any, Dict, Iterator

import pytest
import requests
from faker import Faker


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Return API base URL from environment with local fallback."""
    return os.environ.get("API_BASE_URL", "http://localhost:3001")


@pytest.fixture(scope="session")
def auth_headers() -> Dict[str, str]:
    """Return common JSON headers for API requests."""
    return {"Content-Type": "application/json", "Accept": "application/json"}


@pytest.fixture(scope="function")
def test_task_data() -> Dict[str, Any]:
    """Return valid task payload data for create/update operations."""
    faker = Faker()
    due_date = (date.today() + timedelta(days=30)).isoformat()
    return {
        "title": faker.sentence(nb_words=4).rstrip("."),
        "description": faker.paragraph(nb_sentences=2),
        "due_date": due_date,
        "priority": "medium",
    }


@pytest.fixture(scope="function")
def created_task(
    api_base_url: str, auth_headers: Dict[str, str], test_task_data: Dict[str, Any]
) -> Iterator[Dict[str, Any]]:
    """Create a task and clean it up after the test."""
    create_response = requests.post(
        f"{api_base_url}/tasks",
        json=test_task_data,
        headers=auth_headers,
        timeout=10,
    )
    create_response.raise_for_status()
    task = create_response.json()

    task_id = task.get("id")
    if task_id is None:
        raise RuntimeError("Created task response did not include an 'id' field.")

    yield task

    delete_response = requests.delete(
        f"{api_base_url}/tasks/{task_id}",
        headers=auth_headers,
        timeout=10,
    )
    if delete_response.status_code not in (204, 404):
        delete_response.raise_for_status()