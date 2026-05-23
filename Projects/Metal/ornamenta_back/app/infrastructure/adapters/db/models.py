"""
Legacy file for backwards compatibility.
All models have been moved to the models/ directory.
This file re-exports them for any code still importing from here.
"""
from app.infrastructure.adapters.db.models.user_model import User
from app.infrastructure.adapters.db.models.role_model import Role
from app.infrastructure.adapters.db.models.unit_of_measure_model import UnitOfMeasureModel
from app.infrastructure.adapters.db.models.material_type_model import MaterialTypeModel
from app.infrastructure.adapters.db.models.composition_model import CompositionModel
from app.infrastructure.adapters.db.models.payroll_model import PayrollModel
from app.infrastructure.adapters.db.models.payroll_history_model import PayrollHistoryModel

__all__ = [
    "User",
    "Role",
    "UnitOfMeasureModel",
    "MaterialTypeModel",
    "CompositionModel",
    "PayrollModel",
    "PayrollHistoryModel"
]
