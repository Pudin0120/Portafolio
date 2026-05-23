"""
Use case for managing tasks.
"""
from typing import List, Optional
from uuid import UUID

from app.application.dto.task_dto import (
    TaskCreateDTO, 
    TaskDTO, 
    TaskUpdateDTO,
    TaskAssignDTO,
    TaskStateChangeDTO,
    TaskListDTO,
    TaskSummaryDTO
)
from app.domain.models.task import Task
from app.domain.models.user import User
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.work_repository import WorkRepository
from app.application.mappers.task_mapper import TaskMapper
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class GetTask:
    """Use case for getting a task by ID."""
    
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
    
    def execute(self, task_id: UUID) -> TaskDTO:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            TaskDTO of the task
            
        Raises:
            HTTPException: If task not found
        """
        logger.info(f"Getting task {task_id}")
        
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La task especificada no existe"
            )
        
        return TaskMapper.to_dto(task)


class GetTasksByWork:
    """Use case for getting tasks by work ID."""
    
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
    
    def execute(self, work_id: UUID) -> TaskListDTO:
        """
        Get all tasks for a specific work.
        
        Args:
            work_id: Work ID
            
        Returns:
            TaskListDTO with list of tasks
            
        Raises:
            HTTPException: If retrieval fails
        """
        logger.info(f"Getting tasks for work {work_id}")
        
        try:
            tasks = self.task_repository.get_by_work_id(work_id)
            return TaskMapper.to_dto_list(tasks)
        except Exception as e:
            logger.error(f"Error getting tasks by work: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al obtener las tasks"
            )


class GetTaskSummary:
    """Use case for getting task summary for a work."""
    
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
    
    def execute(self, work_id: UUID) -> TaskSummaryDTO:
        """
        Get task summary for a work.
        
        Args:
            work_id: Work ID
            
        Returns:
            TaskSummaryDTO with task statistics
            
        Raises:
            HTTPException: If retrieval fails
        """
        logger.info(f"Getting task summary for work {work_id}")
        
        try:
            tasks = self.task_repository.get_by_work_id(work_id)
            return TaskMapper.to_summary_dto(tasks, work_id)
        except Exception as e:
            logger.error(f"Error getting task summary: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al obtener el resumen de tasks"
            )


class UpdateTask:
    """Use case for updating a task."""
    
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
    
    def execute(self, task_id: UUID, update_dto: TaskUpdateDTO, current_user: Optional[User] = None) -> TaskDTO:
        """
        Update a task.
        
        Args:
            task_id: Task ID to update
            update_dto: Update data
            current_user: User updating the task (for audit purposes)
            
        Returns:
            TaskDTO of the updated task
            
        Raises:
            HTTPException: If update fails
        """
        logger.info(f"Updating task {task_id}")
        
        try:
            # Get existing task
            task = self.task_repository.get_by_id(task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="La task especificada no existe"
                )
            
            # Apply updates
            updated_task = TaskMapper.apply_update_dto(task, update_dto)
            
            # Save updated task
            saved_task = self.task_repository.save(updated_task)
            
            logger.info(f"Task updated successfully: {saved_task.task_id}")
            
            # Convert to DTO and return
            return TaskMapper.to_dto(saved_task)
            
        except ValueError as e:
            logger.error(f"Validation error updating task: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al actualizar la task"
            )


class AssignTask:
    """Use case for assigning a task to a user."""
    
    def __init__(self, task_repository: TaskRepository, user_repository: UserRepository):
        self.task_repository = task_repository
        self.user_repository = user_repository
    
    def execute(self, task_id: UUID, assign_dto: TaskAssignDTO, current_user: Optional[User] = None) -> TaskDTO:
        """
        Assign a task to a user.
        
        Args:
            task_id: Task ID to assign
            assign_dto: Assignment data
            current_user: User assigning the task (for audit purposes)
            
        Returns:
            TaskDTO of the updated task
            
        Raises:
            HTTPException: If assignment fails
        """
        logger.info(f"Assigning task {task_id} to user {assign_dto.user_id}")
        
        try:
            # Get existing task
            task = self.task_repository.get_by_id(task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="La task especificada no existe"
                )
            
            # Get user to assign - try to find by firebase_uid
            user_to_assign = None
            try:
                # El assign_dto.user_id es el firebase_uid (string)
                user_to_assign = self.user_repository.get_by_firebase_uid(str(assign_dto.user_id))
            except Exception as e:
                logger.error(f"Error getting user by firebase_uid: {e}")
            
            if not user_to_assign:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User con ID {assign_dto.user_id} no encontrado"
                )
            
            # Assign task to user
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Se requiere user autenticado para asignar tasks"
                )
            
            task.assign_to(user_to_assign, current_user)
            
            # Save updated task
            saved_task = self.task_repository.save(task)
            
            logger.info(f"Task assigned successfully: {saved_task.task_id}")
            
            # Convert to DTO and return
            return TaskMapper.to_dto(saved_task)
            
        except ValueError as e:
            logger.error(f"Validation error assigning task: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error assigning task: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al asignar la task"
            )


class ChangeTaskState:
    """Use case for changing task state."""
    
    def __init__(self, task_repository: TaskRepository, work_repository: Optional[WorkRepository] = None):
        self.task_repository = task_repository
        self.work_repository = work_repository
    
    def execute(self, task_id: UUID, state_change_dto: TaskStateChangeDTO, current_user: Optional[User] = None) -> TaskDTO:
        """
        Change task state.
        
        When a task transitions to COMPLETED or FINISHED state, automatically unblocks 
        the next task in the sequence if there is one.
        
        Args:
            task_id: Task ID to update
            state_change_dto: State change data
            current_user: User changing the state (for audit purposes)
            
        Returns:
            TaskDTO of the updated task
            
        Raises:
            HTTPException: If state change fails
        """
        logger.info(f"Changing state of task {task_id} to {state_change_dto.new_state}")
        
        try:
            # Get existing task
            task = self.task_repository.get_by_id(task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="La task especificada no existe"
                )
            
            # Parse new state
            new_state = TaskMapper.parse_state(state_change_dto.new_state)
            
            # Change state
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Se requiere user autenticado para cambiar el estado de la task"
                )
            
            task.change_state(new_state, current_user, state_change_dto.reason or "")
            
            # Save updated task
            saved_task = self.task_repository.save(task)
            
            # Auto-unlock next task if this task was completed/finished and work_repository is available
            self._unlock_next_task_if_needed(saved_task)
            
            logger.info(f"Task state changed successfully: {saved_task.task_id}")
            
            # Convert to DTO and return
            return TaskMapper.to_dto(saved_task)
            
        except ValueError as e:
            logger.error(f"Validation error changing task state: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error changing task state: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al cambiar el estado de la task"
            )
    
    def _unlock_next_task_if_needed(self, task: Task) -> None:
        """
        Helper method to unlock the next task in sequence if this one is completed/finished.
        
        Args:
            task: The task that was just completed/finished
        """
        # Only proceed if task is completed or finished, and we have a work repository
        if not self.work_repository:
            logger.debug(f"Work repository not available, skipping auto-unlock for task {task.task_id}")
            return
        
        if not (task.is_completed or task.is_finished):
            return
        
        try:
            # Get the work containing this task
            work = self.work_repository.get_by_id(task.work_id)
            if not work:
                logger.warning(f"Work {task.work_id} not found for task {task.task_id}, cannot unlock next task")
                return
            
            # Unlock the next task in sequence
            next_task = work.unblock_next_task(task)
            if next_task:
                # Save the unlocked task
                self.task_repository.save(next_task)
                logger.info(f"Auto-unlocked next task {next_task.task_id} after task {task.task_id} was completed")
            else:
                logger.debug(f"No next task to unlock after task {task.task_id}")
        
        except Exception as e:
            logger.error(f"Error auto-unlocking next task after {task.task_id}: {e}")
            # Don't raise - this is a side effect and shouldn't fail the main operation


class FinishTask:
    """Use case for finishing a task."""
    
    def __init__(self, task_repository: TaskRepository, work_repository: Optional[WorkRepository] = None):
        self.task_repository = task_repository
        self.work_repository = work_repository
    
    def execute(self, task_id: UUID, current_user: Optional[User] = None) -> TaskDTO:
        """
        Finish a task and automatically unlock the next task in sequence.
        
        When a task is finished, if it was blocking the next task, the next task
        is automatically unlocked (ASSIGNED  READY) and the employee is notified.
        
        Args:
            task_id: Task ID to finish
            current_user: User finishing the task (for audit purposes)
            
        Returns:
            TaskDTO of the updated task
            
        Raises:
            HTTPException: If finishing fails
        """
        logger.info(f"Finishing task {task_id}")
        
        try:
            # Get existing task
            task = self.task_repository.get_by_id(task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="La task especificada no existe"
                )
            
            # Finish task
            task.finish()
            
            # Save updated task
            saved_task = self.task_repository.save(task)
            
            # Auto-unlock next task
            self._unlock_next_task_if_needed(saved_task)
            
            logger.info(f"Task finished successfully: {saved_task.task_id}")
            
            # Convert to DTO and return
            return TaskMapper.to_dto(saved_task)
            
        except ValueError as e:
            logger.error(f"Validation error finishing task: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error finishing task: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al finalizar la task"
            )
    
    def _unlock_next_task_if_needed(self, task: Task) -> None:
        """
        Helper method to unlock the next task in sequence after this one is finished.
        
        Args:
            task: The task that was just finished
        """
        # Only proceed if we have a work repository
        if not self.work_repository:
            logger.debug(f"Work repository not available, skipping auto-unlock for task {task.task_id}")
            return
        
        try:
            # Get the work containing this task
            work = self.work_repository.get_by_id(task.work_id)
            if not work:
                logger.warning(f"Work {task.work_id} not found for task {task.task_id}, cannot unlock next task")
                return
            
            # Unlock the next task in sequence
            next_task = work.unblock_next_task(task)
            if next_task:
                # Save the unlocked task
                self.task_repository.save(next_task)
                logger.info(f"Auto-unlocked next task {next_task.task_id} after task {task.task_id} was finished")
            else:
                logger.debug(f"No next task to unlock after task {task.task_id}")
        
        except Exception as e:
            logger.error(f"Error auto-unlocking next task after {task.task_id}: {e}")
            # Don't raise - this is a side effect and shouldn't fail the main operation


class CompleteTask:
    """Use case for completing a task."""
    
    def __init__(self, task_repository: TaskRepository, work_repository: Optional[WorkRepository] = None):
        self.task_repository = task_repository
        self.work_repository = work_repository
    
    def execute(self, task_id: UUID, current_user: Optional[User] = None) -> TaskDTO:
        """
        Complete a task (mark it as done, pending validation for EMPLOYEE).
        
        When a task is completed (COMPLETED or FINISHED state), the next blocked 
        task is automatically unlocked, allowing work to continue without waiting 
        for validation.
        
        Args:
            task_id: Task ID to complete
            current_user: User completing the task
            
        Returns:
            TaskDTO of the updated task
            
        Raises:
            HTTPException: If completion fails
        """
        logger.info(f"Completing task {task_id}")
        
        try:
            # Get existing task
            task = self.task_repository.get_by_id(task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="La task especificada no existe"
                )
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Se requiere user autenticado para completar la task"
                )
            
            # Complete task
            task.complete(completed_by=current_user)
            
            # Save updated task
            saved_task = self.task_repository.save(task)
            
            # Auto-unlock next task if this task is completed or finished
            # This allows next task to start even if current task needs validation
            if saved_task.is_completed or saved_task.is_finished:
                self._unlock_next_task_if_needed(saved_task)
            
            logger.info(f"Task completed successfully: {saved_task.task_id}")
            
            return TaskMapper.to_dto(saved_task)
            
        except ValueError as e:
            logger.error(f"Validation error completing task: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al completar la task"
            )
    
    def _unlock_next_task_if_needed(self, task: Task) -> None:
        """
        Helper method to unlock the next task in sequence after this one is completed or finished.
        
        Now triggers on COMPLETED state, not just FINISHED, allowing work to continue
        even if the completed task needs validation.
        
        Args:
            task: The task that was just completed or finished
        """
        if not self.work_repository:
            logger.debug(f"Work repository not available, skipping auto-unlock for task {task.task_id}")
            return
        
        try:
            work = self.work_repository.get_by_id(task.work_id)
            if not work:
                logger.warning(f"Work {task.work_id} not found for task {task.task_id}")
                return
            
            next_task = work.unblock_next_task(task)
            if next_task:
                self.task_repository.save(next_task)
                logger.info(f"Auto-unlocked next task {next_task.task_id} after task {task.task_id} was completed")
        
        except Exception as e:
            logger.error(f"Error auto-unlocking next task: {e}")


class ValidateTask:
    """Use case for validating a completed task."""
    
    def __init__(self, task_repository: TaskRepository, work_repository: Optional[WorkRepository] = None):
        self.task_repository = task_repository
        self.work_repository = work_repository
    
    def execute(self, task_id: UUID, current_user: Optional[User] = None) -> TaskDTO:
        """
        Validate a completed task (COMPLETED  FINISHED).
        
        Automatically unlocks the next task in the sequence.
        
        Args:
            task_id: Task ID to validate
            current_user: User validating the task (must be SUPERVISOR or MANAGER)
            
        Returns:
            TaskDTO of the updated task
            
        Raises:
            HTTPException: If validation fails
        """
        logger.info(f"Validating task {task_id}")
        
        try:
            # Get existing task
            task = self.task_repository.get_by_id(task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="La task especificada no existe"
                )
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Se requiere user autenticado para validar la task"
                )
            
            # Validate task
            task.validate(validated_by=current_user)
            
            # Save updated task
            saved_task = self.task_repository.save(task)
            
            # Auto-unlock next task
            self._unlock_next_task_if_needed(saved_task)
            
            logger.info(f"Task validated successfully: {saved_task.task_id}")
            
            return TaskMapper.to_dto(saved_task)
            
        except ValueError as e:
            logger.error(f"Validation error validating task: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating task: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al validar la task"
            )
    
    def _unlock_next_task_if_needed(self, task: Task) -> None:
        """
        Helper method to unlock the next task in sequence after this one is validated/finished.
        
        Args:
            task: The task that was just validated/finished
        """
        if not self.work_repository:
            logger.debug(f"Work repository not available, skipping auto-unlock for task {task.task_id}")
            return
        
        try:
            work = self.work_repository.get_by_id(task.work_id)
            if not work:
                logger.warning(f"Work {task.work_id} not found for task {task.task_id}")
                return
            
            next_task = work.unblock_next_task(task)
            if next_task:
                self.task_repository.save(next_task)
                logger.info(f"Auto-unlocked next task {next_task.task_id} after task {task.task_id} was validated")
        
        except Exception as e:
            logger.error(f"Error auto-unlocking next task: {e}")
