// Types for service provision task details in payroll

export interface TaskSummaryItem {
  task_name: string;
  task_count: number;
  labor_cost_per_task: string;
  labor_cost_per_task_formatted: string;
  total_labor_cost: string;
  total_labor_cost_formatted: string;
}

export interface ServiceProvisionTasksDetail {
  payroll_id: string;
  payroll_history_id: string;
  identification_number: string;
  period_start_date: string;
  period_end_date: string;
  contract_type: string;
  tasks_summary: TaskSummaryItem[];
  total_tasks_count: number;
  total_labor_cost: string;
  total_labor_cost_formatted: string;
}
