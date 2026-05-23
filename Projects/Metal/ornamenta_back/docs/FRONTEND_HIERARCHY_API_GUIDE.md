# Guia de API para Frontend: Jerarquia de Products y Tasks

##  Tabla de Contenidos

1. [Products en Quotation (Work)](#products-en-quotation-work)
2. [Tasks con Jerarquia](#tasks-con-jerarquia)
3. [Ejemplos Completos de Flujo](#ejemplos-completos-de-flujo)

---

##  Products en Quotation (Work)

### 1. Agregar Product a un Work

**Endpoint:** `POST /works/{work_id}/products`

**Estados permitidos:** DRAFT, QUOTED

```javascript
// Agregar un product simple
async function addProductToWork(workId, productId, quantity) {
  const response = await fetch(`/api/works/${workId}/products`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      product_id: productId,
      quantity: quantity,
      execution_order: null  // null = se agrega al final
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}

// Ejemplo de uso
const productItem = await addProductToWork(
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',  // work_id
  '550e8400-e29b-41d4-a716-446655440000',  // product_id
  2                                         // quantity
);

console.log(productItem);
// {
//   "product_id": "550e8400-e29b-41d4-a716-446655440000",
//   "work_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
//   "product_name": "Puerta Metalica",
//   "quantity": 2,
//   "execution_order": 0,
//   "state": "PENDING",
//   "snapshot": null,  // En DRAFT no hay snapshot
//   "current_price": {
//     "amount": 350000,
//     "currency": "COP",
//     "formatted": "$350,000"
//   }
// }
```

---

### 2. Reordenar Products en un Work

**Endpoint:** `PATCH /works/{work_id}/products/{product_id}/order?new_order={order}`

**Estados permitidos:** DRAFT, QUOTED

```javascript
// Reordenar un product (cambiar orden de ejecucion)
async function reorderProduct(workId, productId, newOrder) {
  const response = await fetch(
    `/api/works/${workId}/products/${productId}/order?new_order=${newOrder}`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  // Retorna 204 No Content (exito sin body)
  return true;
}

// Ejemplo: Mover product a la primera posicion
await reorderProduct(
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',  // work_id
  '550e8400-e29b-41d4-a716-446655440000',  // product_id
  0                                         // new_order (primera posicion)
);
```

---

### 3. Obtener Work Completo con Products Ordenados

**Endpoint:** `GET /works/{work_id}`

```javascript
async function getWorkWithProducts(workId) {
  const response = await fetch(`/api/works/${workId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) throw new Error('Error al obtener work');
  
  return await response.json();
}

// Ejemplo de uso
const work = await getWorkWithProducts('f47ac10b-58cc-4372-a567-0e02b2c3d479');

console.log(work);
// {
//   "work_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
//   "work_name": "Instalacion de puertas",
//   "state": "DRAFT",
//   "tax": 0.15,
//   "products": [
//     {
//       "product_id": "...",
//       "product_name": "Marco de Acero",
//       "execution_order": 0,  //  Orden de ejecucion
//       "quantity": 2,
//       "current_price": { "amount": 50000, ... }
//     },
//     {
//       "product_id": "...",
//       "product_name": "Puerta Metalica",
//       "execution_order": 1,
//       "quantity": 1,
//       "current_price": { "amount": 350000, ... }
//     }
//   ],
//   "products_value": 450000,
//   "work_value": 517500,
//   "tasks": []  // Vacio en DRAFT
// }
```

---

##  Tasks con Jerarquia

###  IMPORTANTE: Cuando aparece `parent_composite_id`

El campo `parent_composite_id` **solo aparece** cuando:

1. OK Agregaste un **Product Compuesto** al work (no products simples individuales)
2. OK El work esta en estado **IN_PROGRESS** (las tasks ya fueron generadas)
3. OK Las tasks se generaron automaticamente al llamar `POST /works/{work_id}/start`

**Ejemplo de lo que NO genera jerarquia:**
```javascript
// ERROR MAL: Agregar componentes por separado
await addProductToWork(workId, 'product-marco-id', 1);      // Task sin parent
await addProductToWork(workId, 'product-vidrio-id', 1);     // Task sin parent  
await addProductToWork(workId, 'product-bisagras-id', 1);   // Task sin parent
```

**Ejemplo correcto para generar jerarquia:**
```javascript
// OK BIEN: Create product compuesto primero
// 1. Create CompositeProduct "Ventana" en el catalogo (POST /products/)
const ventana = await createCompositeProduct({
  name: "Ventana Completa",
  components: [
    { product_id: "marco-id", quantity: 1 },
    { product_id: "vidrio-id", quantity: 1 },
    { product_id: "bisagras-id", quantity: 2 }
  ]
});

// 2. Agregar el product compuesto al work
await addProductToWork(workId, ventana.product_id, 1);

// 3. Iniciar el work
await startWork(workId);

// 4. Ahora si tendras tasks con parent_composite_id = ventana.product_id
```

---

### 1. Obtener Tasks con Jerarquia Agrupada

**Endpoint:** `GET /works/{work_id}/tasks/hierarchy`

**Estados disponibles:** IN_PROGRESS, DELIVERED

```javascript
async function getTasksHierarchy(workId) {
  const response = await fetch(`/api/works/${workId}/tasks/hierarchy`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) throw new Error('Error al obtener tasks');
  
  return await response.json();
}

// Ejemplo de uso
const hierarchy = await getTasksHierarchy('f47ac10b-58cc-4372-a567-0e02b2c3d479');

console.log(hierarchy);

//  CASO 1: Solo products simples (sin jerarquia)
// Si agregaste products simples por separado, veras UN SOLO GRUPO con composite_id=null
// {
//   "work_id": "...",
//   "total_tasks": 6,
//   "composite_groups": [
//     {
//       "composite_id": null,  //  Todas son standalone
//       "composite_name": null,
//       "start_execution_order": 0,
//       "end_execution_order": 5,
//       "tasks": [
//         { "task_id": "...", "task_name": "Marco", "parent_composite_id": null, ... },
//         { "task_id": "...", "task_name": "Vidrio", "parent_composite_id": null, ... },
//         { "task_id": "...", "task_name": "Pintura", "parent_composite_id": null, ... }
//       ]
//     }
//   ]
// }

//  CASO 2: Con products compuestos (CON jerarquia)
// Si agregaste un CompositeProduct, veras MULTIPLES GRUPOS
// {
//   "work_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
//   "total_tasks": 5,
//   "composite_groups": [
//     {
//       "composite_id": null,  // null = task standalone
//       "composite_name": null,
//       "start_execution_order": 0,
//       "end_execution_order": 0,
//       "tasks": [
//         {
//           "task_id": "...",
//           "task_name": "Marco de Acero",
//           "execution_order": 0,
//           "parent_composite_id": null,  // No pertenece a compuesto
//           "composite_task_slot": null,
//           "composite_total_slots": null,
//           "is_blocked": false,
//           "state": "S"
//         }
//       ]
//     },
//     {
//       "composite_id": "550e8400-e29b-41d4-a716-446655440000",
//       "composite_name": "Puerta Metalica",
//       "start_execution_order": 1,
//       "end_execution_order": 3,
//       "tasks": [
//         {
//           "task_id": "...",
//           "task_name": "Marco (x1)",
//           "execution_order": 1,
//           "parent_composite_id": "550e8400-e29b-41d4-a716-446655440000",
//           "composite_task_slot": 0,  // Primera task del compuesto
//           "composite_total_slots": 3,
//           "is_blocked": false,
//           "state": "S"
//         },
//         {
//           "task_id": "...",
//           "task_name": "Lamina (x1)",
//           "execution_order": 2,
//           "parent_composite_id": "550e8400-e29b-41d4-a716-446655440000",
//           "composite_task_slot": 1,  // Segunda task del compuesto
//           "composite_total_slots": 3,
//           "is_blocked": true,
//           "previous_task_id": "...",
//           "state": "S"
//         },
//         {
//           "task_id": "...",
//           "task_name": "Bisagras (x2)",
//           "execution_order": 3,
//           "parent_composite_id": "550e8400-e29b-41d4-a716-446655440000",
//           "composite_task_slot": 2,  // Tercera task del compuesto
//           "composite_total_slots": 3,
//           "is_blocked": true,
//           "previous_task_id": "...",
//           "state": "S"
//         }
//       ]
//     }
//   ]
// }
```

---

### 2. Obtener Informacion de Jerarquia de una Task

**Endpoint:** `GET /works/{work_id}/tasks/{task_id}/hierarchy`

```javascript
async function getTaskHierarchyInfo(workId, taskId) {
  const response = await fetch(
    `/api/works/${workId}/tasks/${taskId}/hierarchy`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  if (!response.ok) throw new Error('Error al obtener info de task');
  
  return await response.json();
}

// Ejemplo de uso
const taskInfo = await getTaskHierarchyInfo(
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',  // work_id
  '6ba7b810-9dad-11d1-80b4-00c04fd430c8'   // task_id
);

console.log(taskInfo);
// {
//   "task": {
//     "task_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
//     "task_name": "Lamina (x1)",
//     "execution_order": 2,
//     "parent_composite_id": "550e8400-e29b-41d4-a716-446655440000",
//     "composite_task_slot": 1,
//     "composite_total_slots": 3,
//     "is_blocked": true,
//     "state": "S"
//   },
//   "parent_composite_id": "550e8400-e29b-41d4-a716-446655440000",
//   "current_slot": 1,
//   "total_slots": 3,
//   "valid_execution_orders": [2],  // Solo puede estar en posicion 2
//   "can_be_reordered": false,      // No se puede mover (solo 1 posicion valid)
//   "sibling_task_ids": [
//     "...",  // ID de task "Marco"
//     "..."   // ID de task "Bisagras"
//   ]
// }
```

---

### 3. Reordenar Task (con Validacion de Jerarquia)

**Endpoint:** `PATCH /works/{work_id}/tasks/{task_id}/reorder`

** Restricciones:**
- Tasks **standalone** (sin `parent_composite_id`): pueden ir a cualquier posicion
- Tasks de **compuesto**: solo pueden moverse dentro del rango `[start, end]` del compuesto
- El slot interno NO puede cambiar (la posicion relativa se mantiene)

```javascript
async function reorderTask(workId, taskId, newExecutionOrder) {
  const response = await fetch(
    `/api/works/${workId}/tasks/${taskId}/reorder`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        new_execution_order: newExecutionOrder
      })
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  // Retorna 204 No Content (exito)
  return true;
}

// Ejemplo: Reordenar task standalone (exitoso)
await reorderTask(
  'f47ac10b-58cc-4372-a567-0e02b2c3d479',  // work_id
  'task-standalone-id',                     // task_id
  3                                         // new_execution_order
);

// Ejemplo: Reordenar task de compuesto fuera de rango (FALLA)
try {
  await reorderTask(
    'f47ac10b-58cc-4372-a567-0e02b2c3d479',
    'task-composite-id',  // Task del compuesto en rango [1, 3]
    0                     // Intentar mover a posicion 0 (fuera del rango)
  );
} catch (error) {
  console.error(error.message);
  // "No se puede reordenar task: La task no puede moverse fuera 
  //  del rango del compuesto [1, 3]. Orden solicitado: 0"
}
```

---

### 4. Obtener Lista Simple de Tasks (sin jerarquia)

**Endpoint:** `GET /works/{work_id}/tasks`

```javascript
async function getWorkTasks(workId) {
  const response = await fetch(`/api/works/${workId}/tasks`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) throw new Error('Error al obtener tasks');
  
  return await response.json();
}

// Ejemplo de uso
const tasksResponse = await getWorkTasks('f47ac10b-58cc-4372-a567-0e02b2c3d479');

console.log(tasksResponse);
// {
//   "tasks": [
//     {
//       "task_id": "...",
//       "task_name": "Marco de Acero",
//       "execution_order": 0,
//       "parent_composite_id": null,
//       "state": "S",
//       "labor_amount": 50000,
//       "labor_formatted": "$50,000",
//       "is_assigned": false
//     },
//     {
//       "task_id": "...",
//       "task_name": "Marco (x1)",
//       "execution_order": 1,
//       "parent_composite_id": "550e8400-...",
//       "composite_task_slot": 0,
//       "composite_total_slots": 3,
//       "state": "S",
//       "labor_amount": 50000,
//       "is_assigned": false
//     }
//     // ... mas tasks
//   ],
//   "total_count": 5
// }
```

---

##  Ejemplos Completos de Flujo

### Flujo 1: Create Work y Reordenar Products

```javascript
// 1. Create work
async function createWorkFlow() {
  // Create work en DRAFT
  const work = await fetch('/api/works/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      client_identification: '1002309888',
      work_name: 'Instalacion de puertas',
      description: 'Work completo de puertas',
      tax: 0.15,
      deposit_amount: 200000
    })
  }).then(r => r.json());
  
  console.log('Work created:', work.work_id);
  
  // 2. Agregar products
  const product1 = await addProductToWork(work.work_id, 'product-marco-id', 1);
  const product2 = await addProductToWork(work.work_id, 'product-puerta-id', 2);
  const product3 = await addProductToWork(work.work_id, 'product-bisagra-id', 4);
  
  console.log('Products agregados en orden:', [
    product1.execution_order,  // 0
    product2.execution_order,  // 1
    product3.execution_order   // 2
  ]);
  
  // 3. Reordenar: Mover "Bisagra" a la primera posicion
  await reorderProduct(work.work_id, product3.product_id, 0);
  
  // 4. Obtener work actualizado
  const updatedWork = await getWorkWithProducts(work.work_id);
  
  console.log('Nuevo orden de products:');
  updatedWork.products.forEach(p => {
    console.log(`${p.execution_order}: ${p.product_name}`);
  });
  // 0: Bisagras
  // 1: Marco de Acero
  // 2: Puerta Metalica
  
  return work.work_id;
}
```

---

### Flujo 2: Visualizar y Reordenar Tasks con Jerarquia

```javascript
async function taskHierarchyFlow(workId) {
  // 1. Obtener jerarquia de tasks
  const hierarchy = await getTasksHierarchy(workId);
  
  // 2. Renderizar grupos
  hierarchy.composite_groups.forEach(group => {
    if (group.composite_id) {
      console.log(` Product Compuesto: ${group.composite_name}`);
      console.log(`   Rango: [${group.start_execution_order}, ${group.end_execution_order}]`);
    } else {
      console.log(` Tasks Independientes`);
    }
    
    group.tasks.forEach(task => {
      const indent = task.parent_composite_id ? '   ' : '  ';
      const slotInfo = task.composite_task_slot !== null 
        ? ` (slot ${task.composite_task_slot}/${task.composite_total_slots})`
        : '';
      
      console.log(`${indent}${task.execution_order}. ${task.task_name}${slotInfo}`);
    });
  });
  
  // Salida:
  //  Tasks Independientes
  //   0. Marco de Acero
  //  Product Compuesto: Puerta Metalica
  //    Rango: [1, 3]
  //    1. Marco (x1) (slot 0/3)
  //    2. Lamina (x1) (slot 1/3)
  //    3. Bisagras (x2) (slot 2/3)
  //  Tasks Independientes
  //   4. Acabado
  
  // 3. Intentar reordenar task standalone (OK)
  const standaloneTask = hierarchy.composite_groups
    .find(g => !g.composite_id)?.tasks[0];
  
  if (standaloneTask) {
    await reorderTask(workId, standaloneTask.task_id, 4);
    console.log('OK Task standalone reordenada a posicion 4');
  }
  
  // 4. Intentar reordenar task de compuesto fuera de rango (FALLA)
  const compositeTask = hierarchy.composite_groups
    .find(g => g.composite_id)?.tasks[1];  // Lamina (order=2, slot=1)
  
  if (compositeTask) {
    // Verificar posiciones valid primero
    const info = await getTaskHierarchyInfo(workId, compositeTask.task_id);
    console.log('Posiciones valid:', info.valid_execution_orders);  // [2]
    
    try {
      await reorderTask(workId, compositeTask.task_id, 0);
    } catch (error) {
      console.error('ERROR Error esperado:', error.message);
      // "No se puede reordenar task: La task no puede moverse fuera del rango..."
    }
  }
}
```

---

### Flujo 3: UI para Drag & Drop con Validacion

```javascript
// Componente React (ejemplo)
function TaskList({ workId }) {
  const [hierarchy, setHierarchy] = useState(null);
  const [draggedTask, setDraggedTask] = useState(null);
  
  useEffect(() => {
    getTasksHierarchy(workId).then(setHierarchy);
  }, [workId]);
  
  const handleDragStart = (task) => {
    setDraggedTask(task);
  };
  
  const handleDrop = async (targetOrder) => {
    if (!draggedTask) return;
    
    // Verificar si el movimiento es valid
    const info = await getTaskHierarchyInfo(workId, draggedTask.task_id);
    
    if (!info.valid_execution_orders.includes(targetOrder)) {
      alert(
        `No puedes mover esta task a la posicion ${targetOrder}.\n` +
        `Posiciones valid: ${info.valid_execution_orders.join(', ')}`
      );
      return;
    }
    
    try {
      await reorderTask(workId, draggedTask.task_id, targetOrder);
      
      // Recargar jerarquia
      const updated = await getTasksHierarchy(workId);
      setHierarchy(updated);
      
      alert('OK Task reordenada exitosamente');
    } catch (error) {
      alert(`ERROR Error: ${error.message}`);
    }
    
    setDraggedTask(null);
  };
  
  return (
    <div>
      {hierarchy?.composite_groups.map(group => (
        <div key={group.composite_id || 'standalone'}>
          <h3>
            {group.composite_name 
              ? ` ${group.composite_name}` 
              : ' Tasks Independientes'}
          </h3>
          
          {group.tasks.map(task => (
            <div
              key={task.task_id}
              draggable={task.parent_composite_id === null}
              onDragStart={() => handleDragStart(task)}
              onDrop={() => handleDrop(task.execution_order)}
              onDragOver={(e) => e.preventDefault()}
              style={{
                padding: '10px',
                margin: '5px',
                border: '1px solid #ccc',
                backgroundColor: task.parent_composite_id ? '#f0f0f0' : 'white',
                cursor: task.parent_composite_id ? 'not-allowed' : 'move'
              }}
            >
              <strong>{task.execution_order}.</strong> {task.task_name}
              {task.composite_task_slot !== null && (
                <span style={{ color: '#666', fontSize: '0.9em' }}>
                  {' '}(Posicion {task.composite_task_slot + 1}/{task.composite_total_slots})
                </span>
              )}
              {task.parent_composite_id && (
                <span style={{ color: 'red', fontSize: '0.8em' }}>
                  {' '} No reordenable
                </span>
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
```

---

##  Resumen de Estados y Permisos

| Accion | DRAFT | QUOTED | IN_PROGRESS | DELIVERED |
|--------|-------|--------|-------------|-----------|
| Agregar product | OK | OK | ERROR | ERROR |
| Delete product | OK | OK | ERROR | ERROR |
| Reordenar product | OK | OK | ERROR | ERROR |
| Ver tasks | ERROR | ERROR | OK | OK |
| Reordenar task | ERROR | ERROR | OK | ERROR |

---

##  Reglas de Negocio Importantes

### Products:
1. OK Se pueden agregar/delete en DRAFT y QUOTED
2. OK Se pueden reordenar libremente en DRAFT y QUOTED
3. ERROR NO se pueden modificar en IN_PROGRESS o DELIVERED

### Tasks:
1. OK Solo existen en IN_PROGRESS y DELIVERED
2. OK Tasks **standalone** (sin compuesto) pueden ir a cualquier posicion
3.  Tasks de **product compuesto**:
   - Solo pueden moverse dentro del rango `[start, end]` del compuesto
   - El slot interno (posicion relativa) NO puede cambiar
   - Ejemplo: Si una task es slot 1/3, siempre debe ser la segunda del grupo

### Validacion en Frontend:
```javascript
function canReorderTask(task, newOrder, allTasks) {
  if (!task.parent_composite_id) {
    // Standalone: puede ir a cualquier posicion
    return newOrder >= 0 && newOrder < allTasks.length;
  }
  
  // Composite: debe estar dentro del rango del compuesto
  const compositeGroup = findCompositeGroup(task.parent_composite_id, allTasks);
  return newOrder >= compositeGroup.start_execution_order &&
         newOrder <= compositeGroup.end_execution_order &&
         (newOrder - compositeGroup.start_execution_order) === task.composite_task_slot;
}
```

---

##  Conclusion

Esta implementacion garantiza que:
- OK Los products se pueden reordenar libremente en DRAFT/QUOTED
- OK Las tasks mantienen la integridad de los products compuestos
- OK No se puede romper la secuencia logica de un product compuesto
- OK El frontend recibe information clara sobre que movimientos son valids
