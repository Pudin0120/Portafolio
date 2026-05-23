import { apiClient } from './apiClient';
import {
  Task,
  TaskListDTO,
  CreateTaskRequest,
  UpdateTaskRequest,
} from '@/types/tasks';

export const taskService = {
  /**
   * Gets all tasks with optional filters
   */
  async getTasks(params?: {
    startDate?: string;
    endDate?: string;
  }): Promise<TaskListDTO> {
    const queryParams = new URLSearchParams();
    if (params?.startDate) queryParams.append('start_date', params.startDate);
    if (params?.endDate) queryParams.append('end_date', params.endDate);
    
    const queryString = queryParams.toString();
    const url = queryString ? `/tasks/?${queryString}` : `/tasks/`;
    
    return apiClient.get<TaskListDTO>(url);
  },

  /**
   * Gets tasks assigned to a specific user
   */
  async getTasksByUserId(
    userId: string,
    params?: {
      startDate?: string;
      endDate?: string;
    }
  ): Promise<TaskListDTO> {
    const queryParams = new URLSearchParams();
    if (params?.startDate) queryParams.append('start_date', params.startDate);
    if (params?.endDate) queryParams.append('end_date', params.endDate);
    
    const queryString = queryParams.toString();
    const url = queryString 
      ? `/tasks/user/${userId}?${queryString}` 
      : `/tasks/user/${userId}`;
    
    return apiClient.get<TaskListDTO>(url);
  },

  /**
   * Gets tasks assigned to the current authenticated user
   */
  async getMyTasks(params?: {
    startDate?: string;
    endDate?: string;
  }): Promise<TaskListDTO> {
    const queryParams = new URLSearchParams();
    if (params?.startDate) queryParams.append('start_date', params.startDate);
    if (params?.endDate) queryParams.append('end_date', params.endDate);
    
    const queryString = queryParams.toString();
    const url = queryString ? `/tasks/me?${queryString}` : `/tasks/me`;
    
    return apiClient.get<TaskListDTO>(url);
  },

  /**
   * Gets tasks with optional filters
   */
  async getTasksByState(state?: string): Promise<TaskListDTO> {
    const params = new URLSearchParams();
    if (state) params.append('state', state);
    
    const queryString = params.toString();
    const url = queryString ? `/tasks/?${queryString}` : `/tasks/`;
    
    return apiClient.get<TaskListDTO>(url);
  },

  /**
   * Gets a specific task
   */
  async getTaskById(taskId: string): Promise<Task> {
    return apiClient.get<Task>(`/tasks/${taskId}`);
  },

  /**
   * Gets the tasks for a work especifico
   */
  async getTasksByWorkId(workId: string): Promise<TaskListDTO> {
    return apiClient.get<TaskListDTO>(`/works/${workId}/tasks`);
  },

  /**
   * Creates a new task
   */
  async createTask(taskData: CreateTaskRequest): Promise<Task> {
    return apiClient.post<Task>(`/tasks/`, taskData);
  },

  /**
   * Updates a task using PUT
   */
  async updateTask(taskId: string, taskData: UpdateTaskRequest | Record<string, any>): Promise<Task> {
    console.log(' taskService.updateTask llamado');
    console.log('  - Task ID:', taskId);
    console.log('  - Task Data:', taskData);
    console.log('  - URL completa:', `/tasks/${taskId}`);
    
    try {
      const result = await apiClient.put<Task>(`/tasks/${taskId}`, taskData);
      console.log('OK Response del backend:', result);
      return result;
    } catch (error) {
      console.error('ERROR Error en taskService.updateTask:', error);
      throw error;
    }
  },

  /**
   * Assigns a task to a user
   * POST /tasks/{task_id}/assign
   */
  async assignTask(taskId: string, userId: string): Promise<Task> {
    return apiClient.post<Task>(`/tasks/${taskId}/assign`, {
      user_id: userId,
    });
  },

  /**
   * Reorders a task within a work
   * PATCH /works/{work_id}/tasks/{task_id}/reorder?new_execution_order=X
   */
  async reorderTask(workId: string, taskId: string, newExecutionOrder: number): Promise<void> {
    return apiClient.patch<void>(`/works/${workId}/tasks/${taskId}/reorder?new_execution_order=${newExecutionOrder}`, {});
  },

  /**
   * Updates task status using POST
   */
  async updateTaskState(taskId: string, newState: string): Promise<Task> {
    return apiClient.post<Task>(`/tasks/${taskId}/change-state`, {
      new_state: newState,
    });
  },

  /**
   * Deletes a task
   */
  async deleteTask(taskId: string): Promise<void> {
    return apiClient.delete<void>(`/tasks/${taskId}`);
  },
};
