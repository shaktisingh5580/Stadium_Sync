/**
 * ============================================================================
 * File: frontend/src/components/shared/GlowButton.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — Glow Button (Shared UI Component).
 *
 * A reusable button with a glowing hover effect and gradient border,
 * supporting primary/secondary/danger variants. Used across all panels.
 */
import React from 'react';
import { cn } from '@/lib/utils';

interface GlowButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  active?: boolean;
}

export const GlowButton: React.FC<GlowButtonProps> = ({ 
  children, 
  active = false,
  className,
  ...props 
}) => {
  return (
    <button 
      className={cn(
        "glow-button flex items-center justify-center gap-2",
        active && "bg-green-500/20 border-green-400 shadow-[0_0_20px_rgba(34,197,94,0.2)]",
        className
      )}
      aria-pressed={active ? "true" : "false"}
      {...props}
    >
      {children}
    </button>
  );
};
