"""
DTOs for measurement strategies and their property schemas.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class PropertyFieldSchema(BaseModel):
    """Schema for a single property field."""
    name: str = Field(..., description="Property field name (e.g., 'thickness', 'diameter')")
    type: str = Field(..., description="Type of the field (e.g., 'Gauge', 'Measurement')")
    required: bool = Field(..., description="Whether this field is required")
    description: str = Field(..., description="Human-readable description")
    dimension: Optional[str] = Field(None, description="Physical dimension if applicable (e.g., 'length', 'area', 'volume')")
    unit_options: Optional[List[str]] = Field(None, description="Suggested units (e.g., ['mm', 'cm', 'm'])")
    gauge_range: Optional[Dict[str, int]] = Field(None, description="Valid gauge range if type is Gauge")
    example_value: Any = Field(None, description="Example value for this field")


class MeasurementStrategySchema(BaseModel):
    """Schema describing a measurement strategy and its required properties."""
    strategy_type: str = Field(..., description="Strategy identifier (SHEET, PROFILE, LIQUID, SOLID)")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Description of what this strategy is for")
    icon: str = Field(..., description="Icon or emoji representing this strategy")
    properties: List[PropertyFieldSchema] = Field(..., description="List of property fields")
    calculation_formula: str = Field(..., description="Formula used to calculate quantity")
    use_cases: List[str] = Field(..., description="Example use cases")


class CategoryWithStrategiesDTO(BaseModel):
    """Category with its available measurement strategies."""
    category: str = Field(..., description="Category name (e.g., 'Metal', 'Pintura')")
    strategies: List[MeasurementStrategySchema] = Field(..., description="Available strategies for this category")
    material_type_count: int = Field(..., description="Number of material types in this category")


class CategoriesResponseDTO(BaseModel):
    """Response containing all categories with their strategies."""
    categories: List[CategoryWithStrategiesDTO]
    total_categories: int
