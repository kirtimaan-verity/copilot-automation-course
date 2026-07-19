# Known Issues

Documented Copilot and test limitations for this project. The MCP
`list_open_issues` tool reads this file.

- **ISSUE-001**: The login smoke test can be flaky on slow networks if
  `waitForTimeout` is used. Fix: use `waitForResponse` (see Module 7 Lab 29).
- **ISSUE-002**: SQLite does not enforce foreign keys on any OS unless
  `PRAGMA foreign_keys = ON` is set per connection — the `db_session`
  fixture in `tests/db/conftest.py` handles this (Module 4 Lab 17). Note:
  in SQLAlchemy 2.0 the pragma must be executed *before* `begin()` (with a
  `rollback()` in between to end the autobegun transaction).
- **ISSUE-003**: `/tests` does not generate Playwright E2E tests — it produces
  unit tests for the active file only. Use Copilot Chat instead (Module 4).
