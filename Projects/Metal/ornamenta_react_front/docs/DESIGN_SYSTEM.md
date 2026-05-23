# Design System - Serviperfiles

## Paleta de Colores

### Colores de Marca

#### Naranja Oscuro (Primario)
- **Usar para**: Acciones principales, botones primarios, elementos destacados
- **600**: `#e67e22` - Color principal
- **700**: `#d35400` - Hover/estado active
- **Ejemplo**: Botones "Save", "Create", acciones principales

#### Aguamarina/Verde Agua (Secundario)
- **Usar para**: Acciones secundarias, information complementaria
- **600**: `#1abc9c` - Color principal
- **500**: `#16a085` - Hover
- **Ejemplo**: Botones "Informacion", "Detalles"

### Estados (Semaforos)

#### Exito (Verde)
- **Usar para**: Operaciones exitosas, confirmaciones
- Clases: `bg-green-100 border-green-300 text-green-800`
- Icono: `CheckCircle` en color verde

#### Error (Rojo)
- **Usar para**: Errores, operaciones fallidas
- Clases: `bg-red-100 border-red-300 text-red-800`
- Icono: `XCircle` en color rojo

#### Advertencia (Amarillo)
- **Usar para**: Advertencias, atencion requerida
- Clases: `bg-yellow-100 border-yellow-300 text-yellow-800`
- Icono: `AlertCircle` en color amarillo

#### Info (Azul)
- **Usar para**: Informacion, tips, ayuda
- Clases: `bg-blue-100 border-blue-300 text-blue-800`
- Icono: `Info` en color azul

## Componentes Estandar

### Botones

```tsx
// Boton primario (naranja oscuro)
<PrimaryButton>Save</PrimaryButton>

// Boton secundario (aguamarina)
<SecondaryButton>Cancel</SecondaryButton>

// Boton de exito
<SuccessButton>Confirmar</SuccessButton>

// Boton de peligro/delete
<DangerButton>Delete</DangerButton>

// Con variantes
<StyledButton colorScheme="primary" variant="outlined">
  Outlined Button
</StyledButton>
```

### Mensajes de Estado

```tsx
// Mensaje de exito
<StatusMessage type="success">
  Operacion realizada con exito
</StatusMessage>

// Mensaje de error
<StatusMessage type="error">
  Error al procesar la solicitud
</StatusMessage>

// Mensaje de advertencia
<StatusMessage type="warning">
  Please verifica la information
</StatusMessage>

// Mensaje de information
<StatusMessage type="info">
  Tip: Puedes edit este campo mas tarde
</StatusMessage>
```

### Colores en Tailwind

```css
/* Naranja oscuro */
bg-brand-orange-600  /* Principal */
bg-brand-orange-700  /* Hover */
text-brand-orange-600
border-brand-orange-600

/* Aguamarina */
bg-brand-teal-600    /* Principal */
bg-brand-teal-500    /* Hover */
text-brand-teal-600
border-brand-teal-600
```

## Reglas de Uso

### Botones

1. **Una accion principal por pantalla**: Usa naranja oscuro
2. **Multiples acciones**: 
   - Principal: Naranja oscuro
   - Secundarias: Aguamarina
   - DANGEROUS: Rojo (delete, cancel irreversible)
3. **Estados deshabilitados**: Automatico con opacidad 50%
4. **Iconos**: Lucide React, tamano consistente (w-4 h-4 o w-5 h-5)

### Colores de Tabla

- **Headers**: Fondo gris claro (`bg-gray-50`)
- **Rows**: Alternar entre blanco y gris muy claro
- **Bordes**: Gris suave (`border-gray-200`)
- **Hover**: Resaltar con naranja suave (`hover:bg-brand-orange-50`)

### Navegacion

- **Sidebar**: Naranja oscuro (#2c3e50) con items en naranja (#f39c12)
- **Header**: Blanco con bordes grises
- **Breadcrumbs**: Azul estandar para enlaces

## Ejemplos Visuales

### Formularios

```tsx
// Layout estandar
<div className="max-w-2xl mx-auto p-6">
  <h2 className="text-2xl font-bold text-gray-900 mb-6">
    Nuevo {Entity}
  </h2>
  
  <form className="space-y-6">
    {/* Campos */}
    
    <div className="flex justify-end gap-3">
      <SecondaryButton>Cancel</SecondaryButton>
      <PrimaryButton>Save</PrimaryButton>
    </div>
  </form>
</div>
```

### Listas/Tablas

```tsx
<div className="rounded-lg border border-gray-200">
  <Table>
    <TableHeader>
      <TableColumn>
        <span className="text-brand-orange-600 font-semibold">
          Nombre
        </span>
      </TableColumn>
    </TableHeader>
    <TableBody>
      {/* Rows */}
    </TableBody>
  </Table>
</div>
```

## Consistencia

- **Usar siempre los mismos componentes**: `StyledButton`, `StatusMessage`
- **Tamanos**: Mantener coherencia (sm, md, lg)
- **Espaciados**: Usar el sistema de spacing de Tailwind
- **Tipografia**: Sistema tipografico consistente


