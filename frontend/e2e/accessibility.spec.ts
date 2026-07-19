/**
 * ============================================================================
 * FILE: frontend/e2e/accessibility.spec.ts
 * PURPOSE: Provides core functionality and logic for this module.
 * ARCHITECTURE: React/Vite/TypeScript component
 * INPUTS: Standard module props or API responses
 * OUTPUTS: Rendered DOM or internal logic
 * HACKATHON VERTICAL: Fan Experience & Navigation
 * ============================================================================
 */
import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test.describe('WCAG 2.1 AA Compliance', () => {
  test('Main chat interface is accessible', async ({ page }) => {
    const baseUrl = process.env.PLAYWRIGHT_TEST_BASE_URL || 'http://localhost:5173';
    await page.goto(baseUrl);
    
    // Inject axe-core into the page
    await injectAxe(page);
    
    // Check accessibility against WCAG 2.1 AA standards
    // This will throw an error if violations are found
    await checkA11y(page, undefined, {
      axeOptions: {
        runOnly: {
          type: 'tag',
          values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']
        }
      }
    });
  });
});
