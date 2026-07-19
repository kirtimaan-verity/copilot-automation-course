# Prompt: Generate Automation Tests
# When to use: before writing a new test file for a feature
# Open first: the source component/route + the API route + any existing related test files

---

Generate tests for:
  Feature: [DESCRIBE THE FEATURE]
  Test type: [web UI / API / database]
  Framework: [Playwright+TypeScript / pytest+requests / pytest+SQLAlchemy]

Requirements:
- Follow all rules in .github/copilot-instructions.md
- Include: 1 happy path, 2 edge cases, 2 negative scenarios
- Use Page Object Model for web UI tests (locators via getByTestId)
- All URLs from environment variables (API_BASE_URL / BASE_URL)
- An assertion message on every expect()/assert
- Setup/teardown: create data in setup, delete it in teardown
- API tests must assert BOTH status code AND response body

Existing test files for reference:
  [LIST RELATED TEST FILES, e.g. tests/api/test_task_creation.py]

Do NOT generate placeholder or TODO code. Every test must be runnable.
