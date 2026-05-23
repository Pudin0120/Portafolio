export type TaskState = 'PENDING' | 'ASSIGNED' | 'READY' | 'IN_PROGRESS' | 'COMPLETED' | 'FINISHED';

export interface Task {
  task_id: string;
  work_id: string;
  product_id?: string;
  task_name: string;
  description?: string;
  state: TaskState;
  labor?: number;
  labor_amount?: string;
  labor_formatted?: string;
  estimated_value?: number;
  estimated_value_amount?: string;
  estimated_value_formatted?: string;
  execution_order?: number;
  requires_validation?: boolean;
  is_blocked?: boolean;
  previous_task_id?: string;
  assigned_user_id?: string | null;
  is_assigned?: boolean;
  completed_by_user_id?: string;
  validated_by_user_id?: string;
  created_at?: string;
  updated_at: string;
}

export interface TaskListDTO {
  tasks: Task[];
  total: number;
}

export interface CreateTaskRequest {
  work_id: string;
  task_name: string;
  description?: string;
  execution_order: number;
}

export interface UpdateTaskRequest {
  task_name?: string;
  description?: string;
  state?: TaskState;
  execution_order?: number;
  assigned_user_id?: string;
  labor_amount?: number;
  estimated_value_amount?: number;
}
