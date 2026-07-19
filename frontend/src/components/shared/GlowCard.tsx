/**
 * ============================================================================
 * File: frontend/src/components/shared/GlowCard.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — Glow Card (Shared UI Component).
 *
 * A glassmorphism card container with a subtle glow border and backdrop blur.
 * Used as the wrapper for sidebar panels and dashboard widgets.
 */
import React from 'react';
import { cn } from '@/lib/utils';

interface GlowCardProps extends React.HTMLAttributes<HTMLDivElement> {
  active?: boolean;
}

export const GlowCard: React.FC<GlowCardProps> = ({ 
  children, 
  active = false, 
  className,
  ...props 
}) => {
  return (
    <div 
      className={cn(
        "glow-card p-4",
        active && "glow-card-active",
        className
      )}
      role={props.role || "region"}
      aria-live={props['aria-live'] || (active ? "polite" : "off")}
      {...props}
    >
      {children}
    </div>
  );
};
