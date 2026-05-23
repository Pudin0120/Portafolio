export interface WorkSnapshot {
  product_id: string;
  product_name: string;
  product_type: string;
  price_amount: string;
  price_currency: string;
  purchase_price_amount?: string;
  purchase_price_currency?: string;
  sale_price_amount?: string;
  sale_price_currency?: string;
  composition?: Record<string, any>;
  dimensions?: Record<string, any>;
  quantity_multiplier?: string;
}

export interface WorkProduct {
  product_id: string;
  work_id: string;
  quantity: number;
  execution_order: number;
  state: string;
  snapshot: WorkSnapshot | null;
  task_ids: string[];
  product_name: string;
  product_type: string;
  current_price?: {
    amount: string;
    currency: string;
    sale_price_amount?: string;
    sale_price_currency?: string;
    purchase_price_amount?: string;
    purchase_price_currency?: string;
  };
  effective_unit_price?: {
    amount: string;
    currency: string;
  };
  line_total_amount?: number;
}

export interface Task {
  task_id: string;
  work_id: string;
  task_name: string;
  description: string;
  state: string;
  execution_order?: number;
  labor_amount: string;
  labor_formatted: string;
  estimated_value_amount: string;
  estimated_value_formatted: string;
  assigned_user_id?: string;
  is_assigned: boolean;
  parent_composite_id?: string | null;
  composite_task_slot?: number | null;
  composite_total_slots?: number | null;
  is_blocked?: boolean;
  previous_task_id?: string | null;
  product_id?: string;
  product_name?: string;
}

export interface TaskWithHierarchy extends Task {
  parent_composite_id: string | null;
  composite_task_slot: number | null;
  composite_total_slots: number | null;
  is_blocked: boolean;
  previous_task_id?: string;
}

export interface CompositeGroup {
  composite_id: string | null;
  composite_name: string | null;
  start_execution_order: number;
  end_execution_order: number;
  tasks: TaskWithHierarchy[];
}

export interface TasksHierarchyResponse {
  work_id: string;
  total_tasks: number;
  composite_groups: CompositeGroup[];
}

export interface Work {
  work_id: string;
  client_identification: string;
  work_name: string;
  description: string;
  state: string;
  tax: number;
  start_date: string;
  end_aprox_delivery_date: string;
  end_delivery_date: string;
  deposit_amount: string;
  deposit_currency: string;
  completion_percentage: number;
  products_value: string;
  work_value: string;
  products: WorkProduct[];
  tasks: Task[];
}

export interface CreateWorkRequest {
  client_identification: string;
  work_name: string;
  description?: string;
  tax?: number;
  end_aprox_delivery_date?: string;
  deposit_amount?: number | string;
}

export interface AddProductToWorkRequest {
  product_id: string;
  quantity: number;
  execution_order?: number;
}

export interface StartWorkResponseDTO {
  work_id: string;
  work_name: string;
  state: string;
  total_tasks_generated: number;
  started_at: string;
}

export interface DeliverWorkResponseDTO {
  work_id: string;
  work_name: string;
  state: string;
  delivery_date: string;
  final_value: string;
  completion_percentage: number;
}

export interface WorksResponse {
  works: Work[];
  total: number;
}
