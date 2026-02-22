import { useState } from 'react';
import type { Feedback, FeedbackRating } from '../types';
import { sendFeedback } from '../api/client';
import { useAuth } from '../hooks/useAuth';

interface MessageFeedbackProps {
  feedback?: Feedback;
  messageContent: string;
  category?: string;
  onFeedback: (feedback: Feedback) => void;
}

export function MessageFeedback({ feedback, messageContent, category, onFeedback }: MessageFeedbackProps) {
  const { getToken } = useAuth();
  const [selectedRating, setSelectedRating] = useState<FeedbackRating | null>(null);
  const [comment, setComment] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const isSubmitted = !!feedback;

  const handleToggle = (rating: FeedbackRating) => {
    if (isSubmitted) return;
    setSelectedRating(rating);
  };

  const handleSubmit = async () => {
    if (!selectedRating || isSubmitted) return;
    setIsSending(true);
    setSendError(null);
    const feedbackData: Feedback = {
      rating: selectedRating,
      ...(selectedRating === 'down' && comment.trim() ? { comment: comment.trim() } : {}),
    };
    try {
      await sendFeedback(
        {
          message_content: messageContent,
          category,
          rating: selectedRating,
          ...(selectedRating === 'down' && comment.trim() ? { comment: comment.trim() } : {}),
        },
        getToken,
      );
      onFeedback(feedbackData);
    } catch {
      setSendError('Failed to send feedback');
    } finally {
      setIsSending(false);
    }
  };

  const displayRating = feedback?.rating ?? selectedRating;

  return (
    <div className="mt-1 flex flex-col items-start gap-1">
      <div className="flex items-center gap-1">
        <button
          type="button"
          aria-label="Thumbs up"
          disabled={isSubmitted}
          onClick={() => handleToggle('up')}
          className={`p-2 rounded transition-colors ${
            displayRating === 'up'
              ? 'text-green-600 dark:text-green-400'
              : 'text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'
          } disabled:cursor-default`}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-6 h-6">
            <path d="M1 8.998a1 1 0 0 1 1-1h3v8H2a1 1 0 0 1-1-1v-6Zm5-1h3.382a1 1 0 0 0 .894-.553l1.448-2.894A2 2 0 0 1 13.236 3.5h.028a.5.5 0 0 1 .5.5v2.5a.5.5 0 0 0 .5.5h3a1.5 1.5 0 0 1 1.476 1.77l-.87 4.79A2.5 2.5 0 0 1 15.41 15.5H6v-7.502Z" />
          </svg>
        </button>
        <button
          type="button"
          aria-label="Thumbs down"
          disabled={isSubmitted}
          onClick={() => handleToggle('down')}
          className={`p-2 rounded transition-colors ${
            displayRating === 'down'
              ? 'text-red-600 dark:text-red-400'
              : 'text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'
          } disabled:cursor-default`}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-6 h-6">
            <path d="M19 11.002a1 1 0 0 1-1 1h-3v-8h2a1 1 0 0 1 1 1v6Zm-5 1h-3.382a1 1 0 0 0-.894.553l-1.448 2.894A2 2 0 0 1 6.764 16.5h-.028a.5.5 0 0 1-.5-.5V13.5a.5.5 0 0 0-.5-.5h-3a1.5 1.5 0 0 1-1.476-1.77l.87-4.79A2.5 2.5 0 0 1 4.59 4.5H14v7.502Z" />
          </svg>
        </button>
        {selectedRating && !isSubmitted && (
          <button
            type="button"
            aria-label="Submit feedback"
            onClick={handleSubmit}
            disabled={isSending}
            className="ml-1 px-4 py-1.5 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors disabled:opacity-50"
          >
            {isSending ? 'Sending...' : 'Submit'}
          </button>
        )}
      </div>
      {selectedRating === 'down' && !isSubmitted && (
        <div className="flex flex-col gap-1 w-full max-w-xs">
          <textarea
            aria-label="Feedback comment"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="What went wrong? (optional)"
            className="w-full px-2 py-1 text-sm border rounded dark:bg-gray-800 dark:border-gray-600 dark:text-gray-200"
            rows={2}
          />
        </div>
      )}
      {sendError && (
        <p className="text-xs text-red-500">{sendError}</p>
      )}
    </div>
  );
}
