import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL;

test.describe('US-002 Filtering and Search', () => {
  test('TC-AC5-UI-01: Search updates with ~300ms debounce', async ({ page }) => {
    test.setTimeout(30000);

    expect(BASE_URL, 'BASE_URL must be set for web UI tests').toBeTruthy();
    await page.goto(BASE_URL as string);

    const searchInput = page.getByTestId('search-input');

    const isAlphaSearchRequest = (urlString: string): boolean => {
      const url = new URL(urlString);
      return (
        url.pathname.endsWith('/tasks') &&
        url.searchParams.get('search') === 'alpha'
      );
    };

    const alphaRequestTimes: number[] = [];
    page.on('request', (req) => {
      if (req.method() === 'GET' && isAlphaSearchRequest(req.url())) {
        alphaRequestTimes.push(Date.now());
      }
    });

    const alphaRequestPromise = page.waitForRequest(
      (req) => req.method() === 'GET' && isAlphaSearchRequest(req.url()),
      { timeout: 2000 }
    );

    await searchInput.click();
    await searchInput.pressSequentially('alpha', { delay: 40 });
    const tLastKeystroke = Date.now();

    const earlyRequestArrived = await page
      .waitForRequest(
        (req) => req.method() === 'GET' && isAlphaSearchRequest(req.url()),
        { timeout: 250 }
      )
      .then(() => true)
      .catch(() => false);

    expect(
      earlyRequestArrived,
      'No search request should fire within 250ms after final keystroke'
    ).toBe(false);

    await alphaRequestPromise;

    expect(alphaRequestTimes.length, 'Expected one debounced alpha request to be captured').toBeGreaterThan(0);
    const firstAlphaRequestAt = alphaRequestTimes[0];
    const elapsedMs = firstAlphaRequestAt - tLastKeystroke;

    expect(elapsedMs, `Debounce fired too early: ${elapsedMs}ms`).toBeGreaterThanOrEqual(280);
    expect(elapsedMs, `Debounce fired too late: ${elapsedMs}ms`).toBeLessThanOrEqual(650);

    expect(
      alphaRequestTimes.length,
      'Rapid typing burst should produce exactly one request for final term'
    ).toBe(1);

    await expect(page.getByTestId('task-list'), 'Task list should remain visible after search').toBeVisible();
  });
});
