# Patron de Persistencia en Repositorios

## Problema Identificado

Al implementar la asignacion de tasks (`assigned_user_id`), se encontro que aunque el valor se asignaba correctamente en memoria y el frontend recibia los datos actualizados, **la base de datos nunca reflejaba estos cambios**.

### Sintomas del Problema

1. OK El objeto de dominio se modificaba correctamente en memoria
2. OK El DTO devuelto al frontend contenia los datos actualizados
3. OK Los logs indicaban que todo funcionaba
4. ERROR La base de datos permanecia sin cambios (campos NULL o valores antiguos)
5. ERROR Al refrescar o consultar posteriormente, los datos se perdian

## Causa Raiz

El problema tenia dos componentes:

### 1. Retorno de Objetos "Stale" (Obsoletos)

```python
# ERROR INCORRECTO - Devuelve el objeto de entrada, no el de la BD
def save(self, entity: Entity) -> Entity:
    model = self._to_model(entity)
    self.db_session.merge(model)
    self.db_session.flush()
    return entity  #  Devuelve el parametro, no un objeto fresh desde BD
```

**Problema**: El objeto devuelto no refleja el estado real de la base de datos. Cualquier valor calculado por la BD (timestamps, triggers, etc.) no se incluye.

### 2. Commit No Ejecutado

Aunque se esperaba que `get_db_session()` hiciera commit automaticamente al final de cada request, en ciertos contextos esto no ocurria, resultando en:

- `flush()` escribe a la BD dentro de la transaccion OK
- Pero sin `commit()`, la transaccion se descarta al finalizar ERROR
- Los cambios se pierden silenciosamente ERROR

## Solucion: Patron de Persistencia Correcto

### Implementacion en `save()`

```python
def save(self, entity: Entity) -> Entity:
    """
    Guarda o actualiza una entidad en la base de datos.
    
    NOTE: COMMITS immediately to ensure data persistence.
    This is necessary because get_db_session() auto-commit is not reliable in all contexts.
    
    Returns:
        Fresh domain object constructed from persisted ORM model
    """
    # Check if entity exists
    stmt = select(Model).where(Model.id == entity.id)
    existing = self.db_session.execute(stmt).scalar_one_or_none()
    
    if existing:
        # Update existing
        self._update_model_from_domain(existing, entity)
        model = existing
    else:
        # Create new
        model = self._to_model(entity)
        self.db_session.add(model)
    
    # OK CRITICAL: Commit to persist changes immediately
    self.db_session.commit()
    
    # OK CRITICAL: Refresh to get updated values from DB
    self.db_session.refresh(model)
    
    # OK CRITICAL: Return fresh domain object from ORM model
    return self._to_domain(model)
```

### Puntos Clave

1. **`commit()` Explicito**: No confiar en commits automaticos
2. **`refresh()` Despues del Commit**: Obtener el estado real de la BD
3. **`_to_domain()` desde el Modelo ORM**: Construir objeto fresh, NO retornar el parametro

## Aplicacion del Patron

### OK Repositorios Corregidos

- `PostgresTaskRepository` OK
- `PostgresProductRepository` OK
- `PostgresWorkRepository` OK
- `PostgresMaterialRepository` OK
- `PostgresClientRepository` OK
- `PostgresUnitOfMeasureRepository` OK
- `PostgresMaterialTypeRepository` OK
- `PayrollRepository` OK
- `PayrollHistoryRepository` OK

### Checklist de Validacion

Al implementar o revisar un repositorio, verificar:

- [ ] El metodo `save()` hace `commit()` explicito?
- [ ] Hace `refresh()` despues del commit?
- [ ] Devuelve `self._to_domain(model)` en lugar del parametro?
- [ ] El metodo `_update_model_from_domain()` actualiza TODOS los campos?
- [ ] Los campos nullable se manejan correctamente?

## Casos Especiales

### Repositorios Anidados (Work  Tasks)

Cuando un repositorio llama a otros repositorios (ej: `WorkRepository.save()` llama a `TaskRepository.save()`):

```python
def save(self, work: Work) -> Work:
    # Save work
    model = self._to_model(work)
    self.db_session.merge(model)
    self.db_session.flush()  # OK Assign IDs
    
    # Save related tasks (cada uno hace su propio commit)
    for task in work.tasks:
        self.task_repo.save(task)  # OK Commits internamente
    
    # Final refresh y retorno
    self.db_session.refresh(model)
    return self._to_domain(model)
```

**Importante**: Cada repositorio es responsable de su propio commit.

## Antipatrones a Evitar

### ERROR Retornar el Parametro

```python
def save(self, entity):
    model = self._to_model(entity)
    self.db_session.merge(model)
    self.db_session.flush()
    return entity  # ERROR MAL: No refleja BD
```

### ERROR Confiar en Commit Automatico

```python
def save(self, entity):
    model = self._to_model(entity)
    self.db_session.merge(model)
    # ERROR MAL: No hay commit explicito
    return self._to_domain(model)
```

### ERROR No Hacer Refresh

```python
def save(self, entity):
    model = self._to_model(entity)
    self.db_session.merge(model)
    self.db_session.commit()
    # ERROR MAL: No refresh, puede tener datos obsoletos
    return self._to_domain(model)
```

## Testing

Para verificar que la persistencia funciona correctamente:

```python
def test_persistence():
    # Create/modificar entidad
    entity.some_field = "new_value"
    
    # Save
    saved = repo.save(entity)
    
    # Verificar que el retorno tiene el valor
    assert saved.some_field == "new_value"
    
    # Limpiar sesion para forzar lectura desde BD
    db.expunge_all()
    
    # Re-leer desde BD
    from_db = repo.get_by_id(entity.id)
    
    # OK Debe tener el valor persistido
    assert from_db.some_field == "new_value"
```

## Resumen

**Regla de Oro**: Los repositorios SIEMPRE deben devolver objetos construidos desde la base de datos despues de un `commit()` + `refresh()`, NUNCA el objeto que recibieron como parametro.

Esto garantiza:
- OK Persistencia real en la BD
- OK Valores calculados/generados por la BD (timestamps, sequences)
- OK Consistencia entre memoria y BD
- OK Eliminacion de bugs sutiles de "datos fantasma"
