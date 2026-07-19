# Prompt: Multi-Layer Automation Strategy
# When to use: starting a new project or a major feature
# Open first: user stories, main source files, existing coverage reports

---

Produce a multi-layer test automation strategy for:
  Application: [NAME / DESCRIBE]
  Current test coverage: [DESCRIBE OR "none"]

Cover all five testing layers:
  1. Unit tests
  2. API / integration tests
  3. Web UI E2E (Playwright)
  4. Mobile E2E (Appium)
  5. Database (constraint) tests

For EACH layer provide:
- Recommended framework + one-line justification
- Specific, measurable coverage target (a number, not "comprehensive")
- Execution frequency (every commit / every PR / nightly / release)
- Ownership (developer / QA / shared)

Also include:
- A "what NOT to automate" section with reasons
- An ASCII testing-pyramid diagram showing the target ratio

Keep it under 2 pages.
