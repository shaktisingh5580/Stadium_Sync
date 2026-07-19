/**
 * ============================================================================
 * File: frontend/src/components/__tests__/GlowCard.test.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — GlowCard Component Tests.
 *
 * Verifies the shared GlowCard container component:
 * - Renders children content
 * - Applies glow-card CSS class
 * - Supports custom className prop
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { GlowCard } from '../shared/GlowCard';

describe('GlowCard', () => {
  it('renders children correctly', () => {
    render(<GlowCard><p>Card Content</p></GlowCard>);
    expect(screen.getByText('Card Content')).toBeInTheDocument();
  });

  it('applies glow-card styling', () => {
    const { container } = render(<GlowCard>Content</GlowCard>);
    const card = container.firstElementChild;
    expect(card?.className).toContain('glow-card');
  });

  it('merges custom className', () => {
    const { container } = render(<GlowCard className="custom-class">Content</GlowCard>);
    const card = container.firstElementChild;
    expect(card?.className).toContain('custom-class');
  });
});
