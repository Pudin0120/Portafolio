"""
PostgreSQL implementation of PayrollRepository.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func

from app.domain.models.Payroll import Payroll
from app.domain.repositories.payroll_repository import PayrollRepository
from app.domain.value_objects.contract_type import ContractType, ContractTypeEnum
from app.domain.value_objects.state_payroll import StatePayroll, StatePayrollEnum
from app.domain.value_objects.money import Money
from app.infrastructure.adapters.db.models.payroll_model import PayrollModel
from app.infrastructure.adapters.repositories.payroll_history_repository import PostgresPayrollHistoryRepository
from app.infrastructure.adapters.db.models.payroll_history_model import PayrollHistoryModel
from sqlalchemy import select
from sqlalchemy.orm import aliased


class PostgresPayrollRepository(PayrollRepository):
    """
    PostgreSQL implementation of PayrollRepository using SQLAlchemy.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_by_id(self, payroll_id: UUID) -> Optional[Payroll]:
        """Get payroll by UUID, eager loading the histories."""
        stmt = (
            select(PayrollModel)
            .options(joinedload(PayrollModel.histories)) 
            .where(PayrollModel.id == payroll_id)
        )
        model = self.db_session.execute(stmt).unique().scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    def get_all(self) -> List[Payroll]:
        """Get all payrolls."""
        try:
            stmt = (
                select(PayrollModel)
                .options(joinedload(PayrollModel.histories)) # Asegura que los histories se carguen
                .order_by(PayrollModel.created_at.desc())
            )
            # Usar .unique() ayuda a evitar duplicados si el JOIN genera filas repetidas
            models = self.db_session.execute(stmt).scalars().unique().all() 
            
            return [self._to_domain(model) for model in models]
        except Exception:
            self.db_session.rollback()
            raise
    
    def get_by_contract_type(self, contract_type: ContractTypeEnum) -> List[Payroll]:
        """Get payrolls by contract type, eager loading the histories."""
        try:
            stmt = (
                select(PayrollModel)
                .options(joinedload(PayrollModel.histories)) # Agregado aqui tambien
                .where(PayrollModel.contract_type == contract_type.value)
                .order_by(PayrollModel.created_at.desc())
            )
            models = self.db_session.execute(stmt).scalars().unique().all()
            return [self._to_domain(model) for model in models]
        except Exception:
            self.db_session.rollback()
            raise
    
    def get_by_state(self, state: StatePayrollEnum) -> List[Payroll]:
        """Get payrolls by state, eager loading the histories."""
        try:
            stmt = (
                select(PayrollModel)
                .options(joinedload(PayrollModel.histories)) #  AGREGADO
                .where(PayrollModel.state == state.value)
                .order_by(PayrollModel.created_at.desc())
            )
            # Usar .unique() por precaucion despues del joinedload
            models = self.db_session.execute(stmt).scalars().unique().all() 
            return [self._to_domain(model) for model in models]
        except Exception:
            self.db_session.rollback()
            raise
    
    def get_by_contract_type_and_state(
        self, 
        contract_type: ContractTypeEnum, 
        state: StatePayrollEnum
    ) -> List[Payroll]:
        """Get payrolls by contract type and state, eager loading the histories."""
        try:
            stmt = (
                select(PayrollModel)
                .options(joinedload(PayrollModel.histories)) #  AGREGADO
                .where(
                    PayrollModel.contract_type == contract_type.value,
                    PayrollModel.state == state.value
                )
                .order_by(PayrollModel.created_at.desc())
            )
            models = self.db_session.execute(stmt).scalars().unique().all()
            return [self._to_domain(model) for model in models]
        except Exception:
            self.db_session.rollback()
            raise
    
    def get_liquidated_payrolls(self) -> List[Payroll]:
        """Get all liquidated payrolls."""
        return self.get_by_state(StatePayrollEnum.LIQUIDATED)
    
    def get_active_payrolls(self) -> List[Payroll]:
        """Get all active payrolls."""
        return self.get_by_state(StatePayrollEnum.ACTIVE)
    
    def get_paid_payrolls(self) -> List[Payroll]:
        """Get all paid payrolls."""
        return self.get_by_state(StatePayrollEnum.PAID)
    
    def get_cancelled_payrolls(self) -> List[Payroll]:
        """Get all cancelled payrolls."""
        return self.get_by_state(StatePayrollEnum.CANCELLED)
    
    def get_fixed_term_payrolls(self) -> List[Payroll]:
        """Get all fixed term contract payrolls."""
        return self.get_by_contract_type(ContractTypeEnum.FIXED_TERM)
    
    def get_indefinite_term_payrolls(self) -> List[Payroll]:
        """Get all indefinite term contract payrolls."""
        return self.get_by_contract_type(ContractTypeEnum.INDEFINITE_TERM)
    
    def get_service_provision_payrolls(self) -> List[Payroll]:
        """Get all service provision contract payrolls."""
        return self.get_by_contract_type(ContractTypeEnum.SERVICE_PROVISION)
    
    def save(self, payroll: Payroll) -> Payroll:
        model = self._to_model(payroll)
        
        if payroll.payroll_id:
            merged_model = self.db_session.merge(model)
        else:
            self.db_session.add(model)
            merged_model = model
        
        self.db_session.commit()  #  Commit para persistir los cambios
        self.db_session.refresh(merged_model)
        
        return self._to_domain(merged_model)
    
    def delete(self, payroll_id: UUID) -> bool:
        """
        Delete a payroll by ID.
        
        NOTE: Does NOT commit - relies on get_db_session() to commit at end of request.
        """
        stmt = select(PayrollModel).where(PayrollModel.id == payroll_id)
        model = self.db_session.execute(stmt).scalar_one_or_none()
        if model:
            self.db_session.delete(model)
            self.db_session.flush()  # Flush to validate constraints
            return True
        return False
    
    def exists(self, payroll_id: UUID) -> bool:
        """Check if a payroll exists by ID."""
        stmt = select(func.count(PayrollModel.id)).where(PayrollModel.id == payroll_id)
        count = self.db_session.execute(stmt).scalar() or 0
        return count > 0
    
    def count(self) -> int:
        """Get total count of payrolls."""
        stmt = select(func.count(PayrollModel.id))
        return self.db_session.execute(stmt).scalar() or 0
    
    def count_by_state(self, state: StatePayrollEnum) -> int:
        """Get count of payrolls by state."""
        stmt = select(func.count(PayrollModel.id)).where(PayrollModel.state == state.value)
        return self.db_session.execute(stmt).scalar() or 0
    
    def count_by_contract_type(self, contract_type: ContractTypeEnum) -> int:
        """Get count of payrolls by contract type."""
        stmt = select(func.count(PayrollModel.id)).where(PayrollModel.contract_type == contract_type.value)
        return self.db_session.execute(stmt).scalar() or 0

    def get_all_with_identification(self) -> List[tuple[Payroll, Optional[str]]]:
        
        subq = select(
            PayrollHistoryModel.payroll_id,
            PayrollHistoryModel.identification_number
        ).distinct(
            PayrollHistoryModel.payroll_id
        ).order_by(
            PayrollHistoryModel.payroll_id,
            PayrollHistoryModel.created_at.desc()
        ).subquery()
        
        # JOIN con la subquery
        stmt = select(
            PayrollModel,
            subq.c.identification_number
        ).outerjoin(
            subq, PayrollModel.id == subq.c.payroll_id
        ).order_by(PayrollModel.created_at.desc())
        
        results = self.db_session.execute(stmt).all()
        
        return [
            (self._to_domain(payroll_model), identification_number)
            for payroll_model, identification_number in results
        ]
    
    @staticmethod
    def _to_domain(model: PayrollModel) -> Payroll:
        """Convert SQLAlchemy model to domain entity, including eager-loaded relations."""
        try:
            # Validar y manejar valores nulos o invalids
            contract_type_value = model.contract_type if model.contract_type is not None else ContractTypeEnum.FIXED_TERM.value
            state_value = model.state if model.state is not None else StatePayrollEnum.ACTIVE.value
            base_salary_amount = model.base_salary_amount if model.base_salary_amount is not None else 0
            
            domain_payroll = Payroll(
                payroll_id=UUID(str(model.id)),
                contract_type=ContractType(value=ContractTypeEnum(contract_type_value)),
                state=StatePayroll(value=StatePayrollEnum(state_value)),
                base_salary=Money(amount=Decimal(str(base_salary_amount)))
            )
            
            #  CAMBIO CLAVE: Cargar y anexar la relacion 'histories' al dominio
            # Usamos getattr() para verificar si 'histories' existe en el modelo (viene del joinedload)
            if hasattr(model, 'histories') and model.histories is not None:
                
                # Convertimos cada modelo de historial a su entidad de dominio
                domain_histories = [
                    PostgresPayrollHistoryRepository._to_domain(h_model) 
                    for h_model in model.histories
                ]
                
                # Asignamos la lista de objetos de dominio de historial al objeto de dominio Payroll.
                # (REQUIERE que tu clase de dominio 'Payroll' tenga un atributo asignable llamado 'histories')
                domain_payroll.histories = domain_histories
                
            return domain_payroll
            
        except Exception as e:
            print(f"Error converting payroll model to domain: {e}, model.id: {model.id}")
            # Considera re-elevar la excepcion en un formato mas especifico (ej. RepositoryError)
            raise
    
    @staticmethod
    def _to_model(payroll: Payroll) -> PayrollModel:
        """Convert domain entity to SQLAlchemy model."""
        return PayrollModel(
            id=payroll.payroll_id,
            contract_type=payroll.contract_type.value.value,
            state=payroll.state.value.value,
            base_salary_amount=float(payroll.base_salary.amount),
        )
