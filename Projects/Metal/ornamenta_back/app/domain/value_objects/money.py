from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Money(BaseModel):
    """Value object para representar dinero."""
    amount: Decimal = Field(..., ge=0, description="Quantity de dinero (mayor o igual a cero)")
    currency: str = Field(default="COP", description="Codigo de moneda (ISO 4217)")

    @field_validator("amount", mode="before")
    def normalize_amount(cls, v):
        # Convierte y redondea a dos decimales
        return Decimal(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def __str__(self) -> str:
        # Formatea con separadores de miles y dos decimales
        return f"${self.amount:,.2f} {self.currency}"

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {other.currency} from {self.currency}")
        return Money(amount=self.amount - other.amount, currency=self.currency)
    
    def multiply(self, factor: Decimal) -> "Money":
        return Money(
            amount=(self.amount * factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            currency=self.currency
        )
    
    def is_positive(self) -> bool:
        return self.amount > 0
    
    def is_zero(self) -> bool:
        return self.amount == 0

    def __eq__(self, other) -> bool:
        return isinstance(other, Money) and self.amount == other.amount and self.currency == other.currency

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))
