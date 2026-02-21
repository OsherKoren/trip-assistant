export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  category?: string;
  timestamp: Date;
}

export interface MessageResponse {
  answer: string;
  category: string;
  confidence: number;
  source: string | null;
}
