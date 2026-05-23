"""
Use case for creating a new task.
"""
from typing import Optional
from uuid import UUID, uuid4

from app.application.dto.task_dto import TaskCreateDTO, TaskDTO
from app.domain.models.task import Task
from app.domain.models.user import User
from app.domain.repositories.task_repository import TaskRepository
from app.application.mappers.task_mapper import TaskMapper
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class CreateTask:
    """Use case for creating a new task."""
    
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
    
    def execute(self, create_dto: TaskCreateDTO, current_user: Optional[User] = None) -> TaskDTO:
        """
        Create a new task.
        
        Args:
            create_dto: Task creation data
            current_user: User creating the task (for audit purposes)
            
        Returns:
            TaskDTO of the created task
            
        Raises:
            HTTPException: If task creation fails
        """
        logger.info(f"Creating new task: {create_dto.task_name} for work {create_dto.work_id}")
        
        try:
            # Generate new task ID
            task_id = uuid4()
            
            # Convert DTO to domain entity
            task = TaskMapper.from_create_dto(create_dto, task_id)
            
            # Save task
            saved_task = self.task_repository.save(task)
            
            logger.info(f"Task created successfully: {saved_task.task_id}")
            
            # Convert to DTO and return
            return TaskMapper.to_dto(saved_task)
            
        except ValueError as e:
            logger.error(f"Validation error creating task: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor al create la task"
            )
