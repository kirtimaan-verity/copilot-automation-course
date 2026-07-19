# US-001: Task Creation

**As a** user
**I want to** create a task with a title, description, due date, and priority
**So that** I can track work that needs doing.

## Acceptance Criteria
1. AC1: A task requires a non-empty title (max 200 characters).
2. AC2: Description is optional (max 2000 characters).
3. AC3: Due date is optional; if provided it must be today or in the future.
4. AC4: Priority defaults to "medium" and must be one of low/medium/high.
5. AC5: On successful creation the new task appears at the top of the task list.
6. AC6: Submitting an invalid form shows an inline error message and does not
   call the API.
7. AC7: The API returns HTTP 201 with the created task including its id.
