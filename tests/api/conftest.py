"""
Shared pytest fixtures for API tests.

Referenced in Module 4 Lab 16. This is the STARTING conftest —
students extend it during the lab. The created_task fixture
demonstrates the setup/teardown (yield) pattern that the slides
describe.

Run: source ../../.venv/bin/activate
     API_BASE_URL=http://localhost:3001 pytest tests/api/ -v
"""
import os
import pytest
import requests


@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for the API under test (from environment)."""
    return os.environ.get("API_BASE_URL", "http://localhost:3001")


@pytest.fixture(scope="session")
def auth_headers():
    """Standard request headers. Extend with auth token if needed."""
    return {"Content-Type": "application/json", "Accept": "application/json"}


@pytest.fixture
def test_task_data():
    """A valid task payload used by multiple tests."""
    from datetime import date, timedelta
    future = (date.today() + timedelta(days=30)).isoformat()
    return {
        "title": "Conftest sample task",
        "description": "Created by the test_task_data fixture",
        "due_date": future,
        "priority": "medium",
    }


@pytest.fixture
def created_task(api_base_url, auth_headers, test_task_data):
    """
    Creates a task before the test and deletes it afterwards.

    Demonstrates the setup/teardown pattern: everything before the
    yield is setup, everything after is teardown. Teardown runs even
    if the test raises an exception.
    """
    resp = requests.post(
        f"{api_base_url}/tasks",
        json=test_task_data,
        headers=auth_headers,
        timeout=10,
    )
    resp.raise_for_status()
    task = resp.json()

    yield task  # ---- test runs here ----

    # Teardown: delete the task we created
    requests.delete(
        f"{api_base_url}/tasks/{task['id']}",
        headers=auth_headers,
        timeout=10,
    )
