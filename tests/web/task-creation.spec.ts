import { expect, test } from '@playwright/test';
import TaskFormPage from './pages/TaskFormPage';
import TaskListPage from './pages/TaskListPage';

const getIsoDateOffset = (offsetDays: number): string => {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  return date.toISOString().split('T')[0];
};

test.describe('Task creation user journey', () => {
  let taskFormPage: TaskFormPage;
  let taskListPage: TaskListPage;

  const waitForNextSecondBoundary = async (): Promise<void> => {
    const currentSecond = new Date().getSeconds();
    await taskListPage.page.waitForFunction(
      (second) => new Date().getSeconds() !== second,
      currentSecond
    );
  };

  const createTaskViaForm = async (title: string, options?: { description?: string; dueDate?: string; priority?: 'Low' | 'Medium' | 'High' }): Promise<void> => {
    await taskListPage.clickNewTaskButton();
    await expect(taskFormPage.form, 'Task form should open after clicking the new task button').toBeVisible();

    await taskFormPage.fillTitle(title);
    if (options?.description) {
      await taskFormPage.fillDescription(options.description);
    }
    if (options?.dueDate) {
      await taskFormPage.setDueDate(options.dueDate);
    }
    if (options?.priority) {
      await taskFormPage.setPriority(options.priority);
    }
    await taskFormPage.submit();

    await expect(taskFormPage.form, 'Task form should close after successful task creation').toBeHidden();
    await taskListPage.waitForTaskToAppear(title);
  };

  test.beforeEach(async ({ page }) => {
    taskFormPage = new TaskFormPage(page);
    taskListPage = new TaskListPage(page);

    await taskListPage.navigateTo();
    await expect(taskListPage.newTaskButton, 'New task button should be visible on the task list page').toBeVisible();
  });

  test('creates a task successfully when all fields are filled', async () => {
    test.setTimeout(30_000);

    const title = `E2E full task ${Date.now()}`;
    const description = 'Created by Playwright test with all available fields';
    const dueDate = getIsoDateOffset(2);

    await createTaskViaForm(title, { description, dueDate, priority: 'High' });
    await expect(taskListPage.getTaskByTitle(title), 'Created task should be visible in the task list').toBeVisible();
  });

  test('creates a task with only the required field (title)', async () => {
    test.setTimeout(30_000);

    const title = `E2E title-only task ${Date.now()}`;

    await createTaskViaForm(title);
    await taskListPage.searchFor(title);
    await expect(taskListPage.getTaskByTitle(title), 'Title-only task should appear in the filtered task list').toBeVisible();
    await expect(taskListPage.getTaskByTitle(title), 'Filtered task list should contain exactly one created title-only task').toHaveCount(1);
  });

  test('shows a validation error when title is empty', async () => {
    test.setTimeout(30_000);

    await taskListPage.clickNewTaskButton();
    await expect(taskFormPage.form, 'Task form should be visible before triggering title validation').toBeVisible();

    await taskFormPage.submit();

    await expect(taskFormPage.errorMessage, 'Validation error should be displayed when title is empty').toBeVisible();
    const errorMessage = await taskFormPage.getErrorMessage();
    expect(errorMessage, 'Empty title should show the required-title validation message').toBe('Title is required');
  });

  test('shows a validation error when due date is in the past', async () => {
    test.setTimeout(30_000);

    const title = `E2E past-due task ${Date.now()}`;
    const pastDueDate = getIsoDateOffset(-1);

    await taskListPage.clickNewTaskButton();
    await expect(taskFormPage.form, 'Task form should be visible before submitting an invalid past due date').toBeVisible();

    await taskFormPage.fillTitle(title);
    await taskFormPage.setDueDate(pastDueDate);
    await taskFormPage.submit();

    await expect(taskFormPage.errorMessage, 'Validation error should be shown when due date is in the past').toBeVisible();
    const errorMessage = await taskFormPage.getErrorMessage();
    expect(
      errorMessage,
      'Past due date should return a future-or-today validation message'
    ).toContain('Due date must be today or in the future');
  });

  test('shows the newly created task at the top of the task list', async () => {
    test.setTimeout(30_000);

    const runId = Date.now();
    const titlePrefix = `E2E top-of-list ${runId}`;
    const olderTitle = `${titlePrefix} older task`;
    const newerTitle = `${titlePrefix} newer task`;

    await createTaskViaForm(olderTitle);
    await waitForNextSecondBoundary();
    await createTaskViaForm(newerTitle);

    await taskListPage.searchFor(titlePrefix);
    await expect(taskListPage.getTaskByTitle(olderTitle), 'Filtered list should include the older task used for ordering validation').toHaveCount(1);
    await expect(taskListPage.getTaskByTitle(newerTitle), 'Filtered list should include the newer task used for ordering validation').toHaveCount(1);

    const firstTaskTitle = (await taskListPage.taskTitleItems.first().textContent())?.trim() ?? '';
    expect(firstTaskTitle, 'Most recently created task should appear as the first item in the task list').toBe(newerTitle);
  });

  test('closes the form without creating a task when cancel is clicked', async () => {
    test.setTimeout(30_000);

    const title = `E2E cancelled task ${Date.now()}`;

    await taskListPage.clickNewTaskButton();
    await expect(taskFormPage.form, 'Task form should open before canceling task creation').toBeVisible();

    await taskFormPage.fillTitle(title);
    await taskFormPage.cancel();

    await expect(taskFormPage.form, 'Task form should close when cancel is clicked').toBeHidden();
    await taskListPage.searchFor(title);
    expect(
      await taskListPage.getTaskByTitle(title).count(),
      'Canceled task title should not be present in the task list'
    ).toBe(0);
  });
});