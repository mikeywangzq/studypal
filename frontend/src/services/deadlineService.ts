/**
 * Deadline API service
 */
import apiClient from './api';
import { Deadline, DeadlineCreate, DeadlineUpdate } from '../types';

export const deadlineService = {
  /**
   * Create a new deadline
   */
  async createDeadline(deadline: DeadlineCreate): Promise<Deadline> {
    const response = await apiClient.post<Deadline>('/api/deadlines', deadline);
    return response.data;
  },

  /**
   * Get all deadlines with filters
   */
  async getDeadlines(params?: {
    status?: 'pending' | 'completed';
    from_date?: string;
    to_date?: string;
    priority?: 'low' | 'medium' | 'high';
    course?: string;
    page?: number;
    limit?: number;
  }): Promise<{ deadlines: Deadline[]; total: number }> {
    const response = await apiClient.get('/api/deadlines', { params });
    return response.data;
  },

  /**
   * Get upcoming deadlines
   */
  async getUpcomingDeadlines(days: number = 7): Promise<Deadline[]> {
    const response = await apiClient.get<Deadline[]>('/api/deadlines/upcoming', {
      params: { days },
    });
    return response.data;
  },

  /**
   * Get overdue deadlines
   */
  async getOverdueDeadlines(): Promise<Deadline[]> {
    const response = await apiClient.get<Deadline[]>('/api/deadlines/overdue');
    return response.data;
  },

  /**
   * Get deadline statistics
   */
  async getStatistics(): Promise<{
    total: number;
    pending: number;
    completed: number;
    overdue: number;
    upcoming_7days: number;
  }> {
    const response = await apiClient.get('/api/deadlines/statistics');
    return response.data;
  },

  /**
   * Get a specific deadline
   */
  async getDeadline(deadlineId: string): Promise<Deadline> {
    const response = await apiClient.get<Deadline>(`/api/deadlines/${deadlineId}`);
    return response.data;
  },

  /**
   * Update a deadline
   */
  async updateDeadline(deadlineId: string, deadline: DeadlineUpdate): Promise<Deadline> {
    const response = await apiClient.put<Deadline>(`/api/deadlines/${deadlineId}`, deadline);
    return response.data;
  },

  /**
   * Mark deadline as completed
   */
  async completeDeadline(deadlineId: string): Promise<Deadline> {
    const response = await apiClient.patch<Deadline>(`/api/deadlines/${deadlineId}/complete`);
    return response.data;
  },

  /**
   * Delete a deadline
   */
  async deleteDeadline(deadlineId: string): Promise<void> {
    await apiClient.delete(`/api/deadlines/${deadlineId}`);
  },
};

export default deadlineService;
