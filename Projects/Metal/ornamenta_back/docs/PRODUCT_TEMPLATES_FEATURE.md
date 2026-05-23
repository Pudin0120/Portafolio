# Product Templates & Instantiation Feature
> **Status:** In Progress (Domain Logic Complete, Persistence/API Pending)  
> **Date:** Jan 02, 2026

## 1. Vision & Objective
The goal is to implement a **Product Template System** that allows the creation of "Abstract Products" (Templates) which define a structure and required material types, but not specific materials or prices. 

This solves the problem of redundancy: instead of creating specific products for every possible material combination (e.g., "Steel Door Gauge 18", "Steel Door Gauge 20", "Aluminum Door"), we create **One Template** ("Metal Door") and "Instantiate" it with specific materials on demand.

### Key Concepts
1.  **Template (Abstract):** A `CompositeProduct` tree where leaf nodes (`SimpleProduct`) define a **Required `MaterialType`** (e.g., "Sheet Metal") but have `material=None`. It has **No Price**.
2.  **Instantiation:** The process of taking a Template, cloning its structure, and injecting concrete `Material` entities (e.g., "Galvanized Steel Gauge 18 - $50k") into the slots defined by the `MaterialType`.
3.  **Concrete Product:** The result of instantiation. A complete product tree where all components have specific materials and a calculated price.

---

## 2. Current Status (What we built)

### OK Domain Layer (100% Complete)
We have successfully implemented the core logic and design patterns required for this feature.

*   **Models Refactoring:**
    *   Updated `SimpleProduct` to support `is_template` state (when `material` is None but `material_type` is set).
    *   Implemented `get_required_material_types()` to recursively fetch requirements from the tree.
    *   Logic to prevent price calculation on incomplete templates.

*   **Design Patterns:**
    *   **Composite Pattern:** Validated via `tests/domain/test_product.py`. Handles nested structures (Door -> Frame + Panel -> Sheet).
    *   **Builder Pattern:** Implemented `CompositeProductBuilder` in `app/domain/builders/composite_builder.py`.
        *   Handles **Deep Copy** of templates (immutability of the source).
        *   Handles **Recursive Search** to find components by ID.
        *   Handles **Material Injection** with type validation (e.g., prevents putting "Wood" where "Steel" is required).

*   **Testing:**
    *   Unit Tests (`tests/domain/test_product.py`): **PASSED** (22/22).
    *   Builder Tests (`tests/domain/test_composite_builder.py`): **PASSED** (8/8).

---

## 3. What is Missing (Roadmap)

To make this feature usable by the frontend application, we need to move up the Clean Architecture layers.

###  Phase 1: Infrastructure & Persistence (20% Effort)
*   **Goal:** Ensure we can save a "Template" to the database without crashing.
*   **Current Risk:** The `products` table expects a linked `material_id`. We need to verify if our SQLAlchemy mapping handles `material_id=NULL` correctly when `material_type_id` is present.
*   **Task:** Create a persistence test that saves a Template and retrieves it, verifying the structure remains intact.

###  Phase 2: Application Layer / Use Cases (40% Effort)
We need to create the "orchestrators" that the API will call.

1.  **`CreateTemplateUseCase`:**
    *   Logic to assemble a Composite Product structure from DTOs.
    *   Mark it as a template.
    *   Save it to the Repo.

2.  **`InstantiateProductUseCase`:**
    *   **Input:** `template_id` (UUID), `material_assignments` (Map of `{component_id: material_id}`).
    *   **Logic:**
        1.  Fetch Template from Repo.
        2.  Fetch Concrete Materials from Repo.
        3.  Initialize `CompositeProductBuilder(template)`.
        4.  Iterate through assignments and call `builder.assign_material()`.
        5.  Validate `product.is_complete`.
        6.  Save the new Concrete Product to Repo.
    *   **Output:** The ID of the new concrete product.

###  Phase 3: API Layer (40% Effort)
Expose the functionality via REST endpoints.

*   `POST /products/templates`: Create a new template structure.
*   `GET /products/templates/{id}/requirements`: Returns the list of "holes" to fill (Component IDs + Material Types). *Useful for the Frontend UI to show dropdowns.*
*   `POST /products/templates/{id}/instantiate`: The action trigger.

---

## 4. Immediate Next Steps (For next session)

1.  **Verify Persistence:** Write an integration test using the actual DB (Docker) to save a generic Template.
2.  **Implement Use Case:** Write the `InstantiateProductUseCase`.
3.  **Wiring:** Connect it to a temporary endpoint or test script to demonstrate the full flow (Template -> Builder -> New Product -> DB).
