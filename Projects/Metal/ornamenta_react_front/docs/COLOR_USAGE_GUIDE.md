# Guia de Uso de Colores

## Paleta de Marca Aprobada

### Naranja Oscuro (Color Primario)
- **Principal**: `#e67e22` - Para acciones principales
- **Mas oscuro**: `#d35400` - Para hover/estados activos
- **Uso**: Botones principales, elementos destacados, navegacion activa

### Aguamarina/Verde Agua (Color Secundario)
- **Principal**: `#1abc9c` - Para acciones secundarias
- **Mas oscuro**: `#16a085` - Para hover
- **Uso**: Botones secundarios, information complementaria

## Como Aplicar

### En Tailwind CSS

```tsx
// Boton naranja oscuro
<button className="bg-brand-orange-600 hover:bg-brand-orange-700 text-white">
  Save
</button>

// Boton aguamarina
<button className="bg-brand-teal-600 hover:bg-brand-teal-500 text-white">
  Informacion
</button>
```

### En Estilos Inline

```tsx
style={{
  backgroundColor: '#e67e22', // Naranja oscuro
  color: '#ffffff',
}}
```

## Componentes Reutilizables

### Botones Estandarizados

Ya no uses `<Button color="primary">` de HeroUI directamente. Usa los componentes estandarizados:

```tsx
import { PrimaryButton, SecondaryButton } from '@components/common';

// Accion principal
<PrimaryButton>Save</PrimaryButton>

// Accion secundaria
<SecondaryButton>Cancel</SecondaryButton>
```

### Mensajes de Estado

```tsx
import { StatusMessage } from '@components/common';

<StatusMessage type="success">
  OK Operacion exitosa
</StatusMessage>

<StatusMessage type="error">
  ERROR Error al procesar
</StatusMessage>
```

## Reglas Importantes

### OK HACER

1. **Usar naranja oscuro (#e67e22)** para la accion principal de cada pantalla
2. **Usar aguamarina (#1abc9c)** para acciones secundarias
3. **Usar rojo** solo para acciones peligrosas (delete, cancel irreversible)
4. **Mantener los semaforos** para estados (exito, error, advertencia, info)

### ERROR NO HACER

1. No usar azul para botones principales (solo para info)
2. No usar verde para acciones primarias (solo para exito)
3. No mezclar colores sin proposito
4. No usar amarillo para acciones normales (solo para advertencias)

## Ejemplos de Uso

### Formulario

```tsx
<div className="flex justify-end gap-3 mt-6">
  <Button variant="light" onPress={onCancel}>
    Cancel
  </Button>
  <PrimaryButton onPress={onSubmit}>
    Save
  </PrimaryButton>
</div>
```

### Tabla con Acciones

```tsx
<div className="flex gap-2">
  <Button size="sm" variant="light" color="primary">
    Ver
  </Button>
  <Button size="sm" variant="light">
    Edit
  </Button>
  <DangerButton size="sm">
    Delete
  </DangerButton>
</div>
```

## Migracion

### Antes
```tsx
<Button color="primary">Save</Button>
<Button color="success">Confirmar</Button>
```

### Despues
```tsx
<PrimaryButton>Save</PrimaryButton> {/* Naranja oscuro */}
<SecondaryButton>Informacion</SecondaryButton> {/* Aguamarina */}
<SuccessButton>Confirmar</SuccessButton> {/* Verde - solo para exito */}
```

## Progreso de Migracion

- OK Sistema de colores definido
- OK Tailwind config actualizado
- OK Componentes estandarizados creados
- OK Guias de uso creadas
-  Migrando componentes existentes (en progreso)


