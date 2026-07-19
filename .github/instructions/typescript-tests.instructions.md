---
applyTo: "tests/web/**,tests/mobile/**"
---

# Copilot Instructions — TypeScript Test Files

These path-specific instructions apply to all web and mobile test files
(`tests/web/`, `tests/mobile/`). Created in Module 5, Lab 18.

## TypeScript Style
- Use strict TypeScript: enable `"strict": true` in tsconfig.json
- Never use `any` type — always define proper interfaces
- Use `const` by default; `let` only when reassignment is necessary

## Playwright-Specific Rules
- Always use `await` — never mix sync and async Playwright APIs
- Use `page.getByTestId()` as the primary locator strategy
- Fall back to `page.getByRole()` for interactive elements without data-testid
- Never use `page.waitForTimeout()` — use `page.waitForSelector()` or `expect(locator).toBeVisible()`
- Set a meaningful test timeout per test with `test.setTimeout(ms)` for slow operations

## Assertions
- Use `expect()` from `@playwright/test` only — never use Jest's expect
- Every assertion must have a failure message: `expect(val, 'msg').toBe(...)`
- Use `toBeVisible()` not `isVisible()` for visibility checks

## Test Organisation
- Use `test.describe()` to group related tests
- Use `test.beforeAll()` only for truly shared, read-only setup
- Use `test.beforeEach()` for per-test navigation and state setup
