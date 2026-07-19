# GitHub Copilot Instructions — Task Manager Automation

These rules are auto-injected into every Copilot request in this repository.
They are built up across Module 2 (Lab 03, 06) and Module 5 (Lab 18).

## Project Context
This is the course project for "GitHub Copilot for Automation Engineers".
It is a task-management app with a React frontend (`web-app/`), a Node/Express
API (`api/`), and a SQLite database (`db/`). Tests cover web (Playwright),
mobile (Appium), API (pytest), and database (SQLAlchemy) layers.

## Test Frameworks
- Web UI tests: Playwright + TypeScript (`tests/web/`)
- Mobile tests: Appium 2.x + WebdriverIO (`tests/mobile/`)
- API tests: pytest + requests (`tests/api/`)
- Database tests: pytest + SQLAlchemy 2.0 (`tests/db/`)
- Performance tests: k6 (`tests/performance/`)

## File Naming
- Python test files: `test_<feature>.py`
- TypeScript test files: `<feature>.spec.ts`
- Python test functions: `test_<action>_<condition>_<expected_result>`
- Page Objects: `<Name>Page.ts` in `tests/web/pages/`

## Locator Strategy (Web)
- Always use `getByTestId()` for locators — the components expose `data-testid`
- Never use CSS class selectors or XPath
- Wrap all locators in Page Object classes; tests never call `page.locator()` directly

## Quality Rules
- Every `expect()` and every `assert` must have a descriptive message
- Every test function must have a docstring stating what it validates
- API tests must assert BOTH `status_code` AND the response body
- No hardcoded URLs — read from environment (`API_BASE_URL`, `BASE_URL`)
- Tests must be independent: create the data they need, delete it in teardown

## Environment
- API base URL: `os.environ["API_BASE_URL"]` (Python) / `process.env.BASE_URL` (TS)
- Never hardcode `localhost` — always use the environment variable with a fallback

## CI/CD Rules
- All test jobs must have `timeout-minutes` set
- Artifact uploads must use `if: always()`
- Tests must be idempotent and runnable in any order

## Never Generate
- Never use `waitForTimeout()` — use `waitForResponse()` or `expect().toBeVisible()`
- Never use a bare `assert` without a message
- Never hardcode credentials, tokens, or API keys
- Never use `/tests` to generate Playwright E2E or full API suites
