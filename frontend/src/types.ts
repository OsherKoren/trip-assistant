export type FeedbackRating = 'up' | 'down';

export interface Feedback {
  rating: FeedbackRating;
  comment?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  category?: string;
  confidence?: number;
  feedback?: Feedback;
  timestamp: Date;
}

export interface MessageResponse {
  answer: string;
  category: string;
  confidence: number;
  source: string | null;
}

export interface FeedbackRequest {
  message_content: string;
  category?: string;
  rating: FeedbackRating;
  comment?: string;
}

export interface FeedbackResponse {
  status: string;
  id: string;
}
