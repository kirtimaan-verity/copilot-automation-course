"""Cross-layer E2E test for task creation via UI -> API -> DB."""

from __future__ import annotations

import os
from datetime import UTC, date, datetime, timedelta
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import pytest
import requests
from faker import Faker
from playwright.sync_api import APIRequestContext, Page, Playwright, Response
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

@pytest.fixture(scope="function")
def web_base_url() -> str:
    """Return web app URL from environment with local fallback."""
    return os.environ.get("BASE_URL", "http://localhost:3000")


@pytest.fixture(scope="function")
def e2e_task_payload() -> Dict[str, str]:
    """Return unique and valid task data for UI submission."""
    faker = Faker()
    due_date = (date.today() + timedelta(days=7)).isoformat()
    return {
        "title": f"E2E task {faker.uuid4()}",
        "description": faker.sentence(nb_words=8),
        "due_date": due_date,
        "priority": "high",
    }


def _is_post_tasks_response(response: Response, api_base_url: str) -> bool:
    """Return True when response matches the POST /tasks API call."""
    request = response.request
    if request.method != "POST":
        return False

    expected_path = "/tasks"
    request_url = urlparse(response.url)
    api_url = urlparse(api_base_url)
    return request_url.path == expected_path and request_url.netloc == api_url.netloc


def _parse_created_at(value: Any) -> datetime:
    """Convert SQLite created_at text/datetime into a datetime instance."""
    parsed: datetime
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    else:
        raise TypeError(f"Unsupported created_at type: {type(value)}")

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _fetch_task_row(engine: Engine, task_id: int) -> Optional[Dict[str, Any]]:
    """Fetch task row by id using a fresh DB connection."""
    with engine.connect() as connection:
        row = connection.execute(
            text(
                """
                SELECT id, title, priority, created_at
                FROM tasks
                WHERE id = :task_id
                """
            ),
            {"task_id": task_id},
        ).mappings().first()

    return dict(row) if row is not None else None


def _resolve_engine(db_session: Session) -> Engine:
    """Return SQLAlchemy engine regardless of Session bind type."""
    bind = db_session.get_bind()
    if isinstance(bind, Engine):
        return bind
    if isinstance(bind, Connection):
        return bind.engine
    raise TypeError(f"Unsupported SQLAlchemy bind type: {type(bind)}")


def test_create_task_via_ui_when_submitted_validates_api_and_db(
    page: Page,
    playwright: Playwright,
    api_base_url: str,
    db_session: Session,
    web_base_url: str,
    e2e_task_payload: Dict[str, str],
) -> None:
    """Validate task creation across UI action, API response, and DB persistence, then cleanup."""
    api_context: APIRequestContext = playwright.request.new_context(base_url=api_base_url)
    created_task_id: Optional[int] = None
    engine = _resolve_engine(db_session)

    try:
        page.goto(web_base_url)
        page.get_by_test_id("new-task-btn").wait_for(state="visible", timeout=10_000)
        page.get_by_test_id("new-task-btn").click()

        page.get_by_test_id("task-form").wait_for(state="visible", timeout=10_000)
        page.get_by_test_id("task-title").fill(e2e_task_payload["title"])
        page.get_by_test_id("task-description").fill(e2e_task_payload["description"])
        page.get_by_test_id("task-due-date").fill(e2e_task_payload["due_date"])
        page.get_by_test_id("task-priority").select_option(e2e_task_payload["priority"])

        with page.expect_response(
            lambda response: _is_post_tasks_response(response, api_base_url),
            timeout=10_000,
        ) as post_response_info:
            page.get_by_test_id("submit-btn").click()

        post_response = post_response_info.value
        assert post_response.status == 201, f"Expected POST /tasks to return 201, got {post_response.status}"
        response_body = post_response.json()
        created_task_id = response_body.get("id")

        assert isinstance(created_task_id, int), f"Expected created task id to be int, got {type(created_task_id)}"
        assert response_body["title"] == e2e_task_payload["title"], (
            f"Expected API title '{e2e_task_payload['title']}', got '{response_body['title']}'"
        )
        assert response_body["priority"] == e2e_task_payload["priority"], (
            f"Expected API priority '{e2e_task_payload['priority']}', got '{response_body['priority']}'"
        )

        api_get_response = api_context.get(f"/tasks/{created_task_id}")
        assert api_get_response.status == 200, f"Expected GET /tasks/{created_task_id} to return 200"
        api_get_body = api_get_response.json()
        assert api_get_body["title"] == e2e_task_payload["title"], (
            f"Expected API GET title '{e2e_task_payload['title']}', got '{api_get_body['title']}'"
        )

        page.get_by_test_id("task-form").wait_for(state="hidden", timeout=10_000)
        page.get_by_test_id("task-card-title").filter(has_text=e2e_task_payload["title"]).first.wait_for(
            state="visible",
            timeout=10_000,
        )

        db_row = _fetch_task_row(engine, created_task_id)
        assert db_row is not None, f"Expected task id {created_task_id} to exist in DB"
        assert db_row["title"] == e2e_task_payload["title"], (
            f"Expected DB title '{e2e_task_payload['title']}', got '{db_row['title']}'"
        )
        assert db_row["priority"] == e2e_task_payload["priority"], (
            f"Expected DB priority '{e2e_task_payload['priority']}', got '{db_row['priority']}'"
        )

        created_at = _parse_created_at(db_row["created_at"])
        age_seconds = (datetime.now(UTC) - created_at).total_seconds()
        assert age_seconds <= 60, f"Expected created_at within 60 seconds, got {age_seconds:.2f} seconds"
        assert age_seconds >= -5, f"Expected created_at not to be in the future, got age {age_seconds:.2f} seconds"
    finally:
        if created_task_id is not None:
            delete_response = requests.delete(f"{api_base_url}/tasks/{created_task_id}", timeout=10)
            assert delete_response.status_code in (204, 404), (
                f"Expected cleanup delete to return 204 or 404, got {delete_response.status_code}"
            )

            db_row_after_delete = _fetch_task_row(engine, created_task_id)
            assert db_row_after_delete is None, f"Expected task id {created_task_id} to be removed from DB after cleanup"

        api_context.dispose()
