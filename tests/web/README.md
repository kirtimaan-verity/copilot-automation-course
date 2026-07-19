# Web UI Tests (Playwright + TypeScript)

**You generate these files during the labs.** This directory starts empty.

| Lab | What you create here |
|-----|---------------------|
| Module 4, Lab 14 | `pages/TaskFormPage.ts`, `pages/TaskListPage.ts`, `task-creation.spec.ts` |
| Module 7, Lab 29 | `flaky-example.spec.ts` (then fix it) |
| Module 8, Lab 32 | `visual-regression.spec.ts` + baselines in `__snapshots__/` |

Before generating, open `web-app/src/components/TaskForm.jsx` so Copilot can
read the `data-testid` locators. Follow `.github/copilot-instructions.md`
(Page Object Model, `getByTestId`, no `waitForTimeout`).

Config lives in `web-app/playwright.config.ts` (already set up).
