/**
 * ============================================================================
 * File: frontend/src/components/__tests__/TabButton.test.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { TabButton } from '../shared/TabButton';

describe('TabButton', () => {
  it('renders children correctly', () => {
    render(<TabButton>Test Tab</TabButton>);
    expect(screen.getByText('Test Tab')).toBeInTheDocument();
  });

  it('has correct role and aria attributes', () => {
    render(<TabButton active={true}>Active Tab</TabButton>);
    const button = screen.getByRole('tab');
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute('aria-selected', 'true');
  });
});
