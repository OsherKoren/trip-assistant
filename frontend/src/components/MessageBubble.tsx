import ReactMarkdown from 'react-markdown';
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
          className={`max-w-[85vw] md:max-w-md px-4 py-2 rounded-lg ${
            isUser ? 'bg-blue-500 dark:bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
          }`}
        >
          {isUser ? (
            message.content
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-headings:my-2">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
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
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                    : message.confidence >= 0.5
                      ? 'bg-blue-50 text-blue-500 dark:bg-blue-900/20 dark:text-blue-400'
                      : 'bg-blue-50/50 text-blue-400 dark:bg-blue-900/10 dark:text-blue-500'
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
