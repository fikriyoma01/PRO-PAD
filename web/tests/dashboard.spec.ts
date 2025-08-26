import { test, expect } from '@playwright/test';

test('Dashboard loads and shows key components', async ({ page }) => {
  // Navigate to the dashboard page
  await page.goto('/');

  // Check for a key static element to ensure the page is loading
  await expect(page.locator('label:has-text("Tahun")')).toBeVisible();

  // Wait for the API call to complete and the KPI to be populated.
  // We'll check that the value is not the initial state (e.g., not 0).
  // This is a proxy for the forecast data being loaded.
  const kpiValue = page.locator('div:has(> h2:has-text("Total Baseline")) + p');
  await expect(kpiValue).not.toHaveText('0', { timeout: 15000 }); // 15s timeout for API calls

  // Check if the new AssumptionCard is visible
  await expect(page.locator('h2:has-text("Asumsi & Algoritma")')).toBeVisible();

  // Check if the card has some content from the meta object
  await expect(page.locator('li:has-text("Base Total PAD")')).toBeVisible();
  await expect(page.locator('li:has-text("Model Averaging")')).toBeVisible();

  // Take a screenshot for verification
  await page.screenshot({ path: 'playwright-screenshot.png' });
});
