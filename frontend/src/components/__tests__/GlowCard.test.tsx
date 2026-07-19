/**
 * ============================================================================
 * FILE: frontend/src/components/__tests__/GlowCard.test.tsx
 * PURPOSE: Stadium Sync — GlowCard Component Tests. Verifies the shared GlowCard container component: - Renders children content - Applies glow-card CSS class - Supports custom className prop
 * ARCHITECTURE: React/Vite/TypeScript component
 * INPUTS: Standard module props or API responses
 * OUTPUTS: Rendered DOM or internal logic
 * HACKATHON VERTICAL: Fan Experience & Navigation
 * ============================================================================
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
