/**
 * ===============================================================================
 * File: frontend/src/components/shared/GlowButton.tsx
 * Purpose: Styled button component - neon glow effect, consistent theming. 
 *          Used for Send, Submit, Call buttons across app.
 * Architecture: Reusable button with neon glow on hover. Props: children, 
 *               onClick, disabled state, variant (primary/secondary).
 * Inputs: Button props (label, onClick, disabled).
 * Outputs: Rendered button with glow styling.
 * Hackathon Vertical: Accessibility & Code Quality
 * ===============================================================================
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
