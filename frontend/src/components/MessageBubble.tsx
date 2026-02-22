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
              <span className="text-xs text-gray-400 dark:text-gray-500 ml-auto">
                Confidence: {Math.round(message.confidence * 100)}%
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
