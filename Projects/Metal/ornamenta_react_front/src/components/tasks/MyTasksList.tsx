import React, { useState, useEffect } from 'react';
import {
  Button,
  Spinner,
  Card,
  CardBody,
  useDisclosure,
} from '@heroui/react';
import { Task } from '@/types/tasks';
import { Work } from '@/types/works';
import { taskService } from '@/services/taskService';
import { employeeService } from '@/services/employeeService';
import { workService } from '@/services/workService';
import { ViewTaskModal } from './ViewTaskModal';
import { TasksFilters } from './TasksFilters';
import { TasksTable } from './TasksTable';

export const MyTasksList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);
  const [works, setWorks] = useState<Work[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchValue, setSearchValue] = useState('');
  const [stateFilter, setStateFilter] = useState<string>('');
  const [workFilter, setWorkFilter] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  
  const { isOpen: isViewOpen, onOpen: onViewOpen, onOpenChange: onViewOpenChange } = useDisclosure();
  
  const itemsPerPage = 10;

  const stateOptions = [
    { label: 'Todos', value: '' },
    { label: 'Pending', value: 'PENDING' },
    { label: 'Asignada', value: 'ASSIGNED' },
    { label: 'Por Iniciar', value: 'READY' },
    { label: 'En Proceso', value: 'IN_PROGRESS' },
    { label: 'Completada', value: 'COMPLETED' },
    { label: 'Finalizada', value: 'FINISHED' },
  ];

  useEffect(() => {
    loadTasks();
    loadEmployees();
    loadWorks();
  }, [stateFilter, startDate, endDate]);

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const params: { startDate?: string; endDate?: string } = {};
      
      if (startDate) {
        params.startDate = new Date(startDate).toISOString();
      }
      
      if (endDate) {
        params.endDate = new Date(endDate).toISOString();
      }
      
      const response = await taskService.getMyTasks(params);
      
      const sortedTasks = (response.tasks || []).sort((a, b) => {
        const dateA = new Date(a.updated_at).getTime();
        const dateB = new Date(b.updated_at).getTime();
        return dateB - dateA;
      });
      
      setTasks(sortedTasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar tus tasks');
    } finally {
      setIsLoading(false);
    }
  };

  const loadEmployees = async () => {
    try {
      const response = await employeeService.getEmployees();
      setEmployees(response || []);
    } catch (err) {
      console.error('Error al cargar empleados:', err);
    }
  };

  const loadWorks = async () => {
    try {
      const response = await workService.getWorks();
      setWorks(response.works || []);
    } catch (err) {
      console.error('Error al cargar works:', err);
    }
  };

  const getEmployeeName = (userId?: string) => {
    if (!userId) return '-';
    const employee = employees.find(
      emp => emp.firebase_uid === userId || emp.identification_number === userId
    );
    return employee ? `${employee.first_name} ${employee.last_name}` : 'Sin asignar';
  };

  const getWorkName = (workId?: string) => {
    if (!workId) return '-';
    const work = works.find(w => w.work_id === workId);
    return work ? work.work_name : 'Work desconocido';
  };

  const handleViewTask = (task: Task) => {
    setSelectedTask(task);
    onViewOpen();
  };

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = 
      task.task_name?.toLowerCase().includes(searchValue.toLowerCase()) ||
      task.description?.toLowerCase().includes(searchValue.toLowerCase());
    
    const matchesState = !stateFilter || task.state === stateFilter;
    
    const matchesWork = !workFilter || task.work_id === workFilter;
    
    return matchesSearch && matchesState && matchesWork;
  });

  const pages = Math.ceil(filteredTasks.length / itemsPerPage);
  const start = (currentPage - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  const items = filteredTasks.slice(start, end);

  const getStateLabel = (state: string) => {
    switch (state) {
      case 'PENDING':
        return 'Pending';
      case 'ASSIGNED':
        return 'Asignada';
      case 'READY':
        return 'Por Iniciar';
      case 'IN_PROGRESS':
        return 'En Proceso';
      case 'COMPLETED':
        return 'Completada';
      case 'FINISHED':
        return 'Finalizada';
      default:
        return state;
    }
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case 'PENDING':
        return { bg: '#f5f5f5', color: '#666666' };
      case 'ASSIGNED':
        return { bg: '#dbeafe', color: '#1e40af' };
      case 'READY':
        return { bg: '#c7d2fe', color: '#3730a3' };
      case 'IN_PROGRESS':
        return { bg: '#fef3c7', color: '#92400e' };
      case 'COMPLETED':
        return { bg: '#d1fae5', color: '#065f46' };
      case 'FINISHED':
        return { bg: '#fed7aa', color: '#9a3412' };
      default:
        return { bg: '#f0fdf4', color: '#166534' };
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <Spinner label="Cargando tus tasks..." />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-1 border-red-200 bg-red-50">
        <CardBody>
          <p className="text-red-600">{error}</p>
          <Button
            color="warning"
            className="mt-4 w-fit"
            onPress={loadTasks}
          >
            Reintentar
          </Button>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-4 mt-4">
      <TasksFilters
        searchValue={searchValue}
        onSearchChange={setSearchValue}
        stateFilter={stateFilter}
        onStateFilterChange={(value) => {
          setStateFilter(value);
          setCurrentPage(1);
        }}
        stateOptions={stateOptions}
        workFilter={workFilter}
        onWorkFilterChange={(value) => {
          setWorkFilter(value);
          setCurrentPage(1);
        }}
        works={works}
        startDate={startDate}
        onStartDateChange={setStartDate}
        endDate={endDate}
        onEndDateChange={setEndDate}
      />

      {items.length === 0 ? (
        <Card className="border-1 border-gray-200">
          <CardBody className="text-center py-10">
            <p className="text-gray-500">No tienes tasks asignadas</p>
          </CardBody>
        </Card>
      ) : (
        <TasksTable
          items={items}
          currentPage={currentPage}
          pages={pages}
          onPageChange={setCurrentPage}
          getEmployeeName={getEmployeeName}
          getWorkName={getWorkName}
          getStateLabel={getStateLabel}
          getStateColor={getStateColor}
          onViewTask={handleViewTask}
        />
      )}

      {selectedTask && (
        <ViewTaskModal
          isOpen={isViewOpen}
          onOpenChange={onViewOpenChange}
          task={selectedTask}
          employeeName={getEmployeeName(selectedTask.assigned_user_id ?? undefined)}
          stateLabel={getStateLabel(selectedTask.state)}
          stateColor={getStateColor(selectedTask.state)}
          onTaskUpdated={loadTasks}
        />
      )}
    </div>
  );
};
