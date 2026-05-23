import React from 'react';
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Pagination,
} from '@heroui/react';
import { Task } from '@/types/tasks';

interface TasksTableProps {
  items: Task[];
  currentPage: number;
  pages: number;
  onPageChange: (page: number) => void;
  getEmployeeName: (userId?: string) => string;
  getWorkName: (workId?: string) => string;
  getStateLabel: (state: string) => string;
  getStateColor: (state: string) => { bg: string; color: string };
  onViewTask: (task: Task) => void;
}

export const TasksTable: React.FC<TasksTableProps> = ({
  items,
  currentPage,
  pages,
  onPageChange,
  getEmployeeName,
  getWorkName,
  getStateLabel,
  getStateColor,
  onViewTask,
}) => {
  return (
    <Table
      aria-label="Tabla de tasks"
      bottomContent={
        pages > 1 ? (
          <div className="flex w-full justify-center">
            <Pagination
              isCompact
              color="warning"
              page={currentPage}
              total={pages}
              onChange={onPageChange}
            />
          </div>
        ) : null
      }
    >
      <TableHeader>
        <TableColumn key="name" allowsSorting>
          Nombre
        </TableColumn>
        <TableColumn key="work">Work</TableColumn>
        <TableColumn key="encargado">Encargado</TableColumn>
        <TableColumn key="status" className="min-w-[120px]">
          Estado
        </TableColumn>
      </TableHeader>
      <TableBody items={items} emptyContent={"No hay tasks"}>
        {(item: Task) => {
          const stateColors = getStateColor(item.state);
          return (
            <TableRow 
              key={item.task_id}
              className="cursor-pointer hover:bg-table-row-hover transition-colors"
              onClick={() => onViewTask(item)}
            >
              <TableCell>{item.task_name}</TableCell>
              <TableCell>{getWorkName(item.work_id ?? undefined)}</TableCell>
              <TableCell>{getEmployeeName(item.assigned_user_id ?? undefined)}</TableCell>
              <TableCell>
                <span
                  className="px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap inline-block"
                  style={{
                    backgroundColor: stateColors.bg,
                    color: stateColors.color,
                  }}
                >
                  {getStateLabel(item.state)}
                </span>
              </TableCell>
            </TableRow>
          );
        }}
      </TableBody>
    </Table>
  );
};
