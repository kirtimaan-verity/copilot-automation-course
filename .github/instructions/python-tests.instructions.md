---
applyTo: "tests/api/**,tests/db/**,tests/e2e/**,tests/fixtures/**"
---

# Copilot Instructions — Python Test Files

These path-specific instructions apply to all Python test files
(`tests/api/`, `tests/db/`, `tests/e2e/`, `tests/fixtures/`).
Created in Module 5, Lab 18.

## Python Style
- Follow PEP 8 for all Python code
- Maximum line length: 120 characters
- Use type hints on all function signatures
- Use f-strings for string formatting, never % or .format()

## pytest-Specific Rules
- Use `pytest.raises(ExceptionType)` for exception testing, not try/except
- Always use `pytest.mark.parametrize` when testing the same logic with multiple inputs
- Fixture scope: use `function` scope by default; `session` only for expensive setup (DB connections)
- Test function names must describe the expected behaviour: `test_<action>_<condition>_<expected_result>`

## requests Library Rules
- Never use `verify=False` in requests calls — handle SSL properly
- Always set a timeout: `requests.get(url, timeout=10)`
- Use `response.raise_for_status()` in test helpers, not in test assertions

## Data Handling
- Never hardcode test data inline in test functions — use fixtures or parametrize
- Sensitive data (passwords, tokens) must come from environment variables
- Use the Faker library for generating realistic test data
