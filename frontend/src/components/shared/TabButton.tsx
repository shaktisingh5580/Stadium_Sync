/**
 * ============================================================================
 * File: frontend/src/components/shared/TabButton.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — Tab Button (Shared UI Component).
 *
 * An accessible tab button with active/inactive states and icon support.
 * Used in the Sidebar for switching between Transit, Incident, and Eco-Vision panels.
 * Includes proper ARIA attributes for screen reader compatibility.
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
