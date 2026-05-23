"""
Use cases for Product Templates and Instantiation.
"""
import uuid
from typing import Dict, List, Optional, Any
from app.domain.models.product import ProductComponent, SimpleProduct, CompositeProduct
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.material_repository import MaterialRepository
from app.domain.builders.composite_builder import CompositeProductBuilder
from app.application.dto.product_dto import TemplateRequirementDTO

class GetTemplateRequirementsUseCase:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def execute(self, template_id: uuid.UUID) -> List[TemplateRequirementDTO]:
        template = self.product_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found.")
        
        requirements: List[TemplateRequirementDTO] = []
        
        def collect_requirements(node: ProductComponent):
            if isinstance(node, SimpleProduct) and node.is_template:
                if node.material_type:
                    requirements.append(TemplateRequirementDTO(
                        component_id=node.id,
                        component_name=node.name,
                        material_type_id=node.material_type.id,
                        material_type_name=node.material_type.name
                    ))
            elif isinstance(node, CompositeProduct):
                for comp_qty in node.components:
                    collect_requirements(comp_qty.component)
        
        collect_requirements(template)
        return requirements

class InstantiateProductUseCase:
    def __init__(
        self, 
        product_repo: ProductRepository,
        material_repo: MaterialRepository
    ):
        self.product_repo = product_repo
        self.material_repo = material_repo

    def execute(
        self, 
        template_id: uuid.UUID, 
        material_assignments: Dict[uuid.UUID, uuid.UUID],
        custom_name: Optional[str] = None,
        image_url: Optional[str] = None,
        overrides: Optional[Dict[uuid.UUID, Dict[str, Any]]] = None
    ) -> ProductComponent:
        # 1. Load template
        template = self.product_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found.")
        
        if not template.is_template:
            raise ValueError(f"Product {template_id} is not a template.")

        # 2. Use CompositeProductBuilder for cloning and injection
        if isinstance(template, CompositeProduct):
            builder = CompositeProductBuilder(template)
            if custom_name:
                builder.with_name(custom_name)
            if image_url:
                builder.with_image_url(image_url)
            
            # 3. Inject materials
            for comp_id, mat_id in material_assignments.items():
                material = self.material_repo.get_by_id(mat_id)
                if not material:
                    raise ValueError(f"Material {mat_id} not found.")
                builder.assign_material(comp_id, material)

            # 4. Apply Overrides
            if overrides:
                for comp_id, attr_overrides in overrides.items():
                    if "image_url" in attr_overrides:
                        builder.override_component_image(comp_id, attr_overrides["image_url"])
                    if "properties" in attr_overrides:
                        builder.override_component_properties(comp_id, attr_overrides["properties"])
            
            new_product = builder.build()
        elif isinstance(template, SimpleProduct):
            # SimpleProduct template
            material_id = material_assignments.get(template.id)
            if not material_id:
                raise ValueError(f"Material assignment missing for template {template.id}")
            
            material = self.material_repo.get_by_id(material_id)
            if not material:
                raise ValueError(f"Material {material_id} not found.")
            
            # Manual clone for SimpleProduct
            new_product = SimpleProduct(
                id=uuid.uuid4(),
                name=custom_name or f"{template.name} (Instantiated)",
                description=template.description,
                material=material,
                material_type=template.material_type,
                dimensions=template.dimensions.copy(),
                quantity_multiplier=template.quantity_multiplier,
                purchase_price=template.purchase_price,
                sale_price=template.sale_price,
                image_url=image_url or template.image_url,
                properties=(overrides.get(template.id, {}).get("properties") or template.properties.copy()) if overrides else template.properties.copy(),
                tenant_id=template.tenant_id
            )
        else:
             raise ValueError("Unsupported product type for instantiation.")

        # 5. Final validation
        if not new_product.is_complete:
            missing = new_product.get_required_material_types()
            raise ValueError(f"Product instantiation incomplete. Missing: {list(missing.values())}")

        # 5. Persist
        return self.product_repo.save(new_product)
