# API Tests (pytest + requests)

**You generate the test files during the labs.** `conftest.py` is provided as
a starting point — you extend it.

| Lab | What you create / extend here |
|-----|------------------------------|
| Module 4, Lab 16 | `test_task_creation.py`, `test_task_operations.py`; extend `conftest.py` |
| Module 7, Lab 28 | `test_task_edge_cases.py` (coverage gaps) |
| Module 9, Lab 36 | `test_security.py` (OWASP) |

Open `api/openapi.yaml` before prompting so Copilot generates against the real
API contract. Run: `API_BASE_URL=http://localhost:3001 pytest tests/api -v`
