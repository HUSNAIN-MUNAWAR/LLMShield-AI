import { test, expect } from '@playwright/test';

test('dashboard renders security product shell', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('LLMShield AI')).toBeVisible();
  await expect(page.getByText('Risk Command Center')).toBeVisible();
});
