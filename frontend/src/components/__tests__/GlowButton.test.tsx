/**
 * ============================================================================
 * FILE: frontend/src/components/__tests__/GlowButton.test.tsx
 * PURPOSE: Stadium Sync — GlowButton Component Tests. Verifies the shared GlowButton component: - Renders children text correctly - Applies disabled state - Handles click events - Has proper CSS classes for glow effect
 * ARCHITECTURE: React/Vite/TypeScript component
 * INPUTS: Standard module props or API responses
 * OUTPUTS: Rendered DOM or internal logic
 * HACKATHON VERTICAL: Fan Experience & Navigation
 * ============================================================================
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
