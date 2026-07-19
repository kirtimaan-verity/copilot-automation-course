# US-002: Task Filtering and Search

**As a** user
**I want to** filter tasks by status and search by keyword
**So that** I can find the tasks I care about quickly.

## Acceptance Criteria
1. AC1: A status filter offers: all, active, completed, overdue, archived.
2. AC2: Selecting a status shows only tasks with that status.
3. AC3: A search box filters tasks whose title or description contains the term.
4. AC4: Search is case-insensitive.
5. AC5: Search updates the list as the user types (debounced ~300ms).
6. AC6: Search terms are limited to 100 characters.
7. AC7: Clearing the search restores the full (filtered) list.
8. AC8: Combining a status filter and a search term applies both.
