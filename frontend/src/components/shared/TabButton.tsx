/**
 * ===============================================================================
 * File: frontend/src/components/shared/TabButton.tsx
 * Purpose: Tab button component - toggles between tabs in sidebar 
 *          (Nav, Transit, Incidents, Eco-Vision). Consistent styling.
 * Architecture: Button variant with active/inactive state styling. Props: 
 *               label, isActive, onClick.
 * Inputs: Tab selection.
 * Outputs: Rendered tab button with active state styling.
 * Hackathon Vertical: Accessibility & Code Quality
 * ===============================================================================
 */

import React from 'react';
import { cn } from '@/lib/utils';

interface TabButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  active?: boolean;
}

/**
 * TabButton component for rendering accessible, stylable tab controls.
 * 
 * @param {TabButtonProps} props - The component props.
 * @returns {JSX.Element} The rendered tab button.
 */
export const TabButton: React.FC<TabButtonProps> = ({ 
  children, 
  active = false,
  className,
  ...props 
}) => {
  return (
    <button 
      role="tab"
      aria-selected={active}
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
