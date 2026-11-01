export type Project = {
  slug: string; title: string; category: 'fullstack' | 'backend' | 'desktop';
  categoryLabel: string; summary: string; description: string; stack: string[];
  repository: string; repositoryLabel: string; highlights: string[]; classification: string;
};

// Catálogo ampliado: proyectos detallados + GERICARE destacado + todos los directorios de Projects/.
export const projects: Project[] = [
  {
    "slug": "huffman-compressor-pro",
    "title": "Huffman Compressor Pro",
    "category": "fullstack",
    "categoryLabel": "Full Stack",
    "summary": "Aplicación web para compresión y descompresión sin pérdida mediante el algoritmo de Huffman.",
    "description": "Proyecto que documenta una arquitectura separada entre una interfaz Next.js y un backend FastAPI. Incluye compresión, formato binario propio, visualización del árbol de Huffman y análisis de métricas.",
    "stack": [
      "Next.js 14",
      "React 18",
      "TypeScript",
      "Tailwind CSS",
      "Python 3.11",
      "FastAPI",
      "Docker"
    ],
    "repository": "https://github.com/Pudin0120/huffman-compressor-pro",
    "repositoryLabel": "Repositorio independiente",
    "highlights": [
      "Separación de frontend y backend mediante API REST.",
      "Compresión y descompresión de texto con el algoritmo de Huffman.",
      "Visualización del árbol, frecuencias y códigos.",
      "Métricas documentadas: ratio, entropía y longitud media del código."
    ],
    "classification": "Proyecto personal / académico"
  },
  {
    "slug": "banking-portal-api",
    "title": "Banking Portal API",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "Proyecto backend Java con componentes de seguridad, persistencia, validación y caché.",
    "description": "Aplicación Spring Boot cuyo archivo Maven declara Java 17 y módulos Spring Web, Spring Security, Spring Data JPA, validación, correo y caché. La configuración también declara conectores MySQL y Redis, además de recursos Docker.",
    "stack": [
      "Java 17",
      "Spring Boot 3.3.1",
      "Spring Security",
      "Spring Data JPA",
      "MySQL",
      "Redis",
      "Docker"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/BankingPortal-API-main",
    "repositoryLabel": "Código dentro del catálogo",
    "highlights": [
      "Backend basado en Spring Boot 3.3.1.",
      "Persistencia con Spring Data JPA y conector MySQL.",
      "Dependencias de seguridad, validación y documentación OpenAPI.",
      "Dependencias de caché y Redis; recursos Docker incluidos."
    ],
    "classification": "Proyecto personal / académico"
  },
  {
    "slug": "inventory-management-system",
    "title": "Inventory Management System",
    "category": "desktop",
    "categoryLabel": "Aplicación de escritorio",
    "summary": "Aplicación Java para gestión de inventario y facturación, con interfaz de escritorio y recursos SQL.",
    "description": "Proyecto Maven con componentes JavaFX, entidades relacionadas con productos, clientes y facturas, controladores de interfaz y recursos SQL.",
    "stack": [
      "Java",
      "JavaFX 11.0.2",
      "Maven",
      "SQL",
      "JUnit 5.7.1"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/inventory-management-system-main",
    "repositoryLabel": "Código dentro del catálogo",
    "highlights": [
      "Interfaz construida con componentes JavaFX.",
      "Entidades documentadas para productos, clientes y facturación.",
      "Gestión de dependencias mediante Maven.",
      "Recursos SQL y dependencias de pruebas declaradas en el POM."
    ],
    "classification": "Proyecto personal / académico"
  },
  {
    "slug": "gericare",
    "title": "GERICARE — Gestión geriátrica",
    "category": "fullstack",
    "categoryLabel": "HealthTech",
    "summary": "Plataforma orientada a la gestión clínica y operativa geriátrica, con enfoque mobile-first.",
    "description": "Proyecto de HealthTech descrito como una plataforma SaaS para gestión clínica y operativa geriátrica, con kardex electrónico, Valoración Geriátrica Integral y arquitectura multi-tenant. Su código no apareció como carpeta independiente en el inventario de Projects de este repositorio; por transparencia, el enlace lleva a la búsqueda del nombre en el perfil de GitHub.",
    "stack": [
      "Next.js 16",
      "TypeScript",
      "Supabase",
      "PostgreSQL",
      "Tailwind CSS",
      "HL7 FHIR R4"
    ],
    "repository": "https://github.com/Pudin0120?tab=repositories&q=GERICARE",
    "repositoryLabel": "Buscar repositorio GERICARE",
    "highlights": [
      "Gestión clínica y operativa geriátrica.",
      "Kardex electrónico y Valoración Geriátrica Integral.",
      "Arquitectura multi-tenant y políticas de acceso a datos descritas para el proyecto.",
      "El código no se encontró como directorio dentro de Projects/ al generar este catálogo."
    ],
    "classification": "HealthTech / proyecto destacado"
  },
  {
    "slug": "repo-2048",
    "title": "2048",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «2048» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/2048. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/2048",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-add-your-code-hs",
    "title": "Add Your Code Hs",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Add Your Code Hs» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Add Your Code Hs. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Add%20Your%20Code%20Hs",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-admission-counselling-system",
    "title": "Admission counselling system",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Admission counselling system» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Admission-counselling-system. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Admission-counselling-system",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-ai-riddle-game",
    "title": "AI Riddle Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «AI Riddle Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/AI Riddle Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/AI%20Riddle%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-algorithms",
    "title": "Algorithms",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Algorithms» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Algorithms. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Algorithms",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-app",
    "title": "app",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «app» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/app. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/app",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-ascii-art",
    "title": "Ascii art",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Ascii art» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Ascii_art. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Ascii_art",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-atm",
    "title": "ATM",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «ATM» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/ATM. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/ATM",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-atm-interface",
    "title": "ATM interface",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «ATM interface» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/ATM interface. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/ATM%20interface",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-attendance",
    "title": "Attendance",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Attendance» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Attendance. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Attendance",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-back-end-chat-api",
    "title": "back end chat API",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "Proyecto «back end chat API» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/back-end--chat-api. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/back-end--chat-api",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-banking-application",
    "title": "banking application",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «banking application» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/banking application. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/banking%20application",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-bankingportal-api-main",
    "title": "BankingPortal API main",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "Proyecto «BankingPortal API main» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/BankingPortal-API-main. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/BankingPortal-API-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-basic-bank-system",
    "title": "Basic Bank System",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Basic Bank System» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Basic_Bank_System. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Basic_Bank_System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-billing-system",
    "title": "Billing system",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Billing system» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Billing-system. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Billing-system",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-binarydecimalconverto",
    "title": "BinaryDecimalConverto",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «BinaryDecimalConverto» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/BinaryDecimalConverto. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/BinaryDecimalConverto",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-blogbackend-main",
    "title": "BlogBackend main",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "Proyecto «BlogBackend main» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/BlogBackend-main. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/BlogBackend-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-brick-breaker-game",
    "title": "Brick Breaker Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Brick Breaker Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Brick-Breaker-Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Brick-Breaker-Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-budget-tracker-project",
    "title": "Budget Tracker project",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Budget Tracker project» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Budget Tracker project. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Budget%20Tracker%20project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-calculator-using-java",
    "title": "Calculator using Java",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Calculator using Java» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Calculator using Java. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Calculator%20using%20Java",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-calculator-oops",
    "title": "Calculator OOPS",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Calculator OOPS» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Calculator-OOPS. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Calculator-OOPS",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-calculator-project",
    "title": "Calculator project",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Calculator project» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Calculator-project. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Calculator-project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-calorie-calculator",
    "title": "Calorie Calculator",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Calorie Calculator» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Calorie Calculator. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Calorie%20Calculator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-chat-project",
    "title": "Chat Project",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Chat Project» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Chat Project. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Chat%20Project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-chessgame",
    "title": "ChessGame",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «ChessGame» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/ChessGame. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/ChessGame",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-clouddevopsproject-main",
    "title": "CloudDevOpsProject main",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "Proyecto «CloudDevOpsProject main» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/CloudDevOpsProject-main. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/CloudDevOpsProject-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-cloudscripts",
    "title": "cloudscripts",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "Proyecto «cloudscripts» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/cloudscripts. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/cloudscripts",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-clue-simulator",
    "title": "Clue Simulator",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Clue Simulator» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Clue Simulator. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Clue%20Simulator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-conversion",
    "title": "Conversion",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Conversion» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Conversion. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Conversion",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-convert-jpeg-to-png",
    "title": "Convert JPEG to PNG",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Convert JPEG to PNG» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Convert_JPEG_to_PNG. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Convert_JPEG_to_PNG",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-correct-number-guess-game",
    "title": "Correct Number Guess Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Correct Number Guess Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Correct Number Guess Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Correct%20Number%20Guess%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-countdown-timer-using-python",
    "title": "Countdown Timer using Python",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Countdown Timer using Python» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Countdown Timer using Python. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Countdown%20Timer%20using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-crypto-image-and-text-encryption-decryption",
    "title": "Crypto Image and Text Encryption Decryption",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Crypto Image and Text Encryption Decryption» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Crypto-Image and Text Encryption Decryption. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Crypto-Image%20and%20Text%20Encryption%20Decryption",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-currency-converter",
    "title": "Currency Converter",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Currency Converter» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Currency Converter. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Currency%20Converter",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-currency-converter-using-java",
    "title": "Currency Converter using Java",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Currency Converter using Java» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Currency Converter using Java. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Currency%20Converter%20using%20Java",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-currency-convertor",
    "title": "currency Convertor",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «currency Convertor» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/currency Convertor. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/currency%20Convertor",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-data-visualisation",
    "title": "Data Visualisation",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Data Visualisation» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Data Visualisation. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Data%20Visualisation",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-datastructures",
    "title": "DataStructures",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «DataStructures» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/DataStructures. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/DataStructures",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-department-wise-salary-calculation",
    "title": "Department Wise Salary Calculation",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Department Wise Salary Calculation» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Department-Wise Salary Calculation. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Department-Wise%20Salary%20Calculation",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-diamond-shipping-project",
    "title": "Diamond shipping project",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Diamond shipping project» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Diamond shipping project. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Diamond%20shipping%20project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-dice-simulator",
    "title": "Dice Simulator",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Dice Simulator» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Dice Simulator. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Dice%20Simulator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-digital-clock",
    "title": "Digital Clock",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Digital Clock» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Digital Clock. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Digital%20Clock",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-dino-game-java",
    "title": "Dino Game Java",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Dino Game Java» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Dino_Game_java. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Dino_Game_java",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-dns-record-using-python",
    "title": "DNS Record using Python",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «DNS Record using Python» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/DNS Record using Python. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/DNS%20Record%20using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-dns-record",
    "title": "Dns record",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Dns record» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Dns_record. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Dns_record",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-duplicate-files-remover",
    "title": "Duplicate files remover",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Duplicate files remover» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Duplicate files remover. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Duplicate%20files%20remover",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-e-commerce-project-springboot-master",
    "title": "E commerce project springBoot master",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «E commerce project springBoot master» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/E-commerce-project-springBoot-master. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/E-commerce-project-springBoot-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-e-health-care-management",
    "title": "E Health Care Management",
    "category": "backend",
    "categoryLabel": "Salud y gestión clínica",
    "summary": "Proyecto del área de salud y gestión clínica incluido en el repositorio. Consulta el código y su README para conocer los detalles de ejecución.",
    "description": "Aplicación relacionada con la gestión de información del sector salud. La documentación disponible en la carpeta del proyecto es la referencia para confirmar su alcance, requisitos y forma de ejecución.",
    "stack": [
      "Java",
      "Gestión de salud",
      "Documentación"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/E-Health%20Care%20Management",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Salud / proyecto académico"
  },
  {
    "slug": "repo-email-generator",
    "title": "Email Generator",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Email Generator» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Email_Generator. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Email_Generator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-employee",
    "title": "Employee",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Employee» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Employee. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Employee",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-employer-worker-registration-system-main",
    "title": "employer worker registration system main",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «employer worker registration system main» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/employer-worker-registration-system-main. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/employer-worker-registration-system-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-encrypt-the-password",
    "title": "Encrypt the Password",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Encrypt the Password» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Encrypt-the-Password. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Encrypt-the-Password",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-eng-dictionary",
    "title": "Eng Dictionary",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Eng Dictionary» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Eng_Dictionary. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Eng_Dictionary",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-exchange-indian-currency",
    "title": "Exchange Indian Currency",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Exchange Indian Currency» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Exchange-Indian-Currency. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Exchange-Indian-Currency",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-face-recognition-using-python",
    "title": "Face Recognition Using Python",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Face Recognition Using Python» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Face Recognition Using Python. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Face%20Recognition%20Using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-fee-management-system",
    "title": "Fee Management System",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Fee Management System» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Fee Management System. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Fee%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-fee-management-system-2",
    "title": "Fee Management System",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Fee Management System» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Fee-Management-System. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Fee-Management-System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-fibonacci",
    "title": "Fibonacci",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Fibonacci» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Fibonacci. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Fibonacci",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-finance",
    "title": "Finance",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Finance» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Finance. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Finance",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-fota-graduation-project-2022-main",
    "title": "FOTA Graduation Project 2022 main",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «FOTA Graduation Project 2022 main» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/FOTA_Graduation-Project-2022-main. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/FOTA_Graduation-Project-2022-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-geocoding-of-a-webpage-using-python",
    "title": "Geocoding of a Webpage using Python",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Geocoding of a Webpage using Python» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Geocoding of a Webpage using Python. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Geocoding%20of%20a%20Webpage%20using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-get-current-time",
    "title": "Get Current Time",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Get Current Time» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Get Current Time. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Get%20Current%20Time",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-graduation-project-master",
    "title": "Graduation Project master",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Graduation Project master» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Graduation-Project-master. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Graduation-Project-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-graduationproject-master",
    "title": "GraduationProject master",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «GraduationProject master» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/GraduationProject-master. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/GraduationProject-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-guess-the-number",
    "title": "Guess the number",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Guess the number» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Guess the number. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Guess%20the%20number",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-guess-the-number-game",
    "title": "Guess The Number Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Guess The Number Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Guess The Number Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Guess%20The%20Number%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-guessthenumbergame",
    "title": "GuessTheNumberGame",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «GuessTheNumberGame» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/GuessTheNumberGame. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/GuessTheNumberGame",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-hospital-management-system",
    "title": "Hospital Management System",
    "category": "backend",
    "categoryLabel": "Salud y gestión clínica",
    "summary": "Proyecto del área de salud y gestión clínica incluido en el repositorio. Consulta el código y su README para conocer los detalles de ejecución.",
    "description": "Aplicación relacionada con la gestión de información del sector salud. La documentación disponible en la carpeta del proyecto es la referencia para confirmar su alcance, requisitos y forma de ejecución.",
    "stack": [
      "Java",
      "Gestión de salud",
      "Documentación"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Hospital%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Salud / proyecto académico"
  },
  {
    "slug": "repo-image-gallery",
    "title": "Image Gallery",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Image Gallery» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Image Gallery. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Image%20Gallery",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-img",
    "title": "img",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «img» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/img. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/img",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-internet-slang-s-dictionary",
    "title": "Internet Slang's Dictionary",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Internet Slang's Dictionary» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Internet Slang's Dictionary. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Internet%20Slang's%20Dictionary",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-inventory-management-system-main",
    "title": "inventory management system main",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «inventory management system main» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/inventory-management-system-main. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/inventory-management-system-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-java-server-client-networking-same-device",
    "title": "Java SERVER CLIENT NETWORKING(SAME DEVICE)",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "Proyecto «Java SERVER CLIENT NETWORKING(SAME DEVICE)» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/JAVA SERVER CLIENT NETWORKING(SAME DEVICE). Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/JAVA%20SERVER%20CLIENT%20NETWORKING(SAME%20DEVICE)",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-javacodes",
    "title": "JavaCodes",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «JavaCodes» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/JavaCodes. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/JavaCodes",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-javagame",
    "title": "javagame",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «javagame» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/javagame. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/javagame",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-languagetranslator-using-python",
    "title": "LanguageTranslator Using Python",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «LanguageTranslator Using Python» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/LanguageTranslator-Using-Python. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/LanguageTranslator-Using-Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-leetcode",
    "title": "Leetcode",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Leetcode» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Leetcode. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Leetcode",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-library-management",
    "title": "Library Management",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Library Management» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Library Management. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Library%20Management",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-libraryapp",
    "title": "LibraryApp",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «LibraryApp» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/LibraryApp. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/LibraryApp",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-librarymangement",
    "title": "LibraryMangement",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «LibraryMangement» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/LibraryMangement. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/LibraryMangement",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-listscanner",
    "title": "ListScanner",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «ListScanner» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/ListScanner. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/ListScanner",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-lost-and-found-application",
    "title": "Lost and found application",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Lost and found application» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Lost and found application. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Lost%20and%20found%20application",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-lucas-numbers",
    "title": "Lucas Numbers",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Lucas Numbers» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Lucas Numbers. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Lucas%20Numbers",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-maildemo",
    "title": "maildemo",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «maildemo» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/maildemo. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/maildemo",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-marvel-avengers-game",
    "title": "Marvel Avengers Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Marvel Avengers Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Marvel Avengers Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Marvel%20Avengers%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-math",
    "title": "Math",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Math» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Math. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Math",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-medical-store-shop-system-database-jar-files",
    "title": "Medical Store Shop System + Database + Jar Files",
    "category": "backend",
    "categoryLabel": "Salud y gestión clínica",
    "summary": "Proyecto del área de salud y gestión clínica incluido en el repositorio. Consulta el código y su README para conocer los detalles de ejecución.",
    "description": "Aplicación relacionada con la gestión de información del sector salud. La documentación disponible en la carpeta del proyecto es la referencia para confirmar su alcance, requisitos y forma de ejecución.",
    "stack": [
      "Java",
      "Gestión de salud",
      "Documentación"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Medical%20Store%20Shop%20System%20%2B%20Database%20%2B%20Jar%20Files",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Salud / proyecto académico"
  },
  {
    "slug": "repo-meditation-app",
    "title": "meditation app",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «meditation app» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/meditation-app. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/meditation-app",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-meme-generator",
    "title": "MEME GENERATOR",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «MEME GENERATOR» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/MEME GENERATOR. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/MEME%20GENERATOR",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-metal",
    "title": "Metal",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Metal» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Metal. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Metal",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-mims-master",
    "title": "MIMS master",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «MIMS master» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/MIMS-master. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/MIMS-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-minesweeper-using-python",
    "title": "MineSweeper Using Python",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «MineSweeper Using Python» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/MineSweeper Using Python. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/MineSweeper%20Using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-movie-ticket-booking-system",
    "title": "Movie Ticket Booking System",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Movie Ticket Booking System» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Movie Ticket Booking System. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Movie%20Ticket%20Booking%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-nbproject",
    "title": "nbproject",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «nbproject» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/nbproject. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/nbproject",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-online-book-store",
    "title": "Online Book Store",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Online Book Store» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Online Book Store. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Online%20Book%20Store",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-online-event-management-system",
    "title": "Online Event Management System",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Online Event Management System» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Online Event Management System. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Online%20Event%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-online-exam",
    "title": "online exam",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «online exam» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/online exam. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/online%20exam",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-online-voting-system",
    "title": "Online Voting System",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Online Voting System» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Online Voting System. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Online%20Voting%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-onlinebookstore-master",
    "title": "onlinebookstore master",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «onlinebookstore master» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/onlinebookstore-master. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/onlinebookstore-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-orderbook",
    "title": "OrderBook",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «OrderBook» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/OrderBook. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/OrderBook",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-otp-generator",
    "title": "OTP generator",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «OTP generator» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/OTP generator. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/OTP%20generator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-otp-generator-2",
    "title": "OTP generator",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «OTP generator» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/OTP-generator. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/OTP-generator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-password-generator",
    "title": "Password Generator",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Password Generator» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Password_Generator. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Password_Generator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-patience-game",
    "title": "Patience game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Patience game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Patience_game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Patience_game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-patterns",
    "title": "Patterns",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Patterns» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Patterns. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Patterns",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-petshop",
    "title": "petshop",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «petshop» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/petshop. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/petshop",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-pirate-adventure-game",
    "title": "Pirate Adventure Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Pirate Adventure Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Pirate_Adventure_Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Pirate_Adventure_Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-pong-game",
    "title": "Pong Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Pong Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Pong Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Pong%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-puzzle-game",
    "title": "Puzzle Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Puzzle Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Puzzle Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Puzzle%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-quiz-management-system",
    "title": "Quiz Management System",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Quiz Management System» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Quiz Management System. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Quiz%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-quiz-project",
    "title": "Quiz project",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Quiz project» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Quiz project. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Quiz%20project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-quizup",
    "title": "QuizUp",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «QuizUp» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/QuizUp. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/QuizUp",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-quotes",
    "title": "Quotes",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Quotes» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Quotes. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Quotes",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-randompasswordgenerator",
    "title": "RandomPasswordGenerator",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «RandomPasswordGenerator» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/RandomPasswordGenerator. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/RandomPasswordGenerator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-restaurant-management-system",
    "title": "Restaurant management system",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Restaurant management system» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Restaurant-management-system. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Restaurant-management-system",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-resume-builder",
    "title": "Resume Builder",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Resume Builder» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Resume Builder. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Resume%20Builder",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-resume-builder-java",
    "title": "resume builder Java",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «resume builder Java» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/resume-builder-java. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/resume-builder-java",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-riddle-game",
    "title": "Riddle Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Riddle Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Riddle Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Riddle%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-riddlequestgame",
    "title": "RiddleQuestGame",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «RiddleQuestGame» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/RiddleQuestGame. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/RiddleQuestGame",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-scientific-calculator",
    "title": "Scientific Calculator",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Scientific Calculator» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Scientific Calculator. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Scientific%20Calculator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-screenshot-using-python",
    "title": "Screenshot using Python",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Screenshot using Python» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Screenshot using Python. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Screenshot%20using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-search",
    "title": "Search",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Search» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Search. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Search",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-shop-management-system",
    "title": "Shop Management System",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Shop Management System» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Shop Management System. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Shop%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-simple-adventure-game",
    "title": "Simple Adventure Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Simple Adventure Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Simple Adventure Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Simple%20Adventure%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-simple-plagiarism-checker-project",
    "title": "Simple Plagiarism Checker Project",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Simple Plagiarism Checker Project» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Simple-Plagiarism-Checker-Project. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Simple-Plagiarism-Checker-Project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-snake-game",
    "title": "Snake game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Snake game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Snake game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Snake%20game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-software-piracy-control",
    "title": "Software Piracy Control",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Software Piracy Control» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Software Piracy Control. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Software%20Piracy%20Control",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-sorting",
    "title": "Sorting",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Sorting» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Sorting. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Sorting",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-src",
    "title": "src",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «src» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/src. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/src",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-stock-algorithm-js-sandbox",
    "title": "stock algorithm js sandbox",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «stock algorithm js sandbox» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/stock-algorithm-js-sandbox. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/stock-algorithm-js-sandbox",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-student-management-system",
    "title": "Student Management System",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Student Management System» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Student Management System. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Student%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-svg-file-generator",
    "title": "Svg File Generator",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Svg File Generator» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Svg File Generator. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Svg%20File%20Generator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-task-list",
    "title": "Task list",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Task list» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Task list. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Task%20list",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-task-tracker",
    "title": "Task Tracker",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Task Tracker» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Task_Tracker. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Task_Tracker",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-task-1-online-reservation-system",
    "title": "TASK 1 (Online Reservation System)",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «TASK 1 (Online Reservation System)» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/TASK-1 (Online Reservation System). Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/TASK-1%20(Online%20Reservation%20System)",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-temperature-converter",
    "title": "Temperature Converter",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Temperature Converter» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Temperature Converter. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Temperature%20Converter",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-temperatureconverter",
    "title": "TemperatureConverter",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «TemperatureConverter» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/TemperatureConverter. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/TemperatureConverter",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-the-metro-app",
    "title": "the metro app",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «the metro app» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/the_metro_app. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/the_metro_app",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-tic-tac-toe-python",
    "title": "Tic Tac Toe Python",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Tic Tac Toe Python» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Tic Tac Toe Python. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Tic%20Tac%20Toe%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-tic-tac-toe-game",
    "title": "Tic  Tac  Toe Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Tic  Tac  Toe Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Tic- Tac- Toe Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Tic-%20Tac-%20Toe%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-tic-tac-toe",
    "title": "Tic Tac Toe",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Tic Tac Toe» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Tic-Tac-Toe. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Tic-Tac-Toe",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-tictactoe",
    "title": "TicTacToe",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «TicTacToe» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/TicTacToe. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/TicTacToe",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-tictactoe-android-apk",
    "title": "TicTacToe Android apk",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «TicTacToe Android apk» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/TicTacToe Android apk. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/TicTacToe%20Android%20apk",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-todoapp-js",
    "title": "ToDoApp JS",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «ToDoApp JS» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/ToDoApp_JS. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/ToDoApp_JS",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-train-reservation",
    "title": "Train Reservation",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Train Reservation» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Train Reservation. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Train%20Reservation",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-train-ticket-reservation-system-master",
    "title": "Train Ticket Reservation System master",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Train Ticket Reservation System master» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Train-Ticket-Reservation-System-master. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Train-Ticket-Reservation-System-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-tribonacci-series",
    "title": "Tribonacci series",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Tribonacci series» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Tribonacci series. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Tribonacci%20series",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-utilities",
    "title": "Utilities",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Utilities» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Utilities. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Utilities",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-vehicle-management-system",
    "title": "Vehicle Management System",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Vehicle Management System» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Vehicle Management System. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Vehicle%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-velocity-calculator",
    "title": "velocity calculator",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «velocity calculator» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/velocity-calculator. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/velocity-calculator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-wack-a-mole-game",
    "title": "Wack a mole game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Wack a mole game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Wack-a-mole-game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Wack-a-mole-game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-water-gun-game",
    "title": "water gun game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «water gun game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/water_gun_game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/water_gun_game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-weatherapp-android-master",
    "title": "WeatherApp Android master",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «WeatherApp Android master» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/WeatherApp-Android-master. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/WeatherApp-Android-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-web-browser",
    "title": "Web Browser",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Web Browser» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Web Browser. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Web%20Browser",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-websiteping",
    "title": "Websiteping",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Websiteping» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Websiteping. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Websiteping",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-women-safety-app-master",
    "title": "Women Safety App master",
    "category": "fullstack",
    "categoryLabel": "Aplicación",
    "summary": "Proyecto «Women Safety App master» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Women-Safety-App-master. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Women-Safety-App-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-word-guess-game",
    "title": "Word Guess Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Word Guess Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Word Guess Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Word%20Guess%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-word-riddle-game",
    "title": "Word Riddle Game",
    "category": "fullstack",
    "categoryLabel": "Juego o simulador",
    "summary": "Proyecto «Word Riddle Game» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Word Riddle Game. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Word%20Riddle%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-youtube-playlist-length-cal",
    "title": "youtube playlist length cal",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «youtube playlist length cal» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/youtube-playlist-length-cal. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/youtube-playlist-length-cal",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  },
  {
    "slug": "repo-zeros-and-one-s-pattern",
    "title": "Zeros and One's Pattern",
    "category": "desktop",
    "categoryLabel": "Aplicación / proyecto académico",
    "summary": "Proyecto «Zeros and One's Pattern» conservado en el repositorio general. Abre su carpeta para consultar el código fuente, los recursos y las instrucciones disponibles.",
    "description": "Entrada del catálogo completo de Projects/Zeros and One's Pattern. Esta ficha enlaza al directorio original para conservar acceso al proyecto, sin atribuirle funciones o tecnologías que no se hayan verificado.",
    "stack": [
      "Ver README del proyecto"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Zeros%20and%20One's%20Pattern",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Acceso directo a la carpeta original del proyecto.",
      "Consulta el README y los archivos de configuración para conocer requisitos y tecnologías.",
      "El contenido original se conserva sin modificaciones."
    ],
    "classification": "Catálogo completo del repositorio"
  }
];
