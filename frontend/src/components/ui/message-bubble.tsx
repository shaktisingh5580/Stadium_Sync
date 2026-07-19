/**
 * ===============================================================================
 * File: frontend/src/components/ui/message-bubble.tsx
 * Purpose: Reusable message bubble component - renders fan or AI message 
 *          with appropriate styling (left/right alignment), timestamp, role.
 * Architecture: Takes message object with content, sender (fan/AI), timestamp. 
 *               Returns JSX with conditional alignment and styling.
 * Inputs: Message object {content, sender, timestamp}.
 * Outputs: Rendered message bubble JSX.
 * Hackathon Vertical: Accessibility & Code Quality
 * ===============================================================================
 */

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { User, Sparkles } from 'lucide-react';
import type { ChatMessage } from '@/hooks/useChat';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={cn(
        "flex w-full gap-4 p-4",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
      role="listitem"
      aria-label={isUser ? "Your message" : "AI Concierge response"}
    >
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-lg",
        isUser ? "bg-emerald-500/20 text-emerald-400" : "bg-white/[0.05] text-emerald-400 border border-emerald-500/20"
      )}>
        {isUser ? <User className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
      </div>
      
      <div className={cn(
        "flex flex-col gap-2 max-w-[80%]",
        isUser ? "items-end" : "items-start"
      )}>
        <div className={cn(
          "px-4 py-3 rounded-2xl backdrop-blur-md shadow-xl text-sm leading-relaxed",
          isUser 
            ? "bg-emerald-700 text-white rounded-tr-sm" 
            : "bg-white/[0.03] border border-white/[0.05] text-white/90 rounded-tl-sm"
        )}>
          {/* Extremely basic markdown parsing for bold text */}
          {message.content.split('**').map((part, i) => (
            i % 2 === 1 ? <strong key={i} className={isUser ? "text-white" : "text-emerald-400 font-semibold"}>{part}</strong> : <span key={i}>{part}</span>
          ))}
        </div>
      </div>
    </motion.div>
  );
};
