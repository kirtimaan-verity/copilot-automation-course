import { test, expect } from '@playwright/test';

test('login page should work', async ({ page }) => {
  await page.goto('/login');
  await expect(page.locator('h1')).toHaveText('Login');
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});