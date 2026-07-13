import React from 'react';
import { cn } from './GlowCard';

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
      {...props}
    >
      {children}
    </button>
  );
};
