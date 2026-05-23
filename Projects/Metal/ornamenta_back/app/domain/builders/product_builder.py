"""
Builder pattern para construccion controlada de products.

Este builder proporciona una interfaz fluida para create products SimpleProduct
con validacion completa de dimensiones, normalizacion de unidades con pint,
y validacion de estrategias de measurement.
"""
from decimal import Decimal
from typing import Dict, Any, Optional, List
import uuid

from app.domain.models.material import Material
from app.domain.models.product import SimpleProduct
from app.domain.value_objects.money import Money
from app.domain.strategies.measurement_strategy import MeasurementStrategy
from app.domain.units import ureg
from app.domain.value_objects.measurement import Measurement


class ProductBuilder:
    """
    Builder para create SimpleProduct con validacion y normalizacion completas.
    
    Este builder:
    1. Valida que las dimensiones sean compatibles con la estrategia del material
    2. Normaliza todas las unidades usando pint (convierte a SI estandar)
    3. Calcula el quantity_multiplier correcto segun la estrategia
    4. Valida restricciones de negocio (ej: solo manager puede hacer price_override)
    5. Genera nombres descriptivos si no se proporciona uno
    
    Example usage (docstring):
        >>> # Create product de lamina con dimensiones en metros
        >>> builder = ProductBuilder()
        >>> product = (builder
        ...     .with_material(steel_material)
        ...     .with_name("Lamina lateral puerta #123")
        ...     .with_dimensions_dict({
        ...         "width": 1.0,
        ...         "height": 2.5,
        ...         "unit": "m"
        ...     })
        ...     .with_strategy(sheet_strategy)
        ...     .build()
        ... )
        >>> product.get_total_price()  # Calcula automaticamente
        Money(amount=Decimal("125000"))
        
        >>> # Create product sin material (ej: servicio)
        >>> service = (ProductBuilder()
        ...     .with_name("Instalacion de porton")
        ...     .with_description("Servicio de instalacion profesional")
        ...     .with_price_override(Money(amount=Decimal("500000"), currency="COP"))
        ...     .build()
        ... )
    
     Example JSON de input para servicios de aplicacion:
        {
            "material_id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Lamina cortada 1x2",
            "description": "Corte personalizado",
            "dimensions": {
                "width": {"value": 1.0, "unit": "m"},
                "length": {"value": 2.0, "unit": "m"}
            },
            "price_override": null
        }
    """
    
    def __init__(self):
        """Inicializa un builder limpio."""
        self._id: uuid.UUID = uuid.uuid4()
        self._recipe_materials: List[Dict[str, Any]] = [] # List of {material: Material, dimensions: dict, quantity: Decimal}
        self._name: Optional[str] = None
        self._description: Optional[str] = None
        self._image_url: Optional[str] = None
        self._dimensions: Dict[str, Any] = {}
        self._normalized_dimensions: Dict[str, float] = {}
        self._original_dimensions: Dict[str, Any] = {}  # Dimensiones originales del user
        self._purchase_price: Optional[Money] = None
        self._sale_price: Optional[Money] = None
        self._properties: Dict[str, Any] = {}
        self._strategy: Optional[MeasurementStrategy] = None
    
    def with_id(self, product_id: uuid.UUID) -> "ProductBuilder":
        """Establece el ID del product (opcional, se genera automaticamente si no se proporciona)."""
        self._id = product_id
        return self

    def with_image_url(self, image_url: Optional[str]) -> "ProductBuilder":
        """Establece la URL de la imagen del product."""
        self._image_url = image_url
        return self
    
    def with_tenant_id(self, tenant_id: uuid.UUID) -> "ProductBuilder":
        """Establece el ID del tenant."""
        self._tenant_id = tenant_id
        return self
    
    def with_material(self, material: Material, dimensions: Optional[Dict[str, Any]] = None, quantity: Optional[Decimal] = None) -> "ProductBuilder":
        """
        Agrega un material a la receta del product.
        
        Args:
            material: Material de dominio
            dimensions: Dimensiones especificas para este material (opcional)
            quantity: Quantity explicita (opcional)
        
        Returns:
            Self para encadenamiento fluido
        """
        self._recipe_materials.append({
            "material": material,
            "dimensions": dimensions or self._dimensions,
            "quantity": quantity
        })
        
        if material.tenant_id and not hasattr(self, "_tenant_id"):
            self._tenant_id = material.tenant_id
        return self
    
    def with_name(self, name: str) -> "ProductBuilder":
        """Establece el nombre del product."""
        self._name = name
        return self
    
    def with_description(self, description: str) -> "ProductBuilder":
        """Establece la description del product."""
        self._description = description
        return self
    
    def with_dimensions_dict(self, dimensions: Dict[str, Any]) -> "ProductBuilder":
        """
        Establece las dimensiones del product a partir de un diccionario.
        
        El diccionario puede contener:
        - Para SHEET: width, height, area (con unit)
        - Para PROFILE: shape, length, width, height, diameter
        - Para LIQUID: volume (con unit)
        - Para SOLID: width, height, depth o mass (con unit)
        
        Args:
            dimensions: Diccionario con dimensiones y unidades
        
        Returns:
            Self para encadenamiento fluido
        """
        # Almacenar tambien las dimensiones originales para generacion de nombres y persistencia
        self._original_dimensions = dimensions.copy()
        
        # Limpiar dimensiones para evitar que vengan con mode u otros campos no deseados en normalized
        clean_dims = {}
        for k, v in dimensions.items():
            if k in ["width", "height", "depth", "length", "area", "volume", "mass", "unit", "diameter", "shape"]:
                clean_dims[k] = v
                
        self._dimensions = clean_dims
        return self
    
    def with_normalized_dimensions(
        self, 
        width: Optional[float] = None,
        height: Optional[float] = None,
        depth: Optional[float] = None,
        length: Optional[float] = None,
        area: Optional[float] = None,
        volume: Optional[float] = None,
        mass: Optional[float] = None
    ) -> "ProductBuilder":
        """
        Establece dimensiones ya normalizadas (en unidades SI estandar).
        
        Util cuando ya se han normalizado las unidades previamente.
        """
        if width is not None:
            self._normalized_dimensions["width"] = width
        if height is not None:
            self._normalized_dimensions["height"] = height
        if depth is not None:
            self._normalized_dimensions["depth"] = depth
        if length is not None:
            self._normalized_dimensions["length"] = length
        if area is not None:
            self._normalized_dimensions["area"] = area
        if volume is not None:
            self._normalized_dimensions["volume"] = volume
        if mass is not None:
            self._normalized_dimensions["mass"] = mass
        return self
    
    def with_purchase_price(self, price: Money) -> "ProductBuilder":
        """Establece el price de compra del product."""
        self._purchase_price = price
        return self

    def with_sale_price(self, price: Money) -> "ProductBuilder":
        """Establece el price de venta del product."""
        self._sale_price = price
        return self

    def with_properties(self, properties: Dict[str, Any]) -> "ProductBuilder":
        """Establece las properties adicionales del product."""
        self._properties = properties
        return self

    def with_price_override(self, price: Money) -> "ProductBuilder":
        """
        Legacy support for setting sale price.
        """
        return self.with_sale_price(price)
    
    @property
    def _material(self) -> Optional[Material]:
        """Backward compatibility for methods that still expect a single material."""
        if not self._recipe_materials:
            return None
        return self._recipe_materials[0]["material"]

    @_material.setter
    def _material(self, value: Material):
        """Temporary setter for compatibility during refactoring."""
        if not self._recipe_materials:
            self.with_material(value)
        else:
            self._recipe_materials[0]["material"] = value

    @property
    def _quantity_multiplier(self) -> Decimal:
        """Backward compatibility for global multiplier."""
        if not self._recipe_materials:
            return Decimal("1.0")
        # For legacy compatibility, return the quantity of the first material
        qty = self._recipe_materials[0].get("quantity")
        return Decimal(str(qty)) if qty is not None else Decimal("1.0")
    
    @_quantity_multiplier.setter
    def _quantity_multiplier(self, value: Any):
        """Setter for backward compatibility."""
        if not self._recipe_materials:
            # We can't set quantity without a material, but we can store it 
            # if we expect a material to be added later, or just ignore if it's a legacy call
            return
        self._recipe_materials[0]["quantity"] = Decimal(str(value))
    
    def _normalize_unit(self, unit: str) -> str:
        """
        Normalize common unit aliases to pint-compatible units.
        
        Examples:
            lb -> pound
            oz -> ounce
            cm3 -> cubic_centimeter
            g -> gram
            kg -> kilogram
            L -> liter
            mL -> milliliter
            gal -> gallon
            etc.
        
        Args:
            unit: Unit string to normalize
        
        Returns:
            Pint-compatible unit string
        """
        unit_map = {
            # Mass units
            'lb': 'pound',
            'lbs': 'pound',
            'oz': 'ounce',
            'g': 'gram',
            'kg': 'kilogram',
            'mg': 'milligram',
            'ton': 'metric_ton',
            # Volume units
            'L': 'liter',
            'mL': 'milliliter',
            'ml': 'milliliter',
            'cm3': 'cubic_centimeter',
            'cm': 'cubic_centimeter',
            'm3': 'cubic_meter',
            'm': 'cubic_meter',
            'gallon': 'gallon',
            'gal': 'gallon',
            # Length units
            'mm': 'millimeter',
            'cm': 'centimeter',
            'm': 'meter',
            'meter': 'meter',
            'metro': 'meter',
            'km': 'kilometer',
            'inch': 'inch',
            'foot': 'foot',
            'feet': 'foot',
            'yard': 'yard',
            # Area units
            'm2': 'meter ** 2',
            'm': 'meter ** 2',
            'cm2': 'centimeter ** 2',
            'cm': 'centimeter ** 2',
        }
        return unit_map.get(unit.strip(), unit)
    
    def _normalize_dimensions_with_pint(self) -> None:
        """
        Normaliza todas las dimensiones a unidades SI estandar usando pint.

        Convierte:
        - Longitudes a metros (m)
        - Areas a metros cuadrados (m)
        - Volumenes a metros cubicos (m) o litros (L)
        - Masas a kilogramos (kg)

        Raises:
            ValueError: Si las dimensiones no son valid o no se pueden convertir
        """
        if not self._dimensions:
            return

        unit_str = self._normalize_unit(self._dimensions.get("unit", "m"))
        
        # Normalizar dimensiones lineales (width, height, depth, length)
        for dim_name in ["width", "height", "depth", "length"]:
            if dim_name in self._dimensions:
                value = self._dimensions[dim_name]
                
                # Validar que el valor no sea vacio o None
                if value is None or value == "" or value == 0:
                    # Ignorar dimensiones vacias o cero - no las incluimos en normalized_dimensions
                    continue
                
                try:
                    if isinstance(value, dict):
                        # Formato: {"value": 1.0, "unit": "m"}
                        if value.get("value") is None or value.get("value") == "":
                            continue
                        normalized_unit = self._normalize_unit(value["unit"])
                        quantity = ureg.Quantity(value["value"], normalized_unit)
                    else:
                        # Formato simple: valor numerico + unit global
                        # Convertir string a float si es necesario
                        if isinstance(value, str):
                            if value.strip() == "":
                                continue
                            value = float(value)
                        quantity = ureg.Quantity(value, unit_str)
                    
                    # Convertir a metros
                    normalized = quantity.to("meter")
                    self._normalized_dimensions[dim_name] = float(normalized.magnitude)
                except (ValueError, TypeError) as e:
                    # Si no se puede convertir, ignorar esta dimension
                    continue
        
        # Normalizar area
        if "area" in self._dimensions:
            value = self._dimensions["area"]
            
            # Validar que el valor no sea vacio
            if value is None or value == "" or value == 0:
                pass  # Ignorar area vacia
            else:
                try:
                    if isinstance(value, dict):
                        if value.get("value") is None or value.get("value") == "":
                            pass
                        else:
                            normalized_unit = self._normalize_unit(value["unit"])
                            quantity = ureg.Quantity(value["value"], normalized_unit)
                            normalized = quantity.to("meter ** 2")
                            self._normalized_dimensions["area"] = float(normalized.magnitude)
                    else:
                        # Convertir string a float si es necesario
                        if isinstance(value, str):
                            if value.strip() == "":
                                pass
                            else:
                                value = float(value)
                                normalized_unit = unit_str
                                
                                # If it's a length unit, square it for area
                                if normalized_unit == 'meter':
                                    normalized_unit = 'meter ** 2'
                                elif normalized_unit == 'centimeter':
                                    normalized_unit = 'centimeter ** 2'
                                elif normalized_unit == 'millimeter':
                                    normalized_unit = 'millimeter ** 2'
                                elif normalized_unit == 'kilometer':
                                    normalized_unit = 'kilometer ** 2'
                                
                                quantity = ureg.Quantity(value, normalized_unit)
                                normalized = quantity.to("meter ** 2")
                                self._normalized_dimensions["area"] = float(normalized.magnitude)
                        else:
                            normalized_unit = unit_str
                            
                            # If it's a length unit, square it for area
                            if normalized_unit == 'meter':
                                normalized_unit = 'meter ** 2'
                            elif normalized_unit == 'centimeter':
                                normalized_unit = 'centimeter ** 2'
                            elif normalized_unit == 'millimeter':
                                normalized_unit = 'millimeter ** 2'
                            elif normalized_unit == 'kilometer':
                                normalized_unit = 'kilometer ** 2'
                            
                            quantity = ureg.Quantity(value, normalized_unit)
                            normalized = quantity.to("meter ** 2")
                            self._normalized_dimensions["area"] = float(normalized.magnitude)
                except (ValueError, TypeError) as e:
                    pass  # Ignorar area invalid
        
        # Normalizar volumen
        if "volume" in self._dimensions:
            value = self._dimensions["volume"]
            
            # Validar que el valor no sea vacio
            if value is None or value == "" or value == 0:
                pass  # Ignorar volumen vacio
            else:
                try:
                    if isinstance(value, dict):
                        if value.get("value") is None or value.get("value") == "":
                            pass
                        else:
                            normalized_unit = self._normalize_unit(value["unit"])
                            quantity = ureg.Quantity(value["value"], normalized_unit)
                            if normalized_unit in ['liter', 'litre']:
                                normalized = quantity.to("liter")
                            else:
                                normalized = quantity.to("meter ** 3")
                            self._normalized_dimensions["volume"] = float(normalized.magnitude)
                    else:
                        # Convertir string a float si es necesario
                        if isinstance(value, str):
                            if value.strip() == "":
                                pass
                            else:
                                value = float(value)
                                volume_units = {'L', 'liter', 'litro', 'litre', 'mL', 'milliliter', 'ml', 'cm3', 'cm', 'm3', 'm', 'gallon', 'gal'}
                                normalized_unit = self._normalize_unit(unit_str) if unit_str in volume_units or self._normalize_unit(unit_str) in volume_units else "liter"
                                quantity = ureg.Quantity(value, normalized_unit)
                                if normalized_unit in ['liter', 'litre']:
                                    normalized = quantity.to("liter")
                                else:
                                    normalized = quantity.to("meter ** 3")
                                self._normalized_dimensions["volume"] = float(normalized.magnitude)
                        else:
                            volume_units = {'L', 'liter', 'litro', 'litre', 'mL', 'milliliter', 'ml', 'cm3', 'cm', 'm3', 'm', 'gallon', 'gal'}
                            normalized_unit = self._normalize_unit(unit_str) if unit_str in volume_units or self._normalize_unit(unit_str) in volume_units else "liter"
                            quantity = ureg.Quantity(value, normalized_unit)
                            if normalized_unit in ['liter', 'litre']:
                                normalized = quantity.to("liter")
                            else:
                                normalized = quantity.to("meter ** 3")
                            self._normalized_dimensions["volume"] = float(normalized.magnitude)
                except (ValueError, TypeError) as e:
                    pass  # Ignorar volumen invalid
        
        # Normalizar masa
        if "mass" in self._dimensions:
            value = self._dimensions["mass"]
            
            # Validar que el valor no sea vacio
            if value is None or value == "" or value == 0:
                pass  # Ignorar masa vacia
            else:
                try:
                    if isinstance(value, dict):
                        if value.get("value") is None or value.get("value") == "":
                            pass
                        else:
                            normalized_unit = self._normalize_unit(value["unit"])
                            quantity = ureg.Quantity(value["value"], normalized_unit)
                            normalized = quantity.to("kilogram")
                            self._normalized_dimensions["mass"] = float(normalized.magnitude)
                    else:
                        # Convertir string a float si es necesario
                        if isinstance(value, str):
                            if value.strip() == "":
                                pass
                            else:
                                value = float(value)
                                mass_units = {'kg', 'kilogram', 'g', 'gram', 'mg', 'milligram', 'lb', 'pound', 'lbs', 'oz', 'ounce', 'ton', 'metric_ton'}
                                normalized_unit = self._normalize_unit(unit_str) if unit_str in mass_units or self._normalize_unit(unit_str) in mass_units else "kilogram"
                                quantity = ureg.Quantity(value, normalized_unit)
                                normalized = quantity.to("kilogram")
                                self._normalized_dimensions["mass"] = float(normalized.magnitude)
                        else:
                            mass_units = {'kg', 'kilogram', 'g', 'gram', 'mg', 'milligram', 'lb', 'pound', 'lbs', 'oz', 'ounce', 'ton', 'metric_ton'}
                            normalized_unit = self._normalize_unit(unit_str) if unit_str in mass_units or self._normalize_unit(unit_str) in mass_units else "kilogram"
                            quantity = ureg.Quantity(value, normalized_unit)
                            normalized = quantity.to("kilogram")
                            self._normalized_dimensions["mass"] = float(normalized.magnitude)
                except (ValueError, TypeError) as e:
                    pass  # Ignorar masa invalid
    
    def _validate_dimensions_with_strategy(self) -> None:
        """
        Valida que las dimensiones sean compatibles con la estrategia de measurement.

        Raises:
            ValueError: Si las dimensiones no son valid para la estrategia
        """
        if not self._strategy:
            return

        # Create diccionario de properties para validar
        # Nota: La estrategia espera value objects (Gauge, Measurement) pero aqui
        # validamos dimensiones normalizadas. La validacion completa se hace
        # en el repositorio/servicio cuando se tienen los value objects completos.

        strategy_name = self._strategy.get_type_name()
        
        if strategy_name == "SHEET":
            # SHEET requiere: (width y height) o area
            has_width_height = "width" in self._normalized_dimensions and "height" in self._normalized_dimensions
            has_area = "area" in self._normalized_dimensions
            if not (has_width_height or has_area):
                raise ValueError(
                    "SHEET strategy requiere dimensiones: (width y height) o area"
                )
        
        elif strategy_name == "PROFILE":
            # PROFILE requiere: length
            if "length" not in self._normalized_dimensions:
                raise ValueError("PROFILE strategy requiere dimension: length")
        
        elif strategy_name == "LIQUID":
            # LIQUID requiere: volume
            if "volume" not in self._normalized_dimensions:
                raise ValueError("LIQUID strategy requiere dimension: volume")
        
        elif strategy_name == "SOLID":
            # SOLID requiere: (width, height, depth) o mass o volume
            has_dimensions = all(
                k in self._normalized_dimensions 
                for k in ["width", "height", "depth"]
            )
            has_mass = "mass" in self._normalized_dimensions
            has_volume = "volume" in self._normalized_dimensions
            if not (has_dimensions or has_mass or has_volume):
                raise ValueError(
                    "SOLID strategy requiere: (width, height, depth) o mass o volume"
                )
        
        elif strategy_name == "LABOR":
            # LABOR requiere: 
            # - Para linear_meter: length O (width y height)
            # - Para square_meter: area O (width y height)
            if self._material and hasattr(self._material, 'properties'):
                unit_type = self._material.properties.get('unit_type', 'linear_meter')
                
                if unit_type == "linear_meter":
                    has_length = "length" in self._normalized_dimensions
                    has_width_height = ("width" in self._normalized_dimensions and 
                                      "height" in self._normalized_dimensions)
                    if not (has_length or has_width_height):
                        raise ValueError(
                            "LABOR linear_meter requiere: length O (width y height)"
                        )
                
                elif unit_type == "square_meter":
                    has_area = "area" in self._normalized_dimensions
                    has_width_height = ("width" in self._normalized_dimensions and 
                                      "height" in self._normalized_dimensions)
                    if not (has_area or has_width_height):
                        raise ValueError(
                            "LABOR square_meter requiere: area O (width y height)"
                        )
    
    def _calculate_quantity_multiplier(self) -> None:
        """
        Calcula el quantity_multiplier basado en las dimensiones normalizadas
        y la estrategia de measurement del material.
        
        El quantity_multiplier se usa para calcular el price:
        price = material.price  quantity_multiplier
        """
        if not self._material:
            self._quantity_multiplier = Decimal("1.0")
            return
        
        strategy_name = self._material.get_measurement_type()
        
        # NOTE: This entire method is now refactored to populate a per-item quantity 
        # instead of a global multiplier. However, the builder logic currently handles 
        # a "single material" case by default.
        # We will keep the logic to calculate the multiplier, but now it represents 
        # the quantity for the ProductMaterial item.
        
        if strategy_name == "SHEET":
            # Para laminas: multiplicador = (area product / area material)
            
            # Si tenemos la estrategia inyectada, delegar el calculo del ratio
            if self._strategy:
                # Preparar material_properties (convertir Value Objects si es necesario)
                # Nota: SheetMeasurementStrategy.calculate_usage_ratio espera que material_properties 
                # contenga los campos 'area' o 'width'/'length'.
                try:
                    self._quantity_multiplier = self._strategy.calculate_usage_ratio(
                        self._material.properties,
                        self._normalized_dimensions # Usamos las normalizadas para consistencia
                    )
                    return
                except Exception:
                    # Si falla la delegacion, procedemos con el calculo local (fallback)
                    pass

            # 1. Obtener el area del product (en m2 ya que normalized_dimensions estan en metros)
            product_area = Decimal("0")
            if all(k in self._normalized_dimensions for k in ["width", "height"]):
                width = Decimal(str(self._normalized_dimensions["width"]))
                height = Decimal(str(self._normalized_dimensions["height"]))
                product_area = width * height
            elif "area" in self._normalized_dimensions:
                product_area = Decimal(str(self._normalized_dimensions["area"]))
            
            # 2. Obtener el area de referencia del material (NORMALIZADO a m2)
            material_area = Decimal("1.0")  # Fallback
            
            # Si tenemos la estrategia, podemos usar calculate_quantity que ya normaliza
            if self._strategy:
                try:
                    qty = self._strategy.calculate_quantity(self._material.properties)
                    if hasattr(qty, 'value'):
                        material_area = qty.value
                except Exception:
                    pass
            else:
                # Fallback manual si no hay estrategia
                if self._material and "area" in self._material.properties:
                    m_area = self._material.properties["area"]
                    if isinstance(m_area, Measurement):
                        # Convertir a m2 si no lo esta
                        # Aqui hay un riesgo si no tenemos el repo de unidades, 
                        # por eso es mejor usar la estrategia.
                        material_area = m_area.value # Asumimos m2 por ahora o que ya viene normalizado
                    elif isinstance(m_area, dict):
                        material_area = Decimal(str(m_area.get("value", "1.0")))
                elif self._material and "width" in self._material.properties and "length" in self._material.properties:
                    def _get_val_in_meters(v):
                        # Este fallback es peligroso sin conocer la unidad, 
                        # reafirma por que necesitamos la estrategia.
                        if isinstance(v, Measurement): 
                            return v.value # TODO: convertir a metros
                        if isinstance(v, dict): return Decimal(str(v.get("value", "0")))
                        return Decimal(str(v))
                    w = _get_val_in_meters(self._material.properties["width"])
                    l = _get_val_in_meters(self._material.properties["length"])
                    material_area = w * l

            # 3. Calcular multiplicador (Ratio)
            if material_area > 0:
                self._quantity_multiplier = product_area / material_area
            else:
                self._quantity_multiplier = Decimal("1.0")

            # 4. Ajuste por profundidad (opcional, si aplica)
            if "depth" in self._normalized_dimensions:
                depth = Decimal(str(self._normalized_dimensions["depth"]))
                self._quantity_multiplier *= depth
        
        elif strategy_name == "PROFILE":
            # Para perfiles: longitud
            if self._strategy:
                try:
                    self._quantity_multiplier = self._strategy.calculate_usage_ratio(
                        self._material.properties,
                        self._normalized_dimensions
                    )
                    return
                except Exception:
                    pass

            if "length" in self._normalized_dimensions:
                self._quantity_multiplier = Decimal(str(self._normalized_dimensions["length"]))
            else:
                self._quantity_multiplier = Decimal("1.0")
        
        elif strategy_name == "LIQUID":
            # Para liquidos: volumen
            if "volume" in self._normalized_dimensions:
                self._quantity_multiplier = Decimal(str(self._normalized_dimensions["volume"]))
            else:
                self._quantity_multiplier = Decimal("1.0")
        
        elif strategy_name == "SOLID":
            # Para solidos: masa o volumen
            if self._strategy:
                try:
                    self._quantity_multiplier = self._strategy.calculate_usage_ratio(
                        self._material.properties,
                        self._normalized_dimensions
                    )
                    return
                except Exception:
                    pass

            if "mass" in self._normalized_dimensions:
                self._quantity_multiplier = Decimal(str(self._normalized_dimensions["mass"]))
            elif "volume" in self._normalized_dimensions:
                self._quantity_multiplier = Decimal(str(self._normalized_dimensions["volume"]))
            elif all(k in self._normalized_dimensions for k in ["width", "height", "depth"]):
                width = Decimal(str(self._normalized_dimensions["width"]))
                height = Decimal(str(self._normalized_dimensions["height"]))
                depth = Decimal(str(self._normalized_dimensions["depth"]))
                self._quantity_multiplier = width * height * depth
            else:
                self._quantity_multiplier = Decimal("1.0")
        
        elif strategy_name == "LABOR":
            # Para mano de obra: perimetro (linear_meter) o area (square_meter)
            if self._strategy:
                try:
                    self._quantity_multiplier = self._strategy.calculate_usage_ratio(
                        self._material.properties,
                        self._normalized_dimensions
                    )
                    return
                except Exception:
                    pass

            if self._material and hasattr(self._material, 'properties'):
                unit_type = self._material.properties.get('unit_type', 'linear_meter')
                
                if unit_type == "linear_meter":
                    # Si tenemos length directo, usalo
                    if "length" in self._normalized_dimensions:
                        self._quantity_multiplier = Decimal(str(self._normalized_dimensions["length"]))
                    # Si tenemos width y height, calcula perimetro
                    elif "width" in self._normalized_dimensions and "height" in self._normalized_dimensions:
                        width = Decimal(str(self._normalized_dimensions["width"]))
                        height = Decimal(str(self._normalized_dimensions["height"]))
                        self._quantity_multiplier = (width + height) * Decimal("2")
                    else:
                        self._quantity_multiplier = Decimal("1.0")
                
                elif unit_type == "square_meter":
                    # Si tenemos width, height Y depth  calcular volumen (width  height  depth)
                    if all(k in self._normalized_dimensions for k in ["width", "height", "depth"]):
                        width = Decimal(str(self._normalized_dimensions["width"]))
                        height = Decimal(str(self._normalized_dimensions["height"]))
                        depth = Decimal(str(self._normalized_dimensions["depth"]))
                        self._quantity_multiplier = width * height * depth
                    # Si solo width y height, calcular area
                    elif "width" in self._normalized_dimensions and "height" in self._normalized_dimensions:
                        width = Decimal(str(self._normalized_dimensions["width"]))
                        height = Decimal(str(self._normalized_dimensions["height"]))
                        self._quantity_multiplier = width * height
                    # Si solo tenemos area directo (sin width y height), usarlo
                    elif "area" in self._normalized_dimensions:
                        self._quantity_multiplier = Decimal(str(self._normalized_dimensions["area"]))
                    else:
                        self._quantity_multiplier = Decimal("1.0")
                else:
                    self._quantity_multiplier = Decimal("1.0")
            else:
                self._quantity_multiplier = Decimal("1.0")
        
        else:
            # Estrategia SIMPLE o desconocida
            self._quantity_multiplier = Decimal("1.0")
    
    def _get_original_dim_info(self, key: str) -> tuple[Any, str]:
        """
        Obtiene valor y unidad de una dimension original de forma segura.
        Maneja tanto el formato simple como el formato de diccionario.
        """
        if not self._original_dimensions:
            return None, self._original_dimensions.get('unit', 'm')
            
        val = self._original_dimensions.get(key)
        unit = self._original_dimensions.get('unit', 'm')
        
        if isinstance(val, dict):
            unit = val.get('unit', unit)
            val = val.get('value')
            
        return val, unit

    def _format_number(self, val: Any) -> str:
        """Formatea un number usando el formato :g de forma segura."""
        if val is None or val == "":
            return ""
        if isinstance(val, (int, float, Decimal)):
            return f"{val:g}"
        try:
            return f"{float(val):g}"
        except (ValueError, TypeError):
            return str(val)

    def _format_original_dimension(self, dimension_key: str):
        """Formatea una dimension original con su unidad para mostrar en el nombre."""
        value, unit = self._get_original_dim_info(dimension_key)
        
        if value is None or value == "":
            return None
        
        formatted_value = self._format_number(value)
        
        # Mapear unidades
        unit_map = {
            'm': 'm', 'meter': 'm', 'cm': 'cm', 'mm': 'mm',
            'm2': 'm', 'meter ** 2': 'm', 'L': 'L', 'liter': 'L', 'kg': 'kg', 'gram': 'g', 'g': 'g'
        }
        
        display_unit = unit_map.get(unit, unit)
        return f"{formatted_value}{display_unit}"
    
    def _generate_name_if_needed(self) -> None:
        """
        Genera un nombre descriptivo considerando los materials clave en la receta.
        Si se proporciono un nombre custom, lo usa como prefijo del nombre tecnico.
        
        Usa las dimensiones originales del user para el nombre, no las normalizadas.
        """
        custom_name_prefix = self._name  # Save el nombre custom si existe
        
        if not self._recipe_materials:
            if custom_name_prefix:
                self._name = custom_name_prefix
            else:
                self._name = self._description or "Product personalizado"
            return

        # 1. Identificar materials clave para el nombre (excluir LABOR si hay fisicos)
        physical_materials = [rm for rm in self._recipe_materials 
                             if rm["material"].material_type.measurement_strategy != "LABOR"]
        
        materials_to_show = physical_materials if physical_materials else self._recipe_materials
        
        # Construir base de materials (ej: "Aluminio + Vidrio")
        material_base_name = " + ".join([rm["material"].material_type.name for rm in materials_to_show[:2]])
        if len(materials_to_show) > 2:
            material_base_name += "..."

        # 2. Generar componente tecnico basado en el primer material (principal)
        primary_rm = self._recipe_materials[0]
        primary_mat = primary_rm["material"]
        strategy_name = primary_mat.get_measurement_type()
        base_mat_full_name = primary_mat.full_name
        
        technical_detail = None
        
        if strategy_name == "PROFILE":
            if self._strategy and hasattr(self._strategy, 'generate_description'):
                props = primary_mat.properties.copy()
                for dim in ["length", "width", "height", "diameter"]:
                    val, _ = self._get_original_dim_info(dim)
                    if val:
                        props[dim] = val
                technical_detail = self._strategy.generate_description(props)
            else:
                length_str = self._format_original_dimension("length")
                technical_detail = f"{material_base_name} {length_str}" if length_str else material_base_name
        
        elif strategy_name == "SHEET":
            w_str = self._format_original_dimension("width")
            h_str = self._format_original_dimension("height")
            if w_str and h_str:
                technical_detail = f"{material_base_name} {w_str}x{h_str}"
            else:
                technical_detail = material_base_name
        
        elif strategy_name == "LIQUID":
            volume_str = self._format_original_dimension("volume")
            technical_detail = f"{material_base_name} {volume_str}" if volume_str else material_base_name
        
        elif strategy_name == "SOLID":
            mass_str = self._format_original_dimension("mass")
            volume_str = self._format_original_dimension("volume")
            w_str = self._format_original_dimension("width")
            h_str = self._format_original_dimension("height")
            d_str = self._format_original_dimension("depth")

            if mass_str:
                technical_detail = f"{material_base_name} {mass_str}"
            elif volume_str:
                technical_detail = f"{material_base_name} {volume_str}"
            elif w_str and h_str and d_str:
                technical_detail = f"{material_base_name} {w_str}x{h_str}x{d_str}"
            else:
                technical_detail = material_base_name
        
        elif strategy_name == "LABOR":
            material_props = getattr(primary_mat, 'properties', {}) or {}
            unit_type = material_props.get('unit_type', 'linear_meter')
            
            if unit_type == "linear_meter":
                length_str = self._format_original_dimension("length")
                w_val_orig, w_unit = self._get_original_dim_info("width")
                h_val_orig, _ = self._get_original_dim_info("height")

                if length_str:
                    technical_detail = f"{material_base_name} {length_str}"
                elif w_val_orig is not None and h_val_orig is not None:
                    perimeter = (float(w_val_orig) + float(h_val_orig)) * 2
                    unit_display = {'m': 'm', 'cm': 'cm', 'mm': 'mm'}.get(w_unit, w_unit)
                    technical_detail = f"{material_base_name} {self._format_number(perimeter)}{unit_display} perim."
                else:
                    technical_detail = material_base_name
            
            elif unit_type == "square_meter":
                w_val_orig, w_unit = self._get_original_dim_info("width")
                h_val_orig, _ = self._get_original_dim_info("height")
                if w_val_orig is not None and h_val_orig is not None:
                    unit_display = {'m': 'm', 'cm': 'cm', 'mm': 'mm'}.get(w_unit, w_unit)
                    technical_detail = f"{material_base_name} {self._format_number(w_val_orig)}x{self._format_number(h_val_orig)}{unit_display}"
                else:
                    technical_detail = material_base_name
            else:
                technical_detail = material_base_name
        
        else:
            # Fallback generico para otras estrategias
            w_val_orig, w_unit = self._get_original_dim_info("width")
            h_val_orig, _ = self._get_original_dim_info("height")
            if w_val_orig is not None and h_val_orig is not None:
                unit_display = {'m': 'm', 'cm': 'cm', 'mm': 'mm'}.get(w_unit, w_unit)
                technical_detail = f"{material_base_name} {self._format_number(w_val_orig)}x{self._format_number(h_val_orig)}{unit_display}"
            else:
                technical_detail = material_base_name
        
        # 3. Combinar nombre custom con el detalle tecnico generado
        if custom_name_prefix:
            self._name = f"{custom_name_prefix} - {technical_detail}"
            # La description tecnica para el frontend sera el detalle
            self._description = technical_detail
        else:
            self._name = technical_detail

    
    def _generate_description_if_needed(self) -> None:
        """Genera una description detallada si no se proporciono una."""
        if self._description:
            return
        
        if not self._recipe_materials:
            self._description = "Product personalizado"
            return
            
        # Usar el nombre de los materials como base
        material_names = [rm["material"].material_type.name for rm in self._recipe_materials]
        primary_material_name = self._recipe_materials[0]["material"].full_name
        
        # Generar description basada en material y dimensiones segun la estrategia
        strategy_name = self._recipe_materials[0]["material"].get_measurement_type()
        
        # Generar description segun la estrategia del material principal
        if strategy_name == "PROFILE":
            if "length" in self._normalized_dimensions:
                length = round(self._normalized_dimensions["length"], 2)
                self._description = f"{primary_material_name} de {length} metros de largo"
            else:
                self._description = f"{primary_material_name} personalizado"
        
        elif strategy_name == "SHEET":
            if "area" in self._normalized_dimensions:
                area = round(self._normalized_dimensions["area"], 2)
                self._description = f"{primary_material_name} con area de {area} m"
            elif "width" in self._normalized_dimensions and "height" in self._normalized_dimensions:
                w = round(self._normalized_dimensions["width"], 2)
                h = round(self._normalized_dimensions["height"], 2)
                area = round(w * h, 2)
                self._description = f"{primary_material_name} de {w}m x {h}m ({area}m)"
            else:
                self._description = f"{primary_material_name} personalizado"
        
        elif strategy_name == "LIQUID":
            if "volume" in self._normalized_dimensions:
                volume = round(self._normalized_dimensions["volume"], 2)
                self._description = f"{primary_material_name} de {volume} litros"
            else:
                self._description = f"{primary_material_name} personalizado"
        
        elif strategy_name == "SOLID":
            if "mass" in self._normalized_dimensions:
                mass = round(self._normalized_dimensions["mass"], 2)
                self._description = f"{primary_material_name} de {mass} kilogramos"
            elif "volume" in self._normalized_dimensions:
                volume = round(self._normalized_dimensions["volume"], 2)
                self._description = f"{primary_material_name} de {volume} litros"
            elif all(k in self._normalized_dimensions for k in ["width", "height", "depth"]):
                w = round(self._normalized_dimensions["width"], 2)
                h = round(self._normalized_dimensions["height"], 2)
                d = round(self._normalized_dimensions["depth"], 2)
                volume = round(w * h * d, 3)
                self._description = f"{primary_material_name} de {w}m x {h}m x {d}m ({volume}m)"
            else:
                self._description = f"{primary_material_name} personalizado"
        
        elif strategy_name == "LABOR":
            material_props = getattr(self._recipe_materials[0]["material"], 'properties', {}) or {}
            unit_type = material_props.get('unit_type', 'linear_meter')
            
            if unit_type == "linear_meter":
                if "length" in self._normalized_dimensions:
                    length = round(self._normalized_dimensions["length"], 2)
                    self._description = f"{primary_material_name} por {length} metros"
                elif "width" in self._normalized_dimensions and "height" in self._normalized_dimensions:
                    w = round(self._normalized_dimensions["width"], 2)
                    h = round(self._normalized_dimensions["height"], 2)
                    perimeter = round((w + h) * 2, 2)
                    self._description = f"{primary_material_name} para perimetro de {perimeter} metros ({w}m x {h}m)"
                else:
                    self._description = f"{primary_material_name} personalizado"
            
            elif unit_type == "square_meter":
                if "area" in self._normalized_dimensions:
                    area = round(self._normalized_dimensions["area"], 2)
                    self._description = f"{primary_material_name} para {area} m"
                elif "width" in self._normalized_dimensions and "height" in self._normalized_dimensions:
                    w = round(self._normalized_dimensions["width"], 2)
                    h = round(self._normalized_dimensions["height"], 2)
                    area = round(w * h, 2)
                    self._description = f"{primary_material_name} para {area} m ({w}m x {h}m)"
                else:
                    self._description = f"{primary_material_name} personalizado"
            else:
                self._description = f"{primary_material_name} personalizado"
        
        else:
            if "width" in self._normalized_dimensions and "height" in self._normalized_dimensions:
                w = round(self._normalized_dimensions["width"], 2)
                h = round(self._normalized_dimensions["height"], 2)
                self._description = f"{primary_material_name} de {w}m x {h}m"
            elif "area" in self._normalized_dimensions:
                area = round(self._normalized_dimensions["area"], 2)
                self._description = f"{primary_material_name} con area de {area} m"
            elif "length" in self._normalized_dimensions:
                length = round(self._normalized_dimensions["length"], 2)
                self._description = f"{primary_material_name} de {length} metros"
            else:
                self._description = f"{primary_material_name} personalizado"
        
        # Si hay mas de un material, mencionarlo
        if len(self._recipe_materials) > 1:
            others = ", ".join([rm["material"].material_type.name for rm in self._recipe_materials[1:]])
            self._description += f" (incluye: {others})"
    
    def _calculate_material_quantity(self, material: Material, dimensions: Dict[str, Any]) -> Decimal:
        """
        Calcula la quantity necesaria para un material especifico basado en dimensiones.
        """
        # 1. Normalizar dimensiones temporales para el calculo
        temp_normalized = {}
        unit_str = self._normalize_unit(dimensions.get("unit", "m"))
        
        for dim_name in ["width", "height", "depth", "length", "area", "volume", "mass"]:
            if dim_name in dimensions:
                value = dimensions[dim_name]
                if value is None or value == "" or value == 0: continue
                
                try:
                    if isinstance(value, dict):
                        norm_unit = self._normalize_unit(value["unit"])
                        q = ureg.Quantity(value["value"], norm_unit)
                    else:
                        if isinstance(value, str): value = float(value)
                        q = ureg.Quantity(value, unit_str)
                    
                    target = "meter"
                    if dim_name == "area": target = "meter ** 2"
                    elif dim_name == "volume": 
                        volume_units = {'L', 'liter', 'litro', 'litre'}
                        target = "liter" if (isinstance(value, dict) and value.get("unit") in volume_units) or unit_str in volume_units else "meter ** 3"
                    elif dim_name == "mass": target = "kilogram"
                    
                    temp_normalized[dim_name] = float(q.to(target).magnitude)
                except: continue

        strategy_name = material.get_measurement_type()
        
        if strategy_name == "PROFILE":
            if "length" in temp_normalized:
                # 1. Get material length (reference)
                mat_len = Decimal("1.0")
                if material.properties and "length" in material.properties:
                    m_len = material.properties["length"]
                    if hasattr(m_len, 'value'): mat_len = Decimal(str(m_len.value))
                    elif isinstance(m_len, dict): mat_len = Decimal(str(m_len.get('value', 1.0)))
                    else: mat_len = Decimal(str(m_len))
                
                # 2. Ratio based on length
                return Decimal(str(temp_normalized["length"])) / mat_len if mat_len > 0 else Decimal("1.0")
            return Decimal("1.0")
        elif strategy_name == "LIQUID" and "volume" in temp_normalized:
            return Decimal(str(temp_normalized["volume"]))
        elif strategy_name == "SOLID":
            if "mass" in temp_normalized:
                return Decimal(str(temp_normalized["mass"]))
            if "volume" in temp_normalized:
                return Decimal(str(temp_normalized["volume"]))
            if all(k in temp_normalized for k in ["width", "height", "depth"]):
                v = Decimal(str(temp_normalized["width"])) * Decimal(str(temp_normalized["height"])) * Decimal(str(temp_normalized["depth"]))
                return v
        elif strategy_name == "LABOR":
            unit_type = material.properties.get("unit_type", "linear_meter")
            if unit_type == "linear_meter":
                if "length" in temp_normalized:
                    return Decimal(str(temp_normalized["length"]))
                if "width" in temp_normalized and "height" in temp_normalized:
                    return (Decimal(str(temp_normalized["width"])) + Decimal(str(temp_normalized["height"]))) * Decimal("2")
            elif unit_type == "square_meter":
                if "area" in temp_normalized:
                    return Decimal(str(temp_normalized["area"]))
                if "width" in temp_normalized and "height" in temp_normalized:
                    return Decimal(str(temp_normalized["width"])) * Decimal(str(temp_normalized["height"]))
        elif strategy_name == "SHEET":
            material_area = Decimal("1.0")
            if material.properties and "area" in material.properties:
                m_area = material.properties["area"]
                if hasattr(m_area, 'value'):
                    material_area = Decimal(str(m_area.value))
                elif isinstance(m_area, dict):
                    material_area = Decimal(str(m_area.get('value', 1.0)))
                else:
                    material_area = Decimal(str(m_area))
            
            prod_area = Decimal("0")
            if "width" in temp_normalized and "height" in temp_normalized:
                prod_area = Decimal(str(temp_normalized["width"])) * Decimal(str(temp_normalized["height"]))
            elif "area" in temp_normalized:
                prod_area = Decimal(str(temp_normalized["area"]))
            
            return prod_area / material_area if material_area > 0 else Decimal("1.0")
        
        return Decimal("1.0")

    def with_strategy(self, strategy: MeasurementStrategy) -> "ProductBuilder":
        """Establece la estrategia de measurement para validacion y calculos."""
        self._strategy = strategy
        return self

    def build(self) -> SimpleProduct:
        """
        Construye el SimpleProduct con soporte para multiples materials.
        """
        if not self._recipe_materials and self._sale_price is None:
            raise ValueError("SimpleProduct requiere al menos un material o un sale_price")

        if self._dimensions:
            self._normalize_dimensions_with_pint()
        
        # Generar materials finales
        from app.domain.models.product import ProductMaterial
        final_materials = []
        for item in self._recipe_materials:
            material = item["material"]
            qty = item["quantity"]
            if qty is None:
                qty = self._calculate_material_quantity(material, item["dimensions"])
            
            final_materials.append(ProductMaterial(
                material=material,
                quantity=qty,
                dimensions=item["dimensions"]
            ))

        # Determinar material primario para el nombre (el primero de la receta)
        primary_material = self._recipe_materials[0]["material"] if self._recipe_materials else None
        
        # Hack temporal para que las funciones de generacion de nombre/description funcionen
        # (Idealmente deberian ser refactorizadas para recetas, pero vamos paso a paso)
        if primary_material:
            self._recipe_materials[0]["material"] = primary_material # Re-ensure for type safety
            
        self._generate_name_if_needed()
        self._generate_description_if_needed()
        
        return SimpleProduct(
            id=self._id,
            name=self._name or "Product",
            description=self._description or "",
            image_url=self._image_url,
            tenant_id=self._tenant_id if hasattr(self, "_tenant_id") else None,
            materials=final_materials,
            dimensions=self._dimensions,
            purchase_price=self._purchase_price if not final_materials else None,
            sale_price=self._sale_price if not final_materials else None,
            properties=self._properties
        )




# INTEGRATION HOOK: Este builder debe ser usado por los servicios de aplicacion
# (ProductCreationService, etc.) para construir products con validacion completa.
# La capa de aplicacion debe:
# 1. Obtener el material del repositorio
# 2. Obtener la estrategia de measurement apropiada
# 3. Validar permisos de user (MANAGER para price_override)
# 4. Usar el builder para construir el product
# 5. Persistir con ProductRepository.save()

