import React from 'react';
import { cn } from './GlowCard';

interface TabButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  active?: boolean;
}

export const TabButton: React.FC<TabButtonProps> = ({ 
  children, 
  active = false,
  className,
  ...props 
}) => {
  return (
    <button 
      className={cn(
        "flex-1 py-3 text-sm font-semibold transition-colors duration-200 border-b-2",
        active 
          ? "bg-green-500/20 text-green-400 border-green-400" 
          : "text-slate-400 border-transparent hover:text-slate-200 hover:bg-slate-800/50",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};
