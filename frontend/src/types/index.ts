/**
 * Type definitions for the application
 */

export interface Note {
  id: string;
  user_id?: string;
  title: string;
  file_type: string;
  file_path: string;
  content: string;
  category?: string;
  tags: string[];
  created_at: string;
  updated_at?: string;
}

export interface NoteCreate {
  title: string;
  file_type: string;
  content: string;
  category?: string;
  tags?: string[];
}

export interface NoteUpdate {
  title?: string;
  category?: string;
  tags?: string[];
  content?: string;
}

export interface Conversation {
  id: string;
  user_id?: string;
  title: string;
  created_at: string;
  updated_at?: string;
  messages?: Message[];
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: SourceReference[];
  created_at: string;
}

export interface SourceReference {
  note_id: string;
  title: string;
  content_snippet: string;
  relevance_score: number;
}

export interface ChatRequest {
  question: string;
  conversation_id?: string;
}

export interface ChatResponse {
  answer: string;
  sources: SourceReference[];
  conversation_id: string;
}

export interface Deadline {
  id: string;
  user_id?: string;
  title: string;
  course?: string;
  description?: string;
  due_date: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'completed';
  reminder_sent: boolean;
  created_at: string;
  updated_at?: string;
}

export interface DeadlineCreate {
  title: string;
  course?: string;
  description?: string;
  due_date: string;
  priority?: 'low' | 'medium' | 'high';
}

export interface DeadlineUpdate {
  title?: string;
  course?: string;
  description?: string;
  due_date?: string;
  priority?: 'low' | 'medium' | 'high';
  status?: 'pending' | 'completed';
}
