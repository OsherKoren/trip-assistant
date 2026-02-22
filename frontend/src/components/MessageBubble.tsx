import type { Feedback, Message } from '../types';
import { MessageFeedback } from './MessageFeedback';

interface MessageBubbleProps {
  message: Message;
  onFeedback?: (feedback: Feedback) => void;
}

export function MessageBubble({ message, onFeedback }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div data-testid="message-bubble" className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div>
        <div
          className={`max-w-xs md:max-w-md px-4 py-2 rounded-lg ${
            isUser ? 'bg-blue-500 dark:bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
          }`}
        >
          {message.content}
        </div>
        {!isUser && (
          <div className="flex items-center justify-between mt-1">
            {onFeedback && (
              <MessageFeedback
                feedback={message.feedback}
                messageContent={message.content}
                category={message.category}
                onFeedback={onFeedback}
              />
            )}
            {message.confidence != null && (
              <span
                className={`ml-auto px-2 py-0.5 rounded-full text-xs font-medium ${
                  message.confidence >= 0.8
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                    : message.confidence >= 0.5
                      ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                      : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                }`}
              >
                {Math.round(message.confidence * 100)}%
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
