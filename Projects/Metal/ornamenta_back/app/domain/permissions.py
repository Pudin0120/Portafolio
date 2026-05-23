from enum import Enum


class Permission(str, Enum):
    """Permisos disponibles en el sistema."""

    VIEW_TASKS = "VIEW_TASKS"
    APPROVE_TASKS = "APPROVE_TASKS"
    MANAGE_USERS = "MANAGE_USERS"
    CREATE_TASKS = "CREATE_TASKS"
    EDIT_TASKS = "EDIT_TASKS"
    DELETE_TASKS = "DELETE_TASKS"
    CREATE_MANAGER = "CREATE_MANAGER"
    CREATE_SUPERVISOR = "CREATE_SUPERVISOR"
    CREATE_EMPLOYEE = "CREATE_EMPLOYEE"


# Mapeo de roles a permisos
ROLE_PERMISSIONS = {
    "EMPLOYEE": [
        Permission.VIEW_TASKS,
        Permission.CREATE_TASKS,
    ],
    "SUPERVISOR": [
        Permission.VIEW_TASKS,
        Permission.CREATE_TASKS,
        Permission.EDIT_TASKS,
        Permission.APPROVE_TASKS,
    ],
    "MANAGER": [
        Permission.VIEW_TASKS,
        Permission.CREATE_TASKS,
        Permission.EDIT_TASKS,
        Permission.APPROVE_TASKS,
        Permission.DELETE_TASKS,
        Permission.CREATE_MANAGER,
        Permission.CREATE_SUPERVISOR,
        Permission.CREATE_EMPLOYEE,
    ],
    "SUPER_ADMIN": [
        Permission.VIEW_TASKS,
        Permission.CREATE_TASKS,
        Permission.EDIT_TASKS,
        Permission.APPROVE_TASKS,
        Permission.DELETE_TASKS,
        Permission.MANAGE_USERS,
        Permission.CREATE_MANAGER,
    ],
}

