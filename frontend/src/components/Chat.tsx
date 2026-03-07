import type { Feedback, Message } from '../types';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

interface ChatProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  onSend: (question: string) => void;
  onFeedback: (messageId: string, feedback: Feedback) => void;
}

export function Chat({ messages, isLoading, error, onSend, onFeedback }: ChatProps) {
  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} isLoading={isLoading} onFeedback={onFeedback} />
      {error && (
        <div role="alert" className="mx-4 mb-2 px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg text-sm">
          {error}
        </div>
      )}
      <MessageInput onSend={onSend} disabled={isLoading} />
    </div>
  );
}
