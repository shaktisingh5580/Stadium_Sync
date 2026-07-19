/**
 * ============================================================================
 * File: frontend/src/lib/utils.ts
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — CSS Utility Functions.
 *
 * Provides the `cn()` helper that merges Tailwind CSS classes using clsx + tailwind-merge.
 * This prevents class conflicts (e.g., `px-2 px-4` resolves to `px-4`) and supports
 * conditional class application throughout the component library.
 */
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
