import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

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
      {...props}
    >
      {children}
    </div>
  );
};
