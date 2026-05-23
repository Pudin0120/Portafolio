# Proyecto ServiPerfiles - Frontend React

Sistema de gestiAn de users con autenticaciAn Firebase y roles dinAmicos, construido bajo una arquitectura modular orientada a SaaS.

## Ys TecnologAas

- **React 19** con TypeScript
- **Vite** como bundler
- **HeroUI** (ex NextUI) + Tailwind CSS 4
- **Bun** como gestor de paquetes y runtime
- **Firebase** para autenticaciAn
- **Infisical** para gestiAn de secretos

## Y" Roles del Sistema

| Rol             | Acceso                             |
| :-------------- | :--------------------------------- |
| **SUPER_ADMIN** | Control total del sistema          |
| **MANAGER**     | GestiAn administrativa de users |
| **SUPERVISOR**  | GestiAn de equipos y tasks        |
| **EMPLOYEE**    | VisualizaciAn de perfil y nAmina   |

## Y-i Estructura del Proyecto

El proyecto sigue una arquitectura modular y escalable. Para mAs detalles tA(c)cnicos sobre la organizaciAn de carpetas y principios de diseAo, consulta:

- [Y-i Arquitectura del Proyecto](./ARCHITECTURE.md)

## Y"s DocumentaciAn Adicional

- [Y GuAa de Flujo de Work (Git)](./GUIDE.md) - **LEER ANTES DE EMPEZAR**
- [Y- GuAa para Agentes AI](./AGENTS.md) - EstAndares para desarrollo asistido por IA.

## Y" GestiAn de Secretos (Infisical)

Este proyecto utiliza **Infisical** para inyectar variables de entorno de forma segura.

1. Instala [Infisical CLI](https://infisical.com/docs/cli/overview).
2. Ejecuta `infisical auth login`.
3. Usa `bun run dev` o `bun run build` para inyectar los secretos automAticamente.

## Y" InstalaciAn y Uso

```bash
# Instalar dependencias
bun install

# Desarrollo
bun run dev

# Build de producciAn
bun run build
```

## Yi Desarrollo (TypeScript + React 19)

### Ejemplo de componente profesional:

```tsx
import { type FC } from "react";
import { Button } from "@heroui/react";
import { useAuth } from "@hooks/useAuth";

interface Props {
  label: string;
  onPress?: () => void;
}

export const ActionButton: FC<Props> = ({ label, onPress }) => {
  const { user } = useAuth();

  return (
    <Button color="primary" onPress={onPress}>
      {label}
    </Button>
  );
};
```

## Y API Endpoints

Consulta la documentaciAn interna en `src/services/` para ver los servicios disponibles o espera a la prAxima actualizaciAn de la **GuAa de Endpoints**.

## Y' Contribuir

1. Asegurate de estar en la rama `dev`.
2. CreA una rama nueva con el prefijo correspondiente: `git checkout -b feature/nombre-mejora`.
3. SeguA las normas de commit y flujo explicadas en [GUIDE.md](./GUIDE.md).
4. AbrA un Pull Request hacia `dev`.

