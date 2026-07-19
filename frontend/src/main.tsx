/**
 * ===============================================================================
 * File: frontend/src/main.tsx
 * Purpose: React application bootstrap - mounts React App component to DOM 
 *          (#root) and initializes React Strict Mode for dev-only error 
 *          checking.
 * Architecture: Entry point for Vite dev server and production build. Sets up 
 *               StrictMode wrapper to catch side effects and state mutations.
 * Inputs: React App component, DOM element with id="root".
 * Outputs: React application mounted and rendering.
 * Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
 * ===============================================================================
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
