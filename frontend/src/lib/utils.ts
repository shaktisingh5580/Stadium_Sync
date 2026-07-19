/**
 * ============================================================================
 * FILE: frontend/src/lib/utils.ts
 * PURPOSE: Stadium Sync — CSS Utility Functions. Provides the `cn()` helper that merges Tailwind CSS classes using clsx + tailwind-merge. This prevents class conflicts (e.g., `px-2 px-4` resolves to `px-4`) and supports conditional class application throughout the component library.
 * ARCHITECTURE: React/Vite/TypeScript component
 * INPUTS: Standard module props or API responses
 * OUTPUTS: Rendered DOM or internal logic
 * HACKATHON VERTICAL: Fan Experience & Navigation
 * ============================================================================
 */
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
