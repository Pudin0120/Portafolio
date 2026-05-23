import React from 'react';
import {
  Input,
  Select,
  SelectItem,
} from '@heroui/react';
import { Search, Calendar } from 'lucide-react';
import { Work } from '@/types/works';

interface TasksFiltersProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  stateFilter: string;
  onStateFilterChange: (value: string) => void;
  stateOptions: Array<{ label: string; value: string }>;
  workFilter: string;
  onWorkFilterChange: (value: string) => void;
  works: Work[];
  startDate: string;
  onStartDateChange: (value: string) => void;
  endDate: string;
  onEndDateChange: (value: string) => void;
}

export const TasksFilters: React.FC<TasksFiltersProps> = ({
  searchValue,
  onSearchChange,
  stateFilter,
  onStateFilterChange,
  stateOptions,
  workFilter,
  onWorkFilterChange,
  works,
  startDate,
  onStartDateChange,
  endDate,
  onEndDateChange,
}) => {
  return (
    <div className="space-y-4">
      <div className="flex gap-4 flex-col sm:flex-row">
        <Input
          isClearable
          className="w-full sm:max-w-xs"
          placeholder="Search task..."
          startContent={<Search className="w-4 h-4" />}
          value={searchValue}
          onValueChange={onSearchChange}
        />
        <Select
          selectedKeys={stateFilter ? [stateFilter] : ['']}
          onSelectionChange={(keys: any) => {
            const selected = Array.from(keys)[0] as string;
            onStateFilterChange(selected || '');
          }}
          placeholder="Filtrar por estado"
          className="w-full sm:max-w-xs"
          aria-label="Filtrar tasks por estado"
        >
          {stateOptions.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </Select>
        <Select
          selectedKeys={workFilter ? [workFilter] : ['']}
          onSelectionChange={(keys: any) => {
            const selected = Array.from(keys)[0] as string;
            onWorkFilterChange(selected || '');
          }}
          placeholder="Filtrar por work"
          className="w-full sm:max-w-xs"
          aria-label="Filtrar tasks por work"
        >
          <SelectItem key="" value="">
            Todos los works
          </SelectItem>
          {works.map((work) => (
            <SelectItem key={work.work_id} value={work.work_id}>
              {work.work_name}
            </SelectItem>
          ))}
        </Select>
      </div>
      
      <div className="flex gap-4 flex-col sm:flex-row items-start sm:items-end">
        <div className="w-full sm:max-w-xs">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Fecha desde
          </label>
          <Input
            type="datetime-local"
            className="w-full"
            value={startDate}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => onStartDateChange(e.target.value)}
            startContent={<Calendar className="w-4 h-4 text-gray-400" />}
          />
        </div>
        <div className="w-full sm:max-w-xs">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Fecha hasta
          </label>
          <Input
            type="datetime-local"
            className="w-full"
            value={endDate}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => onEndDateChange(e.target.value)}
            startContent={<Calendar className="w-4 h-4 text-gray-400" />}
          />
        </div>
      </div>
    </div>
  );
};
