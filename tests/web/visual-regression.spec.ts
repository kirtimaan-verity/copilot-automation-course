import * as fs from 'node:fs';
import { type Page, type TestInfo, expect, test } from '@playwright/test';

const mockTasks = [
  {
    id: 1,
    title: 'Visual baseline task',
    description: 'Seeded for screenshot stability',
    due_date: '2026-12-31',
    priority: 'high',
    status: 'active',
  },
];

test.describe('Visual regression for tasks UI', () => {
  const skipIfSnapshotMissing = (testInfo: TestInfo, snapshotName: string): void => {
    const baselinePath = testInfo.snapshotPath(snapshotName);
    test.skip(
      !fs.existsSync(baselinePath),
      `Visual baseline is missing for ${testInfo.project.name} on ${process.platform}: ${baselinePath}`
    );
  };

  const goToTasksDashboard = async (page: Page): Promise<void> => {
    await page.goto('/');
  };

  test.beforeEach(async ({ page }) => {
    await page.route('**/tasks**', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockTasks),
        });
        return;
      }

      await route.continue();
    });
  });

  test('matches full-page tasks dashboard baseline', async ({ page }, testInfo) => {
    test.setTimeout(30_000);
    skipIfSnapshotMissing(testInfo, 'tasks-dashboard-full-page.png');
    await goToTasksDashboard(page);
    await expect(page.getByTestId('task-list'), 'Task list should be visible before full-page screenshot').toBeVisible();

    // When UI changes are intentional, run: npx playwright test tests/web/visual-regression.spec.ts --config web-app/playwright.config.ts --update-snapshots
    await expect(page, 'Tasks dashboard should match the approved full-page visual baseline').toHaveScreenshot(
      'tasks-dashboard-full-page.png',
      { fullPage: true, animations: 'disabled', maxDiffPixels: 100 }
    );
  });

  test('matches task creation form baseline', async ({ page }, testInfo) => {
    test.setTimeout(30_000);
    skipIfSnapshotMissing(testInfo, 'task-creation-form.png');
    await goToTasksDashboard(page);
    await page.getByTestId('new-task-btn').click();

    const taskForm = page.getByTestId('task-form');
    await expect(taskForm, 'Task creation form should be visible before clipped screenshot').toBeVisible();
    await expect(taskForm, 'Task creation form should match the approved visual baseline').toHaveScreenshot(
      'task-creation-form.png',
      { animations: 'disabled', maxDiffPixels: 100 }
    );
  });

  test('matches task card layout baseline', async ({ page }, testInfo) => {
    test.setTimeout(30_000);
    skipIfSnapshotMissing(testInfo, 'task-card-layout.png');
    await goToTasksDashboard(page);

    const firstTaskCard = page.getByTestId('task-card').first();
    await expect(firstTaskCard, 'At least one task card should be visible before layout screenshot').toBeVisible();
    await expect(firstTaskCard, 'Task card layout should match the approved visual baseline').toHaveScreenshot(
      'task-card-layout.png',
      { animations: 'disabled', maxDiffPixels: 100 }
    );
  });
});
