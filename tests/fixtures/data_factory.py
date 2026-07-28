"""Data factories for test payload generation.

Privacy constraints for generated data:
- Do not generate sensitive identifiers (SSN, passport, or financial account data).
- Emails must use only @example.com or @test.invalid domains.
- Passwords are always stored as SHA-256 hashes, never plaintext.
"""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from typing import Any

from faker import Faker


class TaskFactory:
    """Factory helpers for task payloads used in API and E2E tests."""

    _faker = Faker()
    _priorities = ("low", "medium", "high")

    @classmethod
    def valid_task(cls) -> dict[str, Any]:
        """Return a complete, valid task payload."""
        return {
            "title": cls._faker.sentence(nb_words=4).rstrip("."),
            "description": cls._faker.text(max_nb_chars=120),
            "due_date": (date.today() + timedelta(days=7)).isoformat(),
            "priority": cls._faker.random_element(cls._priorities),
        }

    @classmethod
    def minimal_task(cls) -> dict[str, Any]:
        """Return a minimal valid task payload with only required fields."""
        return {
            "title": cls._faker.sentence(nb_words=3).rstrip("."),
        }

    @classmethod
    def task_with_long_title(cls, length: int = 200) -> dict[str, Any]:
        """Return a task with a title that is exactly the requested length."""
        return {
            "title": "x" * length,
            "description": cls._faker.text(max_nb_chars=80),
            "due_date": (date.today() + timedelta(days=5)).isoformat(),
            "priority": "medium",
        }

    @classmethod
    def overdue_task(cls) -> dict[str, Any]:
        """Return a task that is explicitly overdue."""
        return {
            "title": cls._faker.sentence(nb_words=4).rstrip("."),
            "description": "Backdated task for overdue-state validation",
            "due_date": (date.today() - timedelta(days=30)).isoformat(),
            "priority": "high",
            "status": "overdue",
        }

    @classmethod
    def invalid_tasks(cls) -> list[dict[str, Any]]:
        """Return intentionally invalid payloads for negative validation tests."""
        return [
            {
                "description": "Missing required title",
                "due_date": (date.today() + timedelta(days=2)).isoformat(),
                "priority": "medium",
            },
            {
                "title": "Task with past due date",
                "due_date": (date.today() - timedelta(days=1)).isoformat(),
                "priority": "low",
            },
            {
                "title": "Task with invalid priority",
                "due_date": (date.today() + timedelta(days=3)).isoformat(),
                "priority": "urgent",
            },
            {
                "title": "x" * 201,
                "due_date": (date.today() + timedelta(days=3)).isoformat(),
                "priority": "medium",
            },
            {
                "title": "Task with invalid due date format",
                "due_date": "31-12-2026",
                "priority": "high",
            },
        ]

    @classmethod
    def bulk_tasks(cls, count: int = 50) -> list[dict[str, Any]]:
        """Return a list of unique valid task payloads."""
        tasks: list[dict[str, Any]] = []
        for index in range(count):
            task = cls.valid_task()
            task["title"] = f"{task['title']} #{index + 1}"
            tasks.append(task)
        return tasks


class UserFactory:
    """Factory helpers for user test payloads with privacy-safe defaults."""

    _faker = Faker()
    _allowed_domains = ("example.com", "test.invalid")

    @classmethod
    def valid_user(cls) -> dict[str, str]:
        """Return a realistic user object with a hashed password."""
        local_part = cls._faker.user_name()
        domain = cls._faker.random_element(cls._allowed_domains)
        email = f"{local_part}@{domain}"

        raw_password = cls._faker.password(length=14, special_chars=True, digits=True, upper_case=True, lower_case=True)
        hashed_password = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()

        return {
            "email": email,
            "password": hashed_password,
        }

    @classmethod
    def pii_masked_user(cls) -> dict[str, str]:
        """Return a user object where email local-part is masked."""
        user = cls.valid_user()
        local_part, domain = user["email"].split("@", maxsplit=1)
        masked_local = f"{local_part[0]}***" if local_part else "u***"
        user["email"] = f"{masked_local}@{domain}"
        return user
