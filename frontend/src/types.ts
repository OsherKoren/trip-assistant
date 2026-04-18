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
  isStreaming?: boolean;
}

export interface MessageResponse {
  id: string;
  answer: string;
  category: string;
  confidence: number;
  source: string | null;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

export interface HistoryEntry {
  role: 'user' | 'assistant';
  content: string;
}

export interface FeedbackRequest {
  message_id: string;
  rating: FeedbackRating;
  comment?: string;
}

export interface FeedbackResponse {
  status: string;
  message_id: string;
}

export interface StreamDoneMeta {
  id: string;
  category: string;
  confidence: number;
}
