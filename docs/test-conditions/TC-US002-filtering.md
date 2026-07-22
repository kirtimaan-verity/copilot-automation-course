# Test Conditions: US-002 Task Filtering and Search

Source user story: docs/user-stories/US-002-task-filtering.md

## Flat List of Test Conditions

| Condition ID | AC Mapping | Test Type | Polarity | Specific Input | Expected Output |
|---|---|---|---|---|---|
| TC-001 | AC1 | UI behaviour | Positive | Open task list screen with filter control visible. | Status filter options shown exactly: all, active, completed, overdue, archived. |
| TC-002 | AC1 | UI behaviour | Negative | Inspect status filter options list. | No missing option and no extra option outside the required five. |
| TC-003 | AC1 | State management | Positive | Initial page load with no prior selection. | Default selected status is all. |
| TC-004 | AC1 | API contract | Positive | GET /tasks with no status query parameter. | API returns unfiltered task set (subject to any search term, if provided). |
| TC-005 | AC2 | UI behaviour | Positive | Select status = active from filter. | Only tasks with status active are displayed. |
| TC-006 | AC2 | UI behaviour | Positive | Select status = completed from filter. | Only tasks with status completed are displayed. |
| TC-007 | AC2 | UI behaviour | Positive | Select status = overdue from filter. | Only tasks with status overdue are displayed. |
| TC-008 | AC2 | UI behaviour | Positive | Select status = archived from filter. | Only tasks with status archived are displayed. |
| TC-009 | AC2 | API contract | Positive | GET /tasks?status=active (repeat for completed/overdue/archived). | HTTP 200; every returned item has status equal to the requested status. |
| TC-010 | AC2 | API contract | Negative | GET /tasks?status=invalid_status. | API does not return items with valid statuses by mistake; result is empty list or explicit validation error (define contract expectation). |
| TC-011 | AC3 | UI behaviour | Positive | Enter search term matching part of a title, for example term = report. | List shows tasks where title contains report. |
| TC-012 | AC3 | UI behaviour | Positive | Enter search term matching only description, for example term = invoice. | List shows tasks where description contains invoice even if title does not. |
| TC-013 | AC3 | API contract | Positive | GET /tasks?search=report. | HTTP 200; results include tasks where title OR description contains report. |
| TC-014 | AC3 | UI behaviour | Negative | Enter search term with no matches, for example zzzz-no-hit. | Empty-state message is shown; no task cards displayed. |
| TC-015 | AC4 | UI behaviour | Positive | Search using lowercase term for uppercase stored text, for example search alpha against title ALPHA. | Matching task is returned or displayed (case-insensitive behavior). |
| TC-016 | AC4 | API contract | Positive | GET /tasks?search=ALPHA when stored text is alpha. | HTTP 200; matching task returned despite case difference. |
| TC-017 | AC4 | UI behaviour | Negative | Compare search results for task vs TASK over same dataset. | Result sets are identical; if different, case-insensitive requirement fails. |
| TC-018 | AC5 | Performance | Positive | Type alpha rapidly in search box (5 keystrokes within less than 300ms gaps), then stop. | A single fetch is triggered after about 300ms idle; list updates once for final term. |
| TC-019 | AC5 | Performance | Negative | Type slowly with pauses greater than 300ms between characters. | Multiple updates or fetches occur per pause; each reflects the latest partial term. |
| TC-020 | AC5 | State management | Negative | Trigger overlapping requests by typing quickly then deleting quickly. | Final displayed list corresponds to latest input value, not an earlier stale response. |
| TC-021 | AC6 | UI behaviour | Positive | Paste or enter 101+ characters into search box. | Input value is limited to 100 characters in the UI. |
| TC-022 | AC6 | UI behaviour | Negative | Attempt to exceed 100 chars via continuous typing and paste. | Characters beyond position 100 are not retained; no crash or UI corruption. |
| TC-023 | AC7 | State management | Positive | With filter = all, type a term, then clear search to empty. | Full unfiltered list is restored. |
| TC-024 | AC7 | State management | Positive | With filter = completed and search term present, clear search to empty. | List restores to completed-filtered set (search cleared, filter preserved). |
| TC-025 | AC8 | UI behaviour | Positive | Set filter = active, search = report. | Displayed tasks satisfy both constraints: status active and text contains report. |
| TC-026 | AC8 | API contract | Positive | GET /tasks?status=active&search=report. | HTTP 200; each item matches both status filter and search term condition. |
| TC-027 | AC8 | UI behaviour | Negative | Use filter and search combination with no intersection, for example status=archived, search=brand-new-term. | Empty-state message shown; no task cards displayed. |
| TC-028 | AC8 | State management | Positive | Apply search first, then change status filter (and vice versa). | Both controls remain active; list recomputes intersection each time without clearing the other control. |

## Notes
- Type totals overlap because some acceptance criteria are intentionally validated in both UI and API layers.
- Timing-sensitive conditions in AC5 should use controlled request interception to reduce flakiness.
