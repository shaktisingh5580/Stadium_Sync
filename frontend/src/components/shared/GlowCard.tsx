/**
 * ===============================================================================
 * File: frontend/src/components/shared/GlowCard.tsx
 * Purpose: Styled card component - container with neon glow border. Used for 
 *          info boxes, alerts, POI details throughout app.
 * Architecture: Reusable card with glow border animation. Props: children, 
 *               variant (info/alert/success/error).
 * Inputs: Card children (content).
 * Outputs: Rendered card with glow border styling.
 * Hackathon Vertical: Accessibility & Code Quality
 * ===============================================================================
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
