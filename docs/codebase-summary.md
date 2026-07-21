# Codebase Summary for Test Engineers

This repository is a task-management course starter built to practice automation across a full stack. It contains a React web app, a Node/Express API, and a SQLite database, plus empty test scaffolding for API, DB, web, mobile, end-to-end, and performance work. The codebase is intentionally small, but it includes real contract boundaries and failure modes that are useful for building a practical test strategy.

## Application Purpose

The product is a task manager where users can view tasks, search and filter them, create new tasks, and delete existing ones. The application is also a training environment for Copilot-assisted test generation, so the repo is organized around the exercises a new automation engineer would complete across UI, API, and database layers.

## Technology Stack

- Frontend: React 19, Vite, Playwright
- API: Node.js, Express 5, better-sqlite3, CORS
- Database: SQLite with schema constraints, indexes, and triggers
- Tests: pytest, requests, SQLAlchemy, Playwright, pytest-playwright, pytest-cov
- Tooling: npm workspaces, Node 22+, Python 3.11+

## Key Components

- [web-app/src/App.jsx](../web-app/src/App.jsx): Root UI component that loads tasks, applies search and status filtering, and switches between the list and the form.
- [web-app/src/components/TaskForm.jsx](../web-app/src/components/TaskForm.jsx): Task creation form with client-side validation and API submission.
- [web-app/src/components/TaskList.jsx](../web-app/src/components/TaskList.jsx): Task list, search box, status filter, and delete actions.
- [api/server.js](../api/server.js): Express entrypoint with health check, task routes, and central error handling.
- [api/routes/tasks.js](../api/routes/tasks.js): Main business logic for task CRUD, filtering, and validation.
- [db/schema.sql](../db/schema.sql): Source of truth for database constraints, defaults, indexes, and the updated_at trigger.
- [db/seed.js](../db/seed.js): Seeds deterministic demo users and tasks for local development and testing.

## Main User Flows

1. Open the app and load the current task list from the API.
2. Filter tasks by status or search text.
3. Create a task from the form and return to the list.
4. Delete a task from the list.
5. Exercise the same flows through the API and database layers to verify that UI behavior matches backend rules.

## Top 5 Test Automation Priorities

1. API CRUD and validation: [api/routes/tasks.js](../api/routes/tasks.js). This is the highest-risk layer because it enforces task rules, returns response codes, and persists data.
2. Database constraints: [db/schema.sql](../db/schema.sql). Validate NOT NULL, UNIQUE, CHECK, foreign key cascade, defaults, indexes, and the updated_at trigger.
3. Web app task creation and list interactions: [web-app/src/App.jsx](../web-app/src/App.jsx), [web-app/src/components/TaskForm.jsx](../web-app/src/components/TaskForm.jsx), and [web-app/src/components/TaskList.jsx](../web-app/src/components/TaskList.jsx).
4. Cross-layer end-to-end coverage: confirm the UI, API, and database agree on payload shape, validation, and visible results.
5. Shared test fixtures and environment setup: [tests/api/conftest.py](../tests/api/conftest.py) and [tests/db/conftest.py](../tests/db/conftest.py). If these are wrong, large parts of the suite can give false results.

## What Is Most Likely To Break

The most regression-prone boundary is the task contract shared by the API, database schema, seed data, and web form. Changes to task fields, allowed status or priority values, due-date rules, or default values should be tested across all layers, because a mismatch there will fail in user-visible ways and can also invalidate lower-level tests.