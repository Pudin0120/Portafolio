# Gestion de Base de Datos con SQLAlchemy

**Estado**: OK Sistema Configurado

##  Regla Principal

 **NUNCA create archivos `.sql` manualmente**  
OK **SIEMPRE usar SQLAlchemy + `create_tables.py`**

##  Como Gestionar Base de Datos

### 1. Definir Modelo SQLAlchemy
Create en: `app/infrastructure/adapters/db/models/`

```python
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.infrastructure.adapters.db.database import Base

class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
```

### 2. Importar en create_tables.py
```python
from app.infrastructure.adapters.db.models.my_model import MyModel
```

### 3. Create Tablas
```bash
docker exec -it fastapi-backend-dev python create_tables.py
```

### 4. Verificar
```bash
docker exec postgres-db-dev psql -U user -d serviperfiles_db -c "\dt"
```

##  Estado Actual de Tablas

### OK Existentes
- `units_of_measure` - Unidades de medida
- `material_types` - Tipos de materials
- `users` - Users
- `roles` - Roles de user

###  Por Create
- `materials` - Inventario de materials
- `products` - Catalogo de products
- `product_components` - Composicion de products

##  Proximo Paso

Implementar modelos para `materials`, `products` y `product_components`.

Ver: `docs/PRODUCT_PERSISTENCE_IMPLEMENTATION.md`
