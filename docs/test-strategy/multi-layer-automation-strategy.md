# Multi-Layer Automation Strategy: Task Manager

Application: Task Manager (React web app, Express API, SQLite DB)  
Current test coverage: no consolidated coverage report available yet (coverage flow not run).

## 1. Five-Layer Strategy

| Layer | Framework and Version | Why this stack | Coverage Target (measurable) | Execution Frequency | Ownership | Estimated Effort |
|---|---|---|---|---|---|---|
| Unit tests | Vitest 4.x + React Testing Library 16.x (to add) | Fast feedback for UI logic and component behavior before E2E | 80% statement and 70% branch coverage for web-app/src/components and extracted client logic; 90% on shared validation helpers | Every commit local, every PR in CI | Developer-owned, QA reviews gaps | 5-7 engineer-days |
| API and integration | pytest 9.1.1 + requests 2.34.2 | Stable black-box API contract and negative validation testing | 95% endpoint coverage for tasks routes, 100% AC-linked scenarios for create/filter/search, 100% expected validation/error-path assertions for in-scope 400/404/500 | Every PR; full suite nightly | Shared (Dev + QA) | 4-6 engineer-days |
| Web UI E2E | Playwright 1.61.1 | Best fit with existing data-testid strategy and debounce/network assertions | 100% acceptance criteria coverage for US-001 and US-002; 10 critical smoke journeys; <2% flaky rate over 14-day rolling window | Smoke every PR; full E2E nightly; release gate | QA-owned with Dev support | 4-6 engineer-days |
| Mobile E2E | Appium 2.x + WebdriverIO 9.x (recommended to pin) | Cross-device confidence for business-critical journeys | 70% critical mobile journey coverage (create/filter/search/delete) with at least 20 stable Android baseline scenarios | Nightly and release candidate; PR only for mobile-impacting changes | QA-owned | 5-7 engineer-days |
| DB constraint tests | pytest 9.1.1 + SQLAlchemy 2.0.51 | Direct schema regression safety independent of API behavior | 100% coverage of schema constraints, defaults, foreign keys, and trigger behavior for tasks/users; one test per constraint | Every PR touching schema/API; nightly full DB pack | Shared (QA authorship, Dev review) | 3-4 engineer-days |

## 2. Toolchain Baseline and Version Policy

Current pinned/known:
- Playwright 1.61.1
- pytest 9.1.1
- requests 2.34.2
- SQLAlchemy 2.0.51
- Node runtime >=22

Recommended additions/pinning:
- Vitest 4.x and React Testing Library 16.x for unit layer.
- Appium 2.x and WebdriverIO 9.x pinned in mobile configuration.
- CI coverage publication with pytest-cov and c8 into a single merged report artifact.

## 3. CI Cadence and Quality Gates

PR gate (fast path, target <10 minutes):
1. Unit tests for changed areas.
2. API smoke and contract checks.
3. DB constraint smoke.
4. Web Playwright smoke.

Nightly gate:
1. Full API suite.
2. Full DB suite.
3. Full web E2E suite.
4. Mobile core journey pack.
5. Coverage trend and flaky-test report artifacts.

Release gate:
1. No critical failures across all five layers.
2. Flaky tests fixed or quarantined; none allowed in release-critical pack.
3. Coverage targets met or an approved exception recorded.

## 4. What Not to Automate

1. Pixel-perfect UI checks for all pages on every commit.
Reason: high maintenance and low functional signal.

2. Volatile copy-only assertions unless contract-critical.
Reason: noisy failures from wording updates.

3. One-off exploratory checks as permanent scripted tests.
Reason: low ROI versus session-based exploratory testing.

4. Full mobile regression on every PR.
Reason: runtime and infrastructure cost; run nightly and on release candidates.

5. Redundant duplicate assertions across all layers by default.
Reason: slower pipelines without proportional risk reduction.

## 5. Target Test Pyramid Ratio

```text
                [ Mobile E2E ]                3%
             [ Web UI E2E ]                   7%
        [ DB Constraint Tests ]              10%
      [ API and Integration Tests ]          25%
   [ Unit Tests ]                            55%
```

## 6. Effort and Rollout Plan

Estimated total initial rollout: 21-30 engineer-days (approximately 4-6 weeks with one QA and one developer sharing work).

Suggested sequence:
1. Weeks 1-2: API and DB baseline.
2. Weeks 2-3: Web E2E core journeys (US-001 and US-002, including debounce behavior).
3. Weeks 3-4: Unit layer introduction for components and shared logic.
4. Weeks 4-6: Mobile core journeys, CI stabilization, and flake management.

## 7. Two-Person Team Realism (2-Week Sprints)

Phased targets are realistic; full-depth all-layer targets at once are not.

Sprint 1-2 realistic scope:
1. API: 80-85% endpoint and validation-path coverage.
2. DB: 90-100% constraints for tasks schema.
3. Web E2E: 6-10 critical smoke scenarios.
4. Mobile: 0-5 sanity scenarios.
5. Unit: framework setup and 10-20 high-value tests.

Sprint 3-4 realistic scope:
1. API: 90%+ for in-scope routes.
2. DB: maintain 100% constraint checks.
3. Web E2E: full US-001 and US-002 acceptance coverage.
4. Mobile: 10-15 stable scenarios.
5. Unit: 60-70% targeted coverage on key components/utilities.

Capacity guideline per sprint:
1. 60-70% new automation.
2. 20-30% maintenance and flake reduction.
3. 10% framework and CI improvements.
