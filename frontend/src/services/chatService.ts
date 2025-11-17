/**
 * Chat API service
 */
import apiClient from './api';
import { ChatRequest, ChatResponse, Conversation } from '../types';

export const chatService = {
  /**
   * Ask a question
   */
  async askQuestion(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/api/chat/ask', request);
    return response.data;
  },

  /**
   * Get all conversations
   */
  async getConversations(page: number = 1, limit: number = 20): Promise<{ conversations: Conversation[]; total: number }> {
    const response = await apiClient.get('/api/chat/conversations', {
      params: { page, limit },
    });
    return response.data;
  },

  /**
   * Get a specific conversation with messages
   */
  async getConversation(conversationId: string): Promise<Conversation> {
    const response = await apiClient.get<Conversation>(`/api/chat/conversations/${conversationId}`);
    return response.data;
  },

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: string): Promise<void> {
    await apiClient.delete(`/api/chat/conversations/${conversationId}`);
  },

  /**
   * Update conversation title
   */
  async updateConversationTitle(conversationId: string, title: string): Promise<Conversation> {
    const response = await apiClient.put<Conversation>(
      `/api/chat/conversations/${conversationId}/title`,
      null,
      { params: { title } }
    );
    return response.data;
  },
};

export default chatService;
