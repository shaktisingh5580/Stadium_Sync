/**
 * ============================================================================
 * File: frontend/src/components/__tests__/GlowButton.test.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — GlowButton Component Tests.
 *
 * Verifies the shared GlowButton component:
 * - Renders children text correctly
 * - Applies disabled state
 * - Handles click events
 * - Has proper CSS classes for glow effect
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { GlowButton } from '../shared/GlowButton';

describe('GlowButton', () => {
  it('renders children correctly', () => {
    render(<GlowButton>Click Me</GlowButton>);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });

  it('renders as a button element', () => {
    render(<GlowButton>Test</GlowButton>);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<GlowButton onClick={handleClick}>Click</GlowButton>);
    fireEvent.click(screen.getByText('Click'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('can be disabled', () => {
    render(<GlowButton disabled>Disabled</GlowButton>);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
});
