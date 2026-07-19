import { defineConfig, devices } from '@playwright/test';

// ============================================================
// Playwright configuration
// Referenced in Module 4 (Writer), Module 6 (Execution),
// Module 8 (visual regression).
// Test files live in ../tests/web. Baselines in ../tests/web/__snapshots__.
// ============================================================

export default defineConfig({
  testDir: '../tests/web',
  snapshotDir: '../tests/web/__snapshots__',
  fullyParallel: true,
  reporter: process.env.CI ? 'blob' : 'html',
  timeout: 30_000,
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  expect: {
    toHaveScreenshot: {
      maxDiffPixels: 100,
      threshold: 0.2,
    },
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
});
