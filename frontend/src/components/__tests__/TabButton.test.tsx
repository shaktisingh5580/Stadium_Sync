/**
 * ============================================================================
 * FILE: frontend/src/components/__tests__/TabButton.test.tsx
 * PURPOSE: Provides core functionality and logic for this module.
 * ARCHITECTURE: React/Vite/TypeScript component
 * INPUTS: Standard module props or API responses
 * OUTPUTS: Rendered DOM or internal logic
 * HACKATHON VERTICAL: Fan Experience & Navigation
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
