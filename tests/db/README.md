# Database Tests (pytest + SQLAlchemy)

**You generate the test files during the labs.** `conftest.py` is provided with
the rollback fixture and `PRAGMA foreign_keys = ON` — you use it as-is.

| Lab | What you create here |
|-----|---------------------|
| Module 4, Lab 17 | `test_schema_constraints.py` (one test per constraint) |

Open `db/schema.sql` before prompting so Copilot sees the CHECK / UNIQUE / FK
constraints. Run: `TEST_DB_URL=sqlite:///./db/app.db pytest tests/db -v`
