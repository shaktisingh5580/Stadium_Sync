/**
 * ============================================================================
 * FILE: frontend/src/components/ui/message-bubble.stories.tsx
 * PURPOSE: Provides core functionality and logic for this module.
 * ARCHITECTURE: React/Vite/TypeScript component
 * INPUTS: Standard module props or API responses
 * OUTPUTS: Rendered DOM or internal logic
 * HACKATHON VERTICAL: Fan Experience & Navigation
 * ============================================================================
 */
import type { Meta, StoryObj } from '@storybook/react';
import { MessageBubble } from './message-bubble';

const meta = {
  title: 'UI/MessageBubble',
  component: MessageBubble,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof MessageBubble>;

export default meta;
type Story = StoryObj<typeof meta>;

export const UserMessage: Story = {
  args: {
    message: {
      id: '1',
      role: 'user',
      content: 'Where is the restroom?',
    },
  },
};

export const AssistantMessage: Story = {
  args: {
    message: {
      id: '2',
      role: 'assistant',
      content: 'The nearest restroom is located at **Section 203**. I have highlighted the route on your map.',
    },
  },
};
