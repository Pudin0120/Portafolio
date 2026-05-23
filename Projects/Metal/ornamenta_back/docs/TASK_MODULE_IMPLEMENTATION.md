# Modulo de Tasks - Documentacion

## Resumen

Se ha creado un modulo completo de gestion de tasks que se integra con el sistema de payroll existente. Este modulo permite:

- Create y gestionar tasks vinculadas a works
- Asignar tasks a empleados especificos
- Seguir el progreso de las tasks con estados
- Calcular automaticamente los valores de payroll basados en tasks completadas
- Integrar con contratos de prestacion de servicios

## Arquitectura

El modulo sigue la arquitectura hexagonal (Clean Architecture) del proyecto:

### Capa de Dominio

#### Value Objects
- **StateTask**: Maneja los estados de las tasks (S=SIN_INICIAR, P=EN_PROCESO, F=FINALIZADA)

#### Modelos de Dominio
- **Task**: Representa una task con sus properties basicas y logica de negocio
- **TaskAssignment**: Representa la asignacion de una task a un empleado con fechas y valores

#### Eventos de Dominio
- **TaskAssigned**: Se dispara cuando una task es asignada
- **TaskCompleted**: Se dispara cuando una task es completada
- **TaskStateChanged**: Se dispara cuando cambia el estado de una task
- **TaskDelivered**: Se dispara cuando una task asignada es entregada

#### Repositorios
- **TaskRepository**: Interfaz para operaciones CRUD de tasks
- **TaskAssignmentRepository**: Interfaz para operaciones CRUD de asignaciones

### Capa de Aplicacion

#### DTOs
- **TaskDTO**: Para respuestas de tasks
- **TaskCreateDTO**: Para creation de tasks
- **TaskUpdateDTO**: Para actualizacion de tasks
- **TaskAssignmentDTO**: Para respuestas de asignaciones
- **TaskAssignmentCreateDTO**: Para creation de asignaciones

#### Mappers
- **TaskMapper**: Convierte entre modelos de dominio y DTOs de tasks
- **TaskAssignmentMapper**: Convierte entre modelos de dominio y DTOs de asignaciones

#### Casos de Uso
- **CreateTask**: Create nuevas tasks
- **GetTask**: Obtener task por ID
- **UpdateTask**: Actualizar tasks existentes
- **AssignTask**: Asignar tasks a users
- **ChangeTaskState**: Cambiar estado de tasks
- **FinishTask**: Finalizar tasks
- **CreateTaskAssignment**: Create asignaciones de tasks
- **DeliverTaskAssignment**: Marcar tasks como entregadas
- **CalculatePayrollFromTasks**: Calcular payroll basada en tasks completadas

### Capa de Infraestructura

#### Endpoints REST
- **TaskRouter**: Endpoints para gestion de tasks (`/tasks`)
- **TaskAssignmentRouter**: Endpoints para gestion de asignaciones (`/task-assignments`)
- **PayrollRouter**: Endpoints adicionales para integracion con payroll

## Funcionalidades Principales

### Gestion de Tasks

1. **Create Task**
   - POST `/tasks/`
   - Requiere: work_id, task_name, description, labor_amount, estimated_value_amount

2. **Obtener Task**
   - GET `/tasks/{task_id}`
   - Retorna information completa de la task

3. **Actualizar Task**
   - PUT `/tasks/{task_id}`
   - Permite actualizar nombre, description y valores

4. **Asignar Task**
   - POST `/tasks/{task_id}/assign`
   - Asigna la task a un user especifico

5. **Cambiar Estado**
   - POST `/tasks/{task_id}/change-state`
   - Cambia el estado de la task (S/P/F)

6. **Finalizar Task**
   - POST `/tasks/{task_id}/finish`
   - Marca la task como finalizada

### Gestion de Asignaciones

1. **Create Asignacion**
   - POST `/task-assignments/`
   - Crea una asignacion de task a empleado

2. **Entregar Task**
   - POST `/task-assignments/task/{task_id}/deliver`
   - Marca la task como entregada con fecha

3. **Obtener Asignaciones por Payroll**
   - GET `/task-assignments/payroll/{payroll_id}`
   - Retorna todas las asignaciones de una payroll

4. **Resumen de Empleado**
   - GET `/task-assignments/employee/{identification_number}/summary`
   - Estadisticas de asignaciones del empleado

### Integracion con Payroll

1. **Calcular Payroll desde Tasks**
   - POST `/payrolls/{payroll_id}/calculate-from-tasks`
   - Calcula valores de payroll basados en tasks completadas

2. **Resumen de Tasks por Payroll**
   - GET `/payrolls/{payroll_id}/task-summary`
   - Estadisticas de tasks para una payroll

3. **Actualizar Payroll por Task**
   - POST `/payrolls/{payroll_id}/update-from-task/{task_id}`
   - Actualiza payroll cuando se completa una task

## Estados de Tasks

- **S (SIN_INICIAR)**: Task creada pero no asignada
- **P (EN_PROCESO)**: Task assigned y en progreso
- **F (FINALIZADA)**: Task completada

## Flujo de Work

1. **Creation**: Se crea una task vinculada a un work
2. **Asignacion**: Se asigna la task a un empleado especifico
3. **Progreso**: El empleado trabaja en la task (estado EN_PROCESO)
4. **Entrega**: Se marca la task como entregada con fecha
5. **Finalizacion**: Se marca la task como finalizada
6. **Calculo**: Se calcula el valor de payroll basado en tasks completadas

## Integracion con Contracts

- **Contracts de Service Provision**: Solo reciben valor de tasks (sin salario base)
- **Contracts Fijos e Indefinidos**: Reciben salario base + valor de tasks
- **Calculo Automatico**: Los valores se calculan automaticamente cuando se completan tasks

## Validaciones de Negocio

- Las tasks deben tener valores positivos
- Solo se pueden asignar tasks no asignadas
- Solo se pueden finalizar tasks en proceso
- Las fechas de entrega no pueden ser anteriores a la fecha de asignacion
- Los contratos de prestacion de servicios no pueden tener salario base

## Eventos de Dominio

El sistema genera eventos automaticamente para:
- Auditoria de cambios de estado
- Integracion con otros modulos
- Notificaciones
- Seguimiento de progreso

## Consideraciones Tecnicas

- Todos los endpoints requieren autenticacion
- Se siguen las convenciones de naming del proyecto
- Se utiliza dependency injection para los repositorios
- Se manejan errores con HTTPException apropiadas
- Se incluye logging para auditoria
- Se validan permisos de user segun roles

## Proximos Pasos

Para completar la implementacion se requiere:

1. **Implementar Repositorios**: Create las implementaciones SQLAlchemy de TaskRepository y TaskAssignmentRepository
2. **Configurar Container**: Agregar los nuevos repositorios al contenedor de dependencias
3. **Registrar Routers**: Agregar los nuevos routers a la aplicacion principal
4. **Create Tablas**: Generar migraciones para las nuevas tablas de base de datos
5. **Tests**: Create tests unitarios e integracion para el modulo
6. **Documentacion API**: Generar documentacion OpenAPI/Swagger

El modulo esta disenado para ser completamente funcional una vez implementadas las capas de infraestructura faltantes.
