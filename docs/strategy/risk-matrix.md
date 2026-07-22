# Risk-Based Test Automation Matrix: Task Manager

Risk score formula:
- Impact values: Critical=3, High=2, Medium=1, Low=0
- Likelihood values: High=3, Medium=2, Low=1
- Risk score = Impact x Likelihood

| Functional Area | Business Impact if Broken | Likelihood of Regression | Risk Score | Current Test Coverage | Recommended Automation Priority | Recommended Test Type | Risk Score Justification | Priority Justification |
|---|---|---|---:|---|---|---|---|---|
| Task Creation | Critical | High | 9 | Partial | P1 | API | Core product action; if creation fails, users cannot capture work. Validation and request-shape changes frequently cause regressions. | Highest business value and break risk; protect continuously with strong API coverage and key UI happy/negative checks. |
| Task Filtering/Search | High | High | 6 | Partial | P1 | UI | Users depend on quickly finding tasks. Combined status/search/debounce interactions are change-prone in UI state logic. | Direct productivity impact and interaction complexity justify early UI automation with API cross-checks. |
| API Error Handling | High | High | 6 | Partial | P1 | API | Invalid payloads, not-found paths, and internal failures are common; wrong error contracts break clients and observability. | Error contract checks are high-signal and low-cost at API layer; they should run on every PR. |
| Database Integrity | Critical | Medium | 6 | Partial | P1 | DB | Constraint/default/FK regressions can silently corrupt data or allow invalid states; impact is severe even if frequency is moderate. | DB checks are release-critical guardrails and should gate schema/API-impacting changes. |
| User Authentication | High | Medium | 4 | None | P1 | API | If authentication fails, access control and user trust are affected. Regression likelihood is moderate given expected auth policy changes. | Security gateway behavior is foundational and should be prioritized as soon as auth is implemented. |
| Task Editing | High | Medium | 4 | None | P1 | API | Edit failures create stale/incorrect records and reduce trust. Shared update/validation paths are moderately regression-prone. | Core CRUD operation; should follow task creation in the first automation wave. |
| Task Deletion | High | Medium | 4 | None | P1 | API | Deletion defects can cause data loss or undeleted stale records. Route and confirmation flows change often enough to regress. | Destructive behavior needs early automation, especially negative and idempotency checks. |
| Task Status Updates | High | Medium | 4 | None | P2 | API | Status drives workflow visibility and reporting; transition/mapping issues can misrepresent progress. | Important but narrower than primary CRUD paths, so prioritize after P1 stabilization. |
| Due Date Handling | Medium | High | 3 | None | P2 | API | Date boundaries and timezone behavior commonly regress, though impact is typically scoped to scheduling quality. | High defect likelihood warrants early coverage, but it sits behind core P1 flow reliability. |
| Priority Management | Medium | Medium | 2 | None | P3 | Unit | Priority enum/UI mapping errors are usually bounded in impact and easier to catch in lower layers. | Lower urgency; cover with focused unit/API checks once higher-risk flows are stable. |
| User Session Management | High | Low | 2 | None | P3 | API | Session issues are high impact when present, but current visible app scope suggests lower short-term regression pressure. | Defer behind core flows unless session complexity expands (expiry, refresh, multi-device). |
