"""
Servicio de aplicacion para creation de products.

Este servicio maneja la creation de products (simples y compuestos)
con validacion de roles, normalizacion de dimensiones con pint,
y validacion de estrategias de measurement.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
from app.application.mappers.product_mapper import ProductMapper
from app.domain.models.material import Material
from app.domain.models.product import SimpleProduct, CompositeProduct, ProductComponent
from app.domain.models.user import User
from app.domain.models.price_calculation_audit import PriceCalculationAudit
from app.domain.value_objects.money import Money
from app.domain.builders.product_builder import ProductBuilder
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.price_calculation_audit_repository import PriceCalculationAuditRepository
from app.domain.strategies.strategy_registry import MeasurementStrategyRegistry
from app.domain.repositories.unit_of_measure_repository import UnitOfMeasureRepository
from app.config import settings


class ProductCreationService:
    """
    Servicio de aplicacion para create products (simples y compuestos).
    
    Este servicio:
    1. Valida que el user tenga rol MANAGER (para operaciones administrativas)
    2. Normaliza dimensiones con pint (conversion a SI estandar)
    3. Valida dimensiones segun la estrategia de measurement del material
    4. Construye el product usando ProductBuilder
    5. Calcula price inicial segun material actual
    6. Genera registro de auditoria del calculo
    7. Persiste el product
    
    IMPORTANTE: Solo MANAGER puede:
    - Create products (operacion administrativa)
    - Establecer price_override
    
    Example JSON Request (para docstring de endpoint):
        POST /api/products/simple
        {
            "material_id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Lamina cortada 1x2",
            "description": "Corte personalizado para puerta",
            "dimensions": {
                "width": {"value": 1.0, "unit": "m"},
                "length": {"value": 2.0, "unit": "m"}
            },
            "price_override": null
        }
        
        Headers:
        Authorization: Bearer <token>
        (El token debe contener info del user con rol MANAGER)
    
    Example JSON Response:
        {
            "success": true,
            "product": {
                "id": "prod-0001",
                "name": "Lamina cortada 1x2",
                "product_type": "simple",
                "material": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Lamina acero cal 14",
                    "price_amount": 100000.0
                },
                "dimensions": {
                    "width": 1.0,
                    "height": 2.0
                },
                "computed_quantity": {
                    "value": 2.0,
                    "unit": "m2"
                },
                "price": {
                    "amount": 200000.0,
                    "currency": "COP"
                },
                "audit": {
                    "calculation_id": "calc-00001",
                    "calculated_at": "2025-10-25T10:30:00Z"
                }
            }
        }
    """
    
    def __init__(
        self,
        material_repository: MaterialRepository,
        product_repository: ProductRepository,
        unit_repository: UnitOfMeasureRepository,
        audit_repository: Optional[PriceCalculationAuditRepository] = None
    ):
        """
        Inicializa el servicio con repositorios necesarios.
        
        Args:
            material_repository: Repositorio para Material
            product_repository: Repositorio para Product
            unit_repository: Repositorio para UnitOfMeasure (necesario para estrategias)
            audit_repository: Repositorio opcional para auditoria de precios
        """
        self.material_repo = material_repository
        self.product_repo = product_repository
        self.unit_repo = unit_repository
        self.audit_repo = audit_repository
        self.strategy_registry = MeasurementStrategyRegistry(unit_repository)
    
    def create_simple_product_from_material(
        self,
        dimensions: Dict[str, Any],
        user: User,
        material_id: Optional[uuid.UUID] = None,
        materials: Optional[List[Dict[str, Any]]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price_override: Optional[Money] = None,
        image_url: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crea un SimpleProduct a partir de uno o varios materials.
        """
        self._validate_manager_role(user, "create products")
        
        if price_override is not None:
            self._validate_manager_role(user, "establecer price_override")
        
        # Si no hay dimensiones globales pero si en el primer material, las usamos como fallback
        # Esto hace la API mas amigable cuando el product es basicamente un material procesado.
        if not dimensions and materials and materials[0].get("dimensions"):
            dimensions = materials[0]["dimensions"]

        builder = ProductBuilder()
        builder.with_dimensions_dict(dimensions)
        
        # 1. Resolver materials a agregar
        recipe_to_audit = []
        tenant_id = user.tenant_id if hasattr(user, 'tenant_id') else None
        
        # Backward compatibility para material_id unico
        if material_id:
            material = self.material_repo.get_by_id(material_id, tenant_id=tenant_id)
            if not material: raise ValueError(f"Material {material_id} not found")
            builder.with_material(material)
            recipe_to_audit.append(material)
        
        # Soporte para receta completa
        if materials:
            for m_req in materials:
                m_id = m_req["material_id"]
                material = self.material_repo.get_by_id(m_id, tenant_id=tenant_id)
                if not material: raise ValueError(f"Material {m_id} not found")
                
                builder.with_material(
                    material, 
                    dimensions=m_req.get("dimensions"),
                    quantity=m_req.get("quantity")
                )
                recipe_to_audit.append(material)

        if name: builder.with_name(name)
        if description: builder.with_description(description)
        if price_override: builder.with_price_override(price_override)
        if image_url: builder.with_image_url(image_url)
        if properties: builder.with_properties(properties)
        
        try:
            product = builder.build()
        except ValueError as e:
            raise ValueError(f"Error building product: {str(e)}")
        
        self._validate_product_dimensions_and_price(product)
        
        existing_product = self.product_repo.get_by_name(product.name)
        if existing_product:
            raise ValueError(f"Product with name '{product.name}' already exists")
        
        # Save y retornar
        saved_product = self.product_repo.save(product)
        
        # Auditoria detallada de la receta
        recipe_details = []
        for pm in product.materials:
            recipe_details.append({
                "material_id": str(pm.material.id),
                "material_name": pm.material.full_name,
                "quantity": float(pm.quantity),
                "dimensions": pm.dimensions,
                "price_at_calculation": float(pm.material.purchase_price.amount) if pm.material.purchase_price else 0.0,
                "currency": pm.material.purchase_price.currency if pm.material.purchase_price else "COP"
            })

        primary_material = recipe_to_audit[0] if recipe_to_audit else None
        
        tenant_id = saved_product.tenant_id or user.tenant_id
        if not tenant_id:
            raise ValueError("Tenant ID is required for price calculation audit")

        total_price = saved_product.get_total_sale_price()
        audit = PriceCalculationAudit(
            calculation_id=f"calc-{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            product_id=saved_product.id,
            product_name=saved_product.name,
            calculated_at=datetime.now(),
            calculation_type="INITIAL_CREATION",
            material_id=primary_material.id if primary_material else None,
            material_name=primary_material.full_name if primary_material else None,
            material_price_amount=primary_material.purchase_price.amount if primary_material and primary_material.purchase_price else None,
            material_price_currency=primary_material.purchase_price.currency if primary_material and primary_material.purchase_price else "COP",
            dimensions=product.dimensions,
            computed_quantity=Decimal(str(product.materials[0].quantity)) if product.materials else Decimal("1"),
            quantity_unit=self._get_quantity_unit(primary_material) if primary_material else "unit",
            recipe_details=recipe_details,
            calculated_price_amount=total_price.amount if total_price else Decimal("0"),
            calculated_price_currency=total_price.currency if total_price else "COP",
            triggered_by_user_id=user.id if hasattr(user, "id") else None,
            notes=f"Product creado por {user.full_name} ({user.role})"
        )

        if self.audit_repo:
            self.audit_repo.save(audit)

        return {
            "success": True,
            "product": ProductMapper.to_dto(saved_product),
            "audit": audit.to_dict()
        }

    
    def create_simple_product_without_material(
        self,
        name: str,
        price: Money,
        user: User,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crea un SimpleProduct sin material (ej: servicio).
        
        Este tipo de product tiene un price fijo que no depende de ningun material.
        Util para servicios, mano de obra, etc.
        
        Args:
            name: Nombre del product/servicio
            price: Price fijo del product
            user: User que ejecuta la operacion (debe ser MANAGER)
            description: Description opcional
            image_url: URL opcional de imagen en Firebase
            properties: Properties adicionales opcionales
        
        Returns:
            Diccionario con el product creado
        
        Raises:
            PermissionError: Si el user no es MANAGER
            ValueError: Si los datos son invalids
        
        Example JSON Request:
            POST /api/products/service
            {
                "name": "Instalacion de porton",
                "description": "Servicio de instalacion profesional incluye transporte",
                "price": {
                    "amount": 500000.0,
                    "currency": "COP"
                }
            }
        """
        # 1. VALIDAR ROL MANAGER
        self._validate_manager_role(user, "create products/servicios")
        
        # 2. VALIDAR DATOS
        if not name or not name.strip():
            raise ValueError("El nombre del product es obligatorio")
        
        if not price or price.amount < 0:
            raise ValueError("El price debe ser mayor o igual a cero")
        
        # 3. CONSTRUIR PRODUCTO
        builder = ProductBuilder()
        builder.with_name(name)
        if user.tenant_id:
            builder.with_tenant_id(user.tenant_id)
        
        if description:
            builder.with_description(description)
        
        if image_url:
            builder.with_image_url(image_url)
        
        if properties:
            builder.with_properties(properties)
        
        product = (builder
                   .with_sale_price(price)
                   .build())
        
        # 4. PERSISTIR PRODUCTO
        saved_product = self.product_repo.save(product)
        
        # 5. CREAR REGISTRO DE AUDITORIA
        calc_id = f"calc-{uuid.uuid4().hex[:8]}"
        audit_tenant_id = saved_product.tenant_id or user.tenant_id
        if not audit_tenant_id:
            raise ValueError("Tenant ID is required for price calculation audit")
            
        audit = PriceCalculationAudit(
            calculation_id=calc_id,
            tenant_id=audit_tenant_id,
            product_id=saved_product.id,
            product_name=saved_product.name,
            calculated_at=datetime.now(),
            calculation_type="INITIAL_CREATION",
            calculated_price_amount=price.amount,
            calculated_price_currency=price.currency,
            triggered_by_user_id=user.id if hasattr(user, "id") else None,
            notes=f"Product sin material (servicio) creado por {user.full_name} ({user.role})"
        )
        
        if self.audit_repo:
            self.audit_repo.save(audit)
        
        # 6. RETORNAR RESULTADO
        return {
            "success": True,
            "product": ProductMapper.to_dto(saved_product),
            "audit": audit.to_dict()
        }
    
    def _validate_manager_role(self, user: User, operation: str) -> None:
        """
        Valida que el user tenga rol MANAGER o SUPER_ADMIN.
        
        Args:
            user: User a validar
            operation: Description de la operacion para mensaje de error
        
        Raises:
            PermissionError: Si el user no tiene permisos
        """
        if not hasattr(user, 'role') or not user.role:
            raise PermissionError("User sin rol asignado")
        
        allowed_roles = ["MANAGER", "SUPER_ADMIN"]
        # Handle both RoleEnum and string role
        user_role = user.role.value if hasattr(user.role, 'value') else user.role
        if user_role not in allowed_roles:
            raise PermissionError(
                f"Solo users con rol {' o '.join(allowed_roles)} pueden {operation}. "
                f"Rol actual: {user_role}"
            )
    
    def _get_quantity_unit(self, material: Material) -> str:
        """
        Determina la unidad de quantity segun la estrategia del material.
        
        Args:
            material: Material del cual extraer la unidad
        
        Returns:
            String con la unidad (m2, m3, kg, L, etc.)
        """
        strategy = material.get_measurement_type()
        unit_map = {
            "SHEET": "m2",
            "PROFILE": "m",
            "LIQUID": "L",
            "SOLID": "kg",
            "SIMPLE": "unit"
        }
        return unit_map.get(strategy, "unit")
    
    def _validate_product_dimensions_and_price(self, product: SimpleProduct) -> None:
        """
        Valida las dimensiones y el price del product construido.
        
        Validaciones:
        - Cada dimension debe estar entre product_min_dimension y product_max_dimension
        - El price total debe ser al menos product_min_price
        - Para LABOR y LIQUID, las validaciones son mas flexibles ya que manejan servicios o volumenes
        
        Args:
            product: Product a validar
        
        Raises:
            ValueError: Si las dimensiones o el price son invalids
        """
        from app.domain.units import ureg
        
        if not product.dimensions:
            raise ValueError("Las dimensiones del product no pueden ser vacias.")
        
        min_dim = settings.product_min_dimension or Decimal("0.01")
        max_dim = settings.product_max_dimension or Decimal("100.0")
        min_price = settings.product_min_price or Decimal("100")
        
        # Obtener el tipo de measurement
        measurement_type = None
        if isinstance(product, SimpleProduct) and product.materials:
            measurement_type = product.materials[0].material.get_measurement_type()
        
        # Validar cada dimension usando el valor normalizado (SI)
        # Accedemos a las dimensiones del product que vienen del builder.
        # PERO: SimpleProduct.dimensions guarda las dimensiones ORIGINALES (con unidades).
        # Necesitamos validar contra los valores NORMALIZADOS que el Builder uso.
        # Como el servicio llama al Builder, y el Builder normaliza, pero SimpleProduct guarda el dict original,
        # debemos re-normalizar aqui o cambiar como el builder entrega la data.
        
        # Sin embargo, para no romper el modelo, vamos a normalizar cada valor de product.dimensions
        # a metros (o unidad SI) antes de comparar contra max_dim.

        global_unit = product.dimensions.get("unit", "m")
        
        for dim_name, dim_value in product.dimensions.items():
            # SALTAR validacion para campos que no son dimensiones
            if dim_name in ["mode", "unit"]:
                continue
                
            # Convertir a metros (SI) para validacion
            try:
                if isinstance(dim_value, dict):
                    val = dim_value.get("value", 0)
                    u = str(dim_value.get("unit", global_unit))
                    dim_numeric = float((float(val) * ureg(u)).to('m').magnitude)
                    unit_label = "m"
                else:
                    # Si es valor simple, asumimos metros o la unidad global
                    dim_numeric = float((float(dim_value) * ureg(str(global_unit))).to('m').magnitude)
                    unit_label = "m"
            except (ValueError, TypeError, Exception):
                # Si falla Pint (ej: unidades de masa en dimensiones de longitud), 
                # fallback al valor numerico directo pero esto ya deberia estar validado por el builder
                try:
                    if isinstance(dim_value, dict):
                        dim_numeric = float(dim_value["value"])
                    else:
                        dim_numeric = float(dim_value)
                    unit_label = "m"
                except:
                    continue
            
            # Para LABOR y LIQUID, permitimos dimensiones mas pequenas
            if measurement_type not in ["LABOR", "LIQUID"]:
                if Decimal(str(dim_numeric)) < min_dim:
                    raise ValueError(
                        f"La dimension '{dim_name}' ({dim_numeric}m) es menor que el minimo permitido ({min_dim}m). "
                        f"Minimo: {min_dim}m ({min_dim * 100:.0f}cm)"
                    )
            elif measurement_type == "LIQUID" and dim_numeric <= 0:
                raise ValueError(f"El volumen debe ser mayor a 0, se recibio: {dim_numeric}L")
            
            # Para LIQUID, validar max en litros
            if measurement_type == "LIQUID":
                # Re-normalizar a litros para esta validacion especifica
                try:
                    if isinstance(dim_value, dict):
                        u_str = str(dim_value["unit"])
                        l_val = float((float(dim_value["value"]) * ureg(u_str)).to('L').magnitude)
                    else:
                        l_val = float((float(dim_value) * ureg(str(global_unit))).to('L').magnitude)
                    
                    if Decimal(str(l_val)) > Decimal("1000"):
                        raise ValueError(
                            f"La dimension '{dim_name}' ({l_val}L) excede el maximo permitido (1000L). "
                            f"Maximo: 1000L"
                        )
                except:
                    pass
            elif Decimal(str(dim_numeric)) > max_dim:
                raise ValueError(
                    f"La dimension '{dim_name}' ({dim_numeric}m) excede el maximo permitido ({max_dim}m). "
                    f"Maximo: {max_dim}m"
                )
        
        # Validar price
        total_price = product.get_total_price()
        if not total_price or total_price.amount <= 0:
            raise ValueError("El price total del product debe ser mayor a cero.")
        
        if total_price.amount < min_price:
            raise ValueError(
                f"El price total del product ({total_price.amount} {total_price.currency}) "
                f"es menor que el minimo permitido ({min_price} {total_price.currency}). "
                f"Aumenta las dimensiones o el price del material."
            )


# INTEGRATION HOOK: Para usar este servicio desde un endpoint FastAPI:
#
# @router.post("/products/simple")
# async def create_simple_product(
#     request: SimpleProductCreateRequest,  # Pydantic model con material_id, dimensions, etc.
#     current_user: User = Depends(get_current_user),
#     service: ProductCreationService = Depends(get_product_creation_service)
# ):
#     try:
#         result = service.create_simple_product_from_material(
#             material_id=request.material_id,
#             dimensions=request.dimensions,
#             user=current_user,
#             name=request.name,
#             description=request.description,
#             price_override=request.price_override
#         )
#         return JSONResponse(content=result, status_code=201)
#     except PermissionError as e:
#         raise HTTPException(status_code=403, detail=str(e))
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

