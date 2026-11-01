export type Project = {
  slug: string; title: string; category: 'fullstack' | 'backend' | 'desktop';
  categoryLabel: string; summary: string; description: string; stack: string[];
  repository: string; repositoryLabel: string; highlights: string[]; classification: string;
};

export const projects: Project[] = [
  {
    slug: 'huffman-compressor-pro', title: 'Huffman Compressor Pro',
    category: 'fullstack', categoryLabel: 'Full Stack',
    summary: 'Aplicación web para compresión y descompresión sin pérdida mediante el algoritmo de Huffman.',
    description: 'Proyecto que documenta una arquitectura separada entre una interfaz Next.js y un backend FastAPI. Incluye compresión, formato binario propio, visualización del árbol de Huffman y análisis de métricas.',
    stack: ['Next.js 14','React 18','TypeScript','Tailwind CSS','Python 3.11','FastAPI','Docker'],
    repository: 'https://github.com/Pudin0120/huffman-compressor-pro', repositoryLabel: 'Repositorio independiente',
    highlights: ['Separación de frontend y backend mediante API REST.','Compresión y descompresión de texto con el algoritmo de Huffman.','Visualización del árbol, frecuencias y códigos.','Métricas documentadas: ratio, entropía y longitud media del código.'],
    classification: 'Proyecto personal / académico'
  },
  {
    slug: 'banking-portal-api', title: 'Banking Portal API', category: 'backend', categoryLabel: 'Backend',
    summary: 'Proyecto backend Java con componentes de seguridad, persistencia, validación y caché.',
    description: 'Aplicación Spring Boot cuyo archivo Maven declara Java 17 y módulos Spring Web, Spring Security, Spring Data JPA, validación, correo y caché. La configuración también declara conectores MySQL y Redis, además de recursos Docker.',
    stack: ['Java 17','Spring Boot 3.3.1','Spring Security','Spring Data JPA','MySQL','Redis','Docker'],
    repository: 'https://github.com/Pudin0120/Portafolio/tree/main/Projects/BankingPortal-API-main', repositoryLabel: 'Código dentro del catálogo',
    highlights: ['Backend basado en Spring Boot 3.3.1.','Persistencia con Spring Data JPA y conector MySQL.','Dependencias de seguridad, validación y documentación OpenAPI.','Dependencias de caché y Redis; recursos Docker incluidos.'],
    classification: 'Proyecto personal / académico'
  },
  {
    slug: 'inventory-management-system', title: 'Inventory Management System', category: 'desktop', categoryLabel: 'Aplicación de escritorio',
    summary: 'Aplicación Java para gestión de inventario y facturación, con interfaz de escritorio y recursos SQL.',
    description: 'Proyecto Maven con componentes JavaFX, entidades relacionadas con productos, clientes y facturas, controladores de interfaz y recursos SQL.',
    stack: ['Java','JavaFX 11.0.2','Maven','SQL','JUnit 5.7.1'],
    repository: 'https://github.com/Pudin0120/Portafolio/tree/main/Projects/inventory-management-system-main', repositoryLabel: 'Código dentro del catálogo',
    highlights: ['Interfaz construida con componentes JavaFX.','Entidades documentadas para productos, clientes y facturación.','Gestión de dependencias mediante Maven.','Recursos SQL y dependencias de pruebas declaradas en el POM.'],
    classification: 'Proyecto personal / académico'
  }
];