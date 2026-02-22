import { useEffect, useRef } from 'react';
import type { Feedback, Message } from '../types';
import { MessageBubble } from './MessageBubble';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  onFeedback: (messageId: string, feedback: Feedback) => void;
}

export function MessageList({ messages, isLoading, onFeedback }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {messages.length === 0 && !isLoading && (
        <div className="text-center text-gray-500 dark:text-gray-400 mt-8">
          <p className="text-2xl mb-2">Welcome! ✈️</p>
          <p>Ask me anything about your family trip to the Alps.</p>
        </div>
      )}
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          onFeedback={(feedback) => onFeedback(message.id, feedback)}
        />
      ))}
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2 rounded-lg" role="status">
            Thinking…
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
