# Test Plan: US-001 Task Creation

## 1. Objective
Validate end-to-end behavior for task creation across UI, API, and database layers based on user story US-001 and current implementation.

## 2. References
- User story: docs/user-stories/US-001-task-creation.md
- API route logic: api/routes/tasks.js
- UI form behavior: web-app/src/components/TaskForm.jsx
- Database constraints: db/schema.sql

## 3. In Scope
- Task creation through the web form and direct API calls.
- Validation and error handling for title, description, due date, and priority.
- API response correctness for successful creation (HTTP 201 and response payload fields).
- DB persistence and default values for created tasks.
- Cross-layer consistency between UI validation, API validation, and DB constraints.

## 4. Out of Scope
- Task editing, deletion, filtering, and search behavior.
- Authentication/authorization (user identity is optional for task creation in current route).
- Mobile app flows.
- Performance/load characteristics.
- Styling and non-functional UI details not affecting behavior.

## 5. Test Types Needed

### 5.1 UI Tests (web)
Purpose:
- Validate client-side checks and user feedback.
- Verify API invocation behavior from form submission.
- Verify list update callback path (onCreated) receives created task.

Primary focus:
- Inline validation error behavior.
- Submit/cancel interactions.
- Successful creation and UI reset.

### 5.2 API Tests
Purpose:
- Validate request validation and HTTP contract for POST /tasks.
- Validate negative API scenarios not fully prevented by UI.

Primary focus:
- Status code and response body assertions for valid/invalid payloads.
- Default field behavior in response payload.

### 5.3 DB Tests
Purpose:
- Validate schema constraints and defaults at persistence layer.

Primary focus:
- NOT NULL/CHECK/default behavior tied to task creation fields.
- Timestamp defaults and persistence integrity.

## 6. Acceptance Criteria Coverage (Happy Path + Negative Cases)

### AC1: Title required, non-empty, max 200 characters

Happy path cases:
1. UI-AC1-HP-01: Create task with title length 1.
Expected: submission succeeds, no error shown, task created.
2. UI/API/DB-AC1-HP-02: Create task with title length 200.
Expected: HTTP 201, persisted task title length = 200.

Negative cases:
3. UI-AC1-NG-01: Submit with empty title (blank input).
Expected: inline error "Title is required", API not called.
4. API-AC1-NG-02: POST title = "".
Expected: HTTP 400, error contains title-required message.
5. API/DB-AC1-NG-03: POST title length 201.
Expected: HTTP 400 from API validation.
6. DB-AC1-NG-04: Direct DB insert with title = NULL.
Expected: insert rejected by NOT NULL/CHECK.
7. DB-AC1-NG-05: Direct DB insert with title = ''.
Expected: insert rejected by CHECK length(title) >= 1.

### AC2: Description optional, max 2000 characters

Happy path cases:
1. UI/API/DB-AC2-HP-01: Create with no description.
Expected: creation succeeds, description persisted as NULL.
2. API/DB-AC2-HP-02: Create with description length exactly 2000.
Expected: HTTP 201, value persisted.

Negative cases:
3. API-AC2-NG-01: POST description length 2001.
Expected: HTTP 400 with description length error.
4. DB-AC2-NG-02: Direct DB insert description length 2001.
Expected: insert rejected by CHECK constraint.

### AC3: Due date optional; if present, must be today or future

Happy path cases:
1. UI/API/DB-AC3-HP-01: Create with due_date omitted.
Expected: creation succeeds, due_date = NULL.
2. UI/API-AC3-HP-02: Create with due_date = today.
Expected: HTTP 201 and stored due_date = today.
3. UI/API-AC3-HP-03: Create with due_date in future.
Expected: HTTP 201 and stored due_date matches payload.

Negative cases:
4. API-AC3-NG-01: POST due_date in the past.
Expected: HTTP 400 with due date future/today message.
5. API-AC3-NG-02: POST invalid date string (e.g., 2026-99-99).
Expected: HTTP 400 with invalid date format message.
6. UI-AC3-NG-03: Attempt to submit past due date via form control manipulation.
Expected: inline/API error displayed; task not created.

Note:
- DB has no explicit due_date format CHECK in schema; enforce primarily at API/UI.

### AC4: Priority defaults to medium; must be low/medium/high

Happy path cases:
1. API/DB-AC4-HP-01: POST without priority.
Expected: HTTP 201; response priority = medium; DB persisted medium.
2. UI/API/DB-AC4-HP-02: POST with low, medium, high (parameterized).
Expected: HTTP 201 for each valid value.

Negative cases:
3. API-AC4-NG-01: POST priority = urgent.
Expected: HTTP 400 with allowed-values message.
4. DB-AC4-NG-02: Direct DB insert priority = urgent.
Expected: insert rejected by CHECK constraint.

### AC5: Successful creation appears at top of task list

Happy path cases:
1. UI/API-AC5-HP-01: Create a new task from form; verify list refresh/onCreated path inserts new item first.
Expected: newly created task appears at top.
2. API-AC5-HP-02: Create two tasks sequentially; GET /tasks returns newest first.
Expected: order by created_at DESC respected.

Negative cases:
3. UI-AC5-NG-01: Failed create (validation error) should not alter list.
Expected: no new list item appears.
4. UI-AC5-NG-02: API failure (mock/network failure) should not add optimistic item.
Expected: error shown; list unchanged.

### AC6: Invalid form shows inline error and does not call API

Happy path cases:
1. UI-AC6-HP-01: Invalid title (empty) shows inline error in error-message region.
Expected: visible alert text; no network request fired.
2. UI-AC6-HP-02: Correct invalid field then resubmit valid payload.
Expected: error clears and submit proceeds.

Negative cases:
3. UI-AC6-NG-01: Overlong title (201+) entered/pasted.
Expected: inline error or prevented input leading to validation message; no API call if invalid.
4. UI-AC6-NG-02: Simulated API-side validation failure after UI passes.
Expected: inline error displays API message; form remains for correction.

### AC7: API returns HTTP 201 with created task including id

Happy path cases:
1. API-AC7-HP-01: Valid minimum payload (title only).
Expected: HTTP 201 and JSON contains numeric id and expected defaults.
2. API-AC7-HP-02: Full valid payload.
Expected: HTTP 201 and response echoes persisted fields.

Negative cases:
3. API-AC7-NG-01: Invalid payload (missing/empty title).
Expected: not 201; HTTP 400 with error body.
4. API-AC7-NG-02: Server-side DB fault simulation.
Expected: HTTP 500 with stable error contract.

## 7. Traceability Matrix (AC -> Layers)
- AC1: UI, API, DB
- AC2: UI, API, DB
- AC3: UI, API (DB gap documented)
- AC4: UI, API, DB
- AC5: UI, API
- AC6: UI
- AC7: API, DB

## 8. Test Data Requirements

Core data sets:
1. Titles:
- length 0 (empty)
- length 1
- length 200
- length 201
2. Descriptions:
- null/omitted
- length 2000
- length 2001
3. Due dates:
- null/omitted
- today
- future (today + 7 days)
- past (today - 1 day)
- malformed string
4. Priorities:
- valid: low, medium, high
- invalid: urgent, HIGH, empty string
5. Optional relational data:
- user_id null
- valid existing user_id
- invalid non-existing user_id (for DB/API behavior checks if needed)

Data management:
- Each test creates only required records.
- Use teardown/cleanup to remove created records.
- Avoid shared mutable fixtures that can leak state.

## 9. Environment Dependencies

Required services/components:
1. API service running and reachable through configured base URL.
2. SQLite DB initialized with current schema.sql.
3. Web app running with VITE_API_BASE_URL pointing to API.

Configuration dependencies:
1. Environment variables:
- API_BASE_URL for API tests.
- BASE_URL for web tests.
- VITE_API_BASE_URL for web app runtime.
2. Seed/reset scripts available for deterministic starts.
3. Test frameworks/tooling:
- Playwright (web)
- pytest + requests (API)
- pytest + SQLAlchemy/sqlite access (DB)

Data/time dependencies:
1. System clock/timezone can influence due_date today/past/future tests.
2. Use date generation relative to runtime date to avoid brittle hardcoded values.

## 10. Entry Criteria
1. User story and acceptance criteria are approved and stable enough for implementation.
2. API route for POST /tasks and DB schema are deployed in the test environment.
3. Test environment is configured with required environment variables.
4. DB reset/seed process is successful.
5. No blocking defects in app startup, API startup, or DB initialization.

## 11. Exit Criteria
1. All planned AC-linked happy path tests executed and passing.
2. All planned negative validation tests executed with expected outcomes.
3. No open Severity-1/Severity-2 defects for US-001 behavior.
4. Any known gaps (for example, DB due_date format enforcement) are documented and accepted by stakeholders.
5. Traceability from AC1-AC7 to at least one automated test per criterion is complete.

## 12. Risks and Notes
1. UI maxLength is currently 250 while API limit is 200, so API-side validation path must be covered.
2. DB does not enforce due_date format directly; invalid text can pass DB if inserted outside API.
3. Ordering by created_at DESC can be sensitive when inserts happen within same timestamp granularity; add deterministic tie-breaker checks if flakiness appears.

## 13. Automation Recommendation
1. Prioritize API tests first for fast validation of core contract.
2. Add focused UI tests for inline error handling and list-top insertion behavior.
3. Add DB constraint tests to guard schema regressions independently of API behavior.
4. Maintain one traceability table in test docs mapping AC IDs to automated test IDs.
