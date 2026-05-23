# Frontend Integration: Task Endpoints

##  Integracion en tu Frontend

### 1. React Hook para Obtener Tasks

```javascript
import { useState, useEffect } from 'react';

/**
 * Hook personalizado para obtener tasks del user actual
 */
export function useMyTasks(token) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!token) return;

    const fetchTasks = async () => {
      try {
        const response = await fetch('/api/tasks/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('Token expirado. Please, inicia sesion de nuevo.');
          }
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        setTasks(data.tasks);
        setError(null);
      } catch (err) {
        setError(err.message);
        setTasks([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [token]);

  return { tasks, loading, error };
}
```

### 2. Componente React para Listar Tasks

```javascript
import React from 'react';
import { useMyTasks } from './hooks/useMyTasks';

export function TaskList({ token }) {
  const { tasks, loading, error } = useMyTasks(token);

  if (loading) {
    return <div className="loading">Cargando tasks...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (tasks.length === 0) {
    return <div className="empty">No tienes tasks asignadas</div>;
  }

  return (
    <div className="task-list">
      <h2>Mis Tasks ({tasks.length})</h2>
      {tasks.map((task) => (
        <TaskCard key={task.task_id} task={task} />
      ))}
    </div>
  );
}

function TaskCard({ task }) {
  const getStateColor = (state) => {
    const colors = {
      'PENDING': '#gray',
      'ASSIGNED': '#blue',
      'READY': '#green',
      'IN_PROGRESS': '#orange',
      'COMPLETED': '#purple',
      'FINISHED': '#darkgreen',
    };
    return colors[state] || '#gray';
  };

  return (
    <div className="task-card" style={{ borderLeft: `4px solid ${getStateColor(task.state)}` }}>
      <h3>{task.task_name}</h3>
      <p className="description">{task.description}</p>
      
      <div className="task-meta">
        <span className="state">{task.state}</span>
        <span className="value">{task.labor_formatted}</span>
      </div>

      <button onClick={() => openTaskDetail(task.task_id)}>
        Ver Detalles
      </button>
    </div>
  );
}
```

### 3. Servicio de API Reutilizable

```javascript
/**
 * Servicio para interactuar con endpoints de tasks
 */
class TaskService {
  constructor(baseUrl = '/api', getToken) {
    this.baseUrl = baseUrl;
    this.getToken = getToken;
  }

  /**
   * Obtiene tasks del user autenticado
   */
  async getMyTasks() {
    return this.fetchWithAuth(`${this.baseUrl}/tasks/me`);
  }

  /**
   * Obtiene tasks de un user especifico (admin/manager)
   */
  async getUserTasks(userId) {
    return this.fetchWithAuth(`${this.baseUrl}/tasks/user/${userId}`);
  }

  /**
   * Obtiene tasks de un work
   */
  async getWorkTasks(workId) {
    return this.fetchWithAuth(`${this.baseUrl}/tasks/work/${workId}`);
  }

  /**
   * Obtiene resumen de tasks de un work
   */
  async getWorkTasksSummary(workId) {
    return this.fetchWithAuth(`${this.baseUrl}/tasks/work/${workId}/summary`);
  }

  /**
   * Gets a specific task
   */
  async getTask(taskId) {
    return this.fetchWithAuth(`${this.baseUrl}/tasks/${taskId}`);
  }

  /**
   * Helper para hacer requests autenticados
   */
  async fetchWithAuth(url, options = {}) {
    const token = this.getToken();
    if (!token) {
      throw new Error('No hay token disponible');
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error ${response.status}`);
    }

    return response.json();
  }
}

// Uso
const taskService = new TaskService('/api', () => localStorage.getItem('token'));
const myTasks = await taskService.getMyTasks();
```

### 4. Dashboard de Tasks Completo

```javascript
import React, { useState, useEffect } from 'react';

export function TaskDashboard({ token }) {
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTasks();
    // Actualizar cada 30 segundos
    const interval = setInterval(fetchTasks, 30000);
    return () => clearInterval(interval);
  }, [token]);

  async function fetchTasks() {
    try {
      const response = await fetch('/api/tasks/me', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      setTasks(data.tasks);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  }

  const filteredTasks = filter === 'ALL' 
    ? tasks 
    : tasks.filter(t => t.state === filter);

  const stats = {
    total: tasks.length,
    pending: tasks.filter(t => t.state === 'PENDING').length,
    assigned: tasks.filter(t => t.state === 'ASSIGNED').length,
    inProgress: tasks.filter(t => t.state === 'IN_PROGRESS').length,
    finished: tasks.filter(t => t.state === 'FINISHED').length,
  };

  return (
    <div className="task-dashboard">
      <h1>Mis Tasks</h1>

      {/* Stats */}
      <div className="stats">
        <StatCard label="Total" value={stats.total} />
        <StatCard label="Asignadas" value={stats.assigned} color="blue" />
        <StatCard label="En Progreso" value={stats.inProgress} color="orange" />
        <StatCard label="Finalizadas" value={stats.finished} color="green" />
      </div>

      {/* Filters */}
      <div className="filters">
        <button 
          className={filter === 'ALL' ? 'active' : ''} 
          onClick={() => setFilter('ALL')}
        >
          Todas
        </button>
        <button 
          className={filter === 'ASSIGNED' ? 'active' : ''} 
          onClick={() => setFilter('ASSIGNED')}
        >
          Asignadas
        </button>
        <button 
          className={filter === 'IN_PROGRESS' ? 'active' : ''} 
          onClick={() => setFilter('IN_PROGRESS')}
        >
          En Progreso
        </button>
        <button 
          className={filter === 'FINISHED' ? 'active' : ''} 
          onClick={() => setFilter('FINISHED')}
        >
          Finalizadas
        </button>
      </div>

      {/* Task List */}
      <div className="task-list">
        {loading ? (
          <div className="loading">Cargando...</div>
        ) : filteredTasks.length === 0 ? (
          <div className="empty">No hay tasks en esta categoria</div>
        ) : (
          filteredTasks.map(task => (
            <TaskItem key={task.task_id} task={task} />
          ))
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, color = 'gray' }) {
  return (
    <div className="stat-card" style={{ borderTopColor: color }}>
      <h3>{label}</h3>
      <p className="value">{value}</p>
    </div>
  );
}

function TaskItem({ task }) {
  return (
    <div className="task-item">
      <div className="task-header">
        <h4>{task.task_name}</h4>
        <span className={`state state-${task.state.toLowerCase()}`}>
          {task.state}
        </span>
      </div>
      
      <p className="description">{task.description}</p>
      
      <div className="task-footer">
        <div className="values">
          <span className="labor">Mano de obra: {task.labor_formatted}</span>
          <span className="estimated">Estimado: {task.estimated_value_formatted}</span>
        </div>
        <button className="detail-btn">Detalles</button>
      </div>
    </div>
  );
}
```

### 5. CSS Styling (Tailwind)

```css
/* Task Dashboard */
.task-dashboard {
  @apply p-6;
}

.task-dashboard h1 {
  @apply text-3xl font-bold mb-6;
}

/* Stats */
.stats {
  @apply grid grid-cols-4 gap-4 mb-6;
}

.stat-card {
  @apply border-t-4 bg-white p-4 rounded shadow;
}

.stat-card h3 {
  @apply text-sm font-semibold text-gray-600;
}

.stat-card .value {
  @apply text-2xl font-bold text-gray-900;
}

/* Filters */
.filters {
  @apply flex gap-2 mb-6;
}

.filters button {
  @apply px-4 py-2 rounded border border-gray-300 hover:bg-gray-50;
}

.filters button.active {
  @apply bg-blue-500 text-white border-blue-500;
}

/* Task List */
.task-list {
  @apply space-y-4;
}

.task-item {
  @apply bg-white p-4 rounded shadow hover:shadow-lg transition;
}

.task-header {
  @apply flex justify-between items-start mb-3;
}

.task-header h4 {
  @apply font-bold text-lg;
}

.state {
  @apply px-3 py-1 rounded text-sm font-semibold;
}

.state-assigned { @apply bg-blue-100 text-blue-800; }
.state-in_progress { @apply bg-orange-100 text-orange-800; }
.state-finished { @apply bg-green-100 text-green-800; }

.description {
  @apply text-gray-600 mb-3;
}

.task-footer {
  @apply flex justify-between items-center pt-3 border-t;
}

.values {
  @apply flex gap-4 text-sm;
}

.labor { @apply font-semibold; }
.estimated { @apply text-gray-600; }

.detail-btn {
  @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600;
}
```

### 6. Vue.js Alternative

```vue
<template>
  <div class="task-container">
    <h1>Mis Tasks</h1>
    
    <div v-if="loading" class="loading">Cargando...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="tasks.length === 0" class="empty">
      No tienes tasks asignadas
    </div>
    
    <div v-else class="tasks-grid">
      <div 
        v-for="task in tasks" 
        :key="task.task_id"
        class="task-card"
        :class="`state-${task.state.toLowerCase()}`"
      >
        <h3>{{ task.task_name }}</h3>
        <p>{{ task.description }}</p>
        <div class="task-info">
          <span class="state">{{ task.state }}</span>
          <span class="value">{{ task.labor_formatted }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  props: {
    token: String,
  },
  setup(props) {
    const tasks = ref([]);
    const loading = ref(true);
    const error = ref(null);

    onMounted(async () => {
      try {
        const response = await fetch('/api/tasks/me', {
          headers: {
            'Authorization': `Bearer ${props.token}`,
          },
        });
        
        if (!response.ok) throw new Error('Error fetching tasks');
        
        const data = await response.json();
        tasks.value = data.tasks;
      } catch (err) {
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    });

    return { tasks, loading, error };
  },
};
</script>

<style scoped>
.task-container {
  padding: 1.5rem;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.task-card {
  background: white;
  border-left: 4px solid;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.task-card.state-assigned { border-left-color: #3b82f6; }
.task-card.state-in_progress { border-left-color: #f97316; }
.task-card.state-finished { border-left-color: #22c55e; }
</style>
```

---

##  Puntos Clave de Integracion

1. **Token Management:** Siempre pasar el token en el header `Authorization: Bearer TOKEN`
2. **Error Handling:** Capturar 401 (token expirado) para redirigir a login
3. **Loading States:** Mostrar estados de carga para mejor UX
4. **Polling:** Actualizar tasks cada 30-60 segundos
5. **Caching:** Implementar cache en el client si es necesario
6. **Real-time:** Considerar WebSockets para actualizaciones en tiempo real

---

##  Documentacion Relacionada

- `/docs/TASK_ENDPOINTS_GUIDE.md` - Guia tecnica de endpoints
- `/TASK_ENDPOINTS_QUICK_REF.md` - Reference rapida
- `/test_task_endpoints.py` - Ejemplos de prueba backend

---

**Fecha:** 7 de noviembre de 2025 OK
