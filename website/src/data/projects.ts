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
    "summary": "A web application for lossless text compression and decompression using the Huffman coding algorithm.",
    "description": "The project documents a split architecture with a Next.js frontend and a FastAPI backend. It includes compression and decompression, a custom binary format, Huffman tree visualization, and compression metrics.",
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
      "Frontend and backend are separated through a REST API.",
      "Text compression and decompression using Huffman coding.",
      "Visualization of the Huffman tree, character frequencies, and codes.",
      "Documented metrics include compression ratio, entropy, and average code length."
    ],
    "classification": "Personal / Academic Project"
  },
  {
    "slug": "banking-portal-api",
    "title": "Banking Portal API",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "A Java backend project with security, persistence, validation, and caching components.",
    "description": "A Spring Boot application whose Maven configuration declares Java 17 and Spring Web, Spring Security, Spring Data JPA, validation, mail, and cache modules. The configuration also declares MySQL and Redis connectors, alongside Docker resources.",
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
      "Backend built on Spring Boot 3.3.1.",
      "Persistence through Spring Data JPA and the MySQL connector.",
      "Security, validation, and OpenAPI documentation dependencies.",
      "Cache and Redis dependencies, with Docker resources included."
    ],
    "classification": "Personal / Academic Project"
  },
  {
    "slug": "inventory-management-system",
    "title": "Inventory Management System",
    "category": "desktop",
    "categoryLabel": "Desktop Application",
    "summary": "A Java inventory and billing application with a desktop interface and SQL resources.",
    "description": "A Maven project with JavaFX components, entities related to products, customers, and invoices, interface controllers, and SQL resources.",
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
      "Desktop interface built with JavaFX components.",
      "Documented entities for products, customers, and invoicing.",
      "Dependency management through Maven.",
      "SQL resources and test dependencies declared in the project configuration."
    ],
    "classification": "Personal / Academic Project"
  },
  {
    "slug": "gericare",
    "title": "GERICARE — Geriatric Care Management",
    "category": "fullstack",
    "categoryLabel": "HealthTech",
    "summary": "A mobile-first platform focused on geriatric clinical and operational workflows.",
    "description": "A HealthTech platform described as a SaaS solution for geriatric clinical and operational management, including an electronic clinical record (kardex), Comprehensive Geriatric Assessment (CGA), and a multi-tenant architecture. Its code was not found as a standalone directory under Projects/ in this repository, so the repository link opens a GitHub profile search for GERICARE.",
    "stack": [
      "Next.js 16",
      "TypeScript",
      "Supabase",
      "PostgreSQL",
      "Tailwind CSS",
      "HL7 FHIR R4"
    ],
    "repository": "https://github.com/Pudin0120?tab=repositories&q=GERICARE",
    "repositoryLabel": "Search GERICARE repositories",
    "highlights": [
      "Clinical and operational workflows for geriatric care.",
      "Electronic clinical record (kardex) and Comprehensive Geriatric Assessment.",
      "Multi-tenant architecture and data-access policies described for the project.",
      "No standalone GERICARE directory was found under Projects/ in this repository."
    ],
    "classification": "HealthTech / Featured Project"
  },
  {
    "slug": "repo-2048",
    "title": "2048",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"2048\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/2048. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/2048",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-add-your-code-hs",
    "title": "Add Your Code Hs",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Add Your Code Hs\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Add Your Code Hs. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Add%20Your%20Code%20Hs",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-admission-counselling-system",
    "title": "Admission counselling system",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Admission counselling system\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Admission-counselling-system. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Admission-counselling-system",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-ai-riddle-game",
    "title": "AI Riddle Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"AI Riddle Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/AI Riddle Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/AI%20Riddle%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-algorithms",
    "title": "Algorithms",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Algorithms\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Algorithms. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Algorithms",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-app",
    "title": "app",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"app\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/app. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/app",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-ascii-art",
    "title": "Ascii art",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Ascii art\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Ascii_art. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Ascii_art",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-atm",
    "title": "ATM",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"ATM\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/ATM. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/ATM",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-atm-interface",
    "title": "ATM interface",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"ATM interface\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/ATM interface. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/ATM%20interface",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-attendance",
    "title": "Attendance",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Attendance\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Attendance. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Attendance",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-back-end-chat-api",
    "title": "back end chat API",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "\"back end chat API\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/back-end--chat-api. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/back-end--chat-api",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-banking-application",
    "title": "banking application",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"banking application\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/banking application. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/banking%20application",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-bankingportal-api-main",
    "title": "BankingPortal API main",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "\"BankingPortal API main\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/BankingPortal-API-main. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/BankingPortal-API-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-basic-bank-system",
    "title": "Basic Bank System",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Basic Bank System\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Basic_Bank_System. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Basic_Bank_System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-billing-system",
    "title": "Billing system",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Billing system\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Billing-system. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Billing-system",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-binarydecimalconverto",
    "title": "BinaryDecimalConverto",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"BinaryDecimalConverto\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/BinaryDecimalConverto. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/BinaryDecimalConverto",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-blogbackend-main",
    "title": "BlogBackend main",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "\"BlogBackend main\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/BlogBackend-main. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/BlogBackend-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-brick-breaker-game",
    "title": "Brick Breaker Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Brick Breaker Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Brick-Breaker-Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Brick-Breaker-Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-budget-tracker-project",
    "title": "Budget Tracker project",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Budget Tracker project\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Budget Tracker project. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Budget%20Tracker%20project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-calculator-using-java",
    "title": "Calculator using Java",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Calculator using Java\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Calculator using Java. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Calculator%20using%20Java",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-calculator-oops",
    "title": "Calculator OOPS",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Calculator OOPS\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Calculator-OOPS. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Calculator-OOPS",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-calculator-project",
    "title": "Calculator project",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Calculator project\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Calculator-project. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Calculator-project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-calorie-calculator",
    "title": "Calorie Calculator",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Calorie Calculator\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Calorie Calculator. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Calorie%20Calculator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-chat-project",
    "title": "Chat Project",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Chat Project\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Chat Project. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Chat%20Project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-chessgame",
    "title": "ChessGame",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"ChessGame\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/ChessGame. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/ChessGame",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-clouddevopsproject-main",
    "title": "CloudDevOpsProject main",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "\"CloudDevOpsProject main\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/CloudDevOpsProject-main. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/CloudDevOpsProject-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-cloudscripts",
    "title": "cloudscripts",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "\"cloudscripts\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/cloudscripts. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/cloudscripts",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-clue-simulator",
    "title": "Clue Simulator",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Clue Simulator\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Clue Simulator. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Clue%20Simulator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-conversion",
    "title": "Conversion",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Conversion\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Conversion. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Conversion",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-convert-jpeg-to-png",
    "title": "Convert JPEG to PNG",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Convert JPEG to PNG\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Convert_JPEG_to_PNG. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Convert_JPEG_to_PNG",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-correct-number-guess-game",
    "title": "Correct Number Guess Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Correct Number Guess Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Correct Number Guess Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Correct%20Number%20Guess%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-countdown-timer-using-python",
    "title": "Countdown Timer using Python",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Countdown Timer using Python\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Countdown Timer using Python. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Countdown%20Timer%20using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-crypto-image-and-text-encryption-decryption",
    "title": "Crypto Image and Text Encryption Decryption",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Crypto Image and Text Encryption Decryption\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Crypto-Image and Text Encryption Decryption. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Crypto-Image%20and%20Text%20Encryption%20Decryption",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-currency-converter",
    "title": "Currency Converter",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Currency Converter\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Currency Converter. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Currency%20Converter",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-currency-converter-using-java",
    "title": "Currency Converter using Java",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Currency Converter using Java\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Currency Converter using Java. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Currency%20Converter%20using%20Java",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-currency-convertor",
    "title": "currency Convertor",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"currency Convertor\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/currency Convertor. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/currency%20Convertor",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-data-visualisation",
    "title": "Data Visualisation",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Data Visualisation\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Data Visualisation. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Data%20Visualisation",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-datastructures",
    "title": "DataStructures",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"DataStructures\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/DataStructures. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/DataStructures",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-department-wise-salary-calculation",
    "title": "Department Wise Salary Calculation",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Department Wise Salary Calculation\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Department-Wise Salary Calculation. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Department-Wise%20Salary%20Calculation",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-diamond-shipping-project",
    "title": "Diamond shipping project",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Diamond shipping project\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Diamond shipping project. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Diamond%20shipping%20project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-dice-simulator",
    "title": "Dice Simulator",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Dice Simulator\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Dice Simulator. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Dice%20Simulator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-digital-clock",
    "title": "Digital Clock",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Digital Clock\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Digital Clock. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Digital%20Clock",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-dino-game-java",
    "title": "Dino Game Java",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Dino Game Java\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Dino_Game_java. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Dino_Game_java",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-dns-record-using-python",
    "title": "DNS Record using Python",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"DNS Record using Python\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/DNS Record using Python. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/DNS%20Record%20using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-dns-record",
    "title": "Dns record",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Dns record\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Dns_record. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Dns_record",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-duplicate-files-remover",
    "title": "Duplicate files remover",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Duplicate files remover\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Duplicate files remover. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Duplicate%20files%20remover",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-e-commerce-project-springboot-master",
    "title": "E commerce project springBoot master",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"E commerce project springBoot master\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/E-commerce-project-springBoot-master. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/E-commerce-project-springBoot-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-e-health-care-management",
    "title": "E Health Care Management",
    "category": "backend",
    "categoryLabel": "Healthcare & Clinical Management",
    "summary": "A healthcare and clinical-management project included in the repository. Review its source folder and README for verified implementation details.",
    "description": "An application related to healthcare information management. The documentation available in the project folder is the reference for confirming its scope, requirements, and setup.",
    "stack": [
      "Java",
      "Healthcare Management",
      "Project Documentation"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/E-Health%20Care%20Management",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Healthcare information-management focus.",
      "Review the project folder for implementation details and setup instructions.",
      "No additional features are claimed beyond the available project documentation."
    ],
    "classification": "Healthcare / Academic Project"
  },
  {
    "slug": "repo-email-generator",
    "title": "Email Generator",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Email Generator\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Email_Generator. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Email_Generator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-employee",
    "title": "Employee",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Employee\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Employee. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Employee",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-employer-worker-registration-system-main",
    "title": "employer worker registration system main",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"employer worker registration system main\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/employer-worker-registration-system-main. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/employer-worker-registration-system-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-encrypt-the-password",
    "title": "Encrypt the Password",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Encrypt the Password\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Encrypt-the-Password. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Encrypt-the-Password",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-eng-dictionary",
    "title": "Eng Dictionary",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Eng Dictionary\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Eng_Dictionary. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Eng_Dictionary",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-exchange-indian-currency",
    "title": "Exchange Indian Currency",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Exchange Indian Currency\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Exchange-Indian-Currency. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Exchange-Indian-Currency",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-face-recognition-using-python",
    "title": "Face Recognition Using Python",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Face Recognition Using Python\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Face Recognition Using Python. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Face%20Recognition%20Using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-fee-management-system",
    "title": "Fee Management System",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Fee Management System\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Fee Management System. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Fee%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-fee-management-system-2",
    "title": "Fee Management System",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Fee Management System\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Fee-Management-System. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Fee-Management-System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-fibonacci",
    "title": "Fibonacci",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Fibonacci\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Fibonacci. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Fibonacci",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-finance",
    "title": "Finance",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Finance\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Finance. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Finance",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-fota-graduation-project-2022-main",
    "title": "FOTA Graduation Project 2022 main",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"FOTA Graduation Project 2022 main\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/FOTA_Graduation-Project-2022-main. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/FOTA_Graduation-Project-2022-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-geocoding-of-a-webpage-using-python",
    "title": "Geocoding of a Webpage using Python",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Geocoding of a Webpage using Python\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Geocoding of a Webpage using Python. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Geocoding%20of%20a%20Webpage%20using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-get-current-time",
    "title": "Get Current Time",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Get Current Time\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Get Current Time. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Get%20Current%20Time",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-graduation-project-master",
    "title": "Graduation Project master",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Graduation Project master\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Graduation-Project-master. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Graduation-Project-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-graduationproject-master",
    "title": "GraduationProject master",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"GraduationProject master\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/GraduationProject-master. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/GraduationProject-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-guess-the-number",
    "title": "Guess the number",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Guess the number\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Guess the number. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Guess%20the%20number",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-guess-the-number-game",
    "title": "Guess The Number Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Guess The Number Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Guess The Number Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Guess%20The%20Number%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-guessthenumbergame",
    "title": "GuessTheNumberGame",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"GuessTheNumberGame\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/GuessTheNumberGame. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/GuessTheNumberGame",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-hospital-management-system",
    "title": "Hospital Management System",
    "category": "backend",
    "categoryLabel": "Healthcare & Clinical Management",
    "summary": "A hospital-management project included in the repository. Review its source folder and README for verified implementation details.",
    "description": "An application related to hospital information and management workflows. The documentation available in the project folder is the reference for confirming its scope, requirements, and setup.",
    "stack": [
      "Java",
      "Hospital Management",
      "Project Documentation"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Hospital%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Hospital information-management focus.",
      "Review the project folder for implementation details and setup instructions.",
      "No additional features are claimed beyond the available project documentation."
    ],
    "classification": "Healthcare / Academic Project"
  },
  {
    "slug": "repo-image-gallery",
    "title": "Image Gallery",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Image Gallery\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Image Gallery. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Image%20Gallery",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-img",
    "title": "img",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"img\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/img. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/img",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-internet-slang-s-dictionary",
    "title": "Internet Slang's Dictionary",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Internet Slang's Dictionary\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Internet Slang's Dictionary. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Internet%20Slang's%20Dictionary",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-inventory-management-system-main",
    "title": "inventory management system main",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"inventory management system main\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/inventory-management-system-main. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/inventory-management-system-main",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-java-server-client-networking-same-device",
    "title": "Java SERVER CLIENT NETWORKING(SAME DEVICE)",
    "category": "backend",
    "categoryLabel": "Backend",
    "summary": "\"Java SERVER CLIENT NETWORKING(SAME DEVICE)\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/JAVA SERVER CLIENT NETWORKING(SAME DEVICE). This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/JAVA%20SERVER%20CLIENT%20NETWORKING(SAME%20DEVICE)",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-javacodes",
    "title": "JavaCodes",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"JavaCodes\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/JavaCodes. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/JavaCodes",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-javagame",
    "title": "javagame",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"javagame\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/javagame. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/javagame",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-languagetranslator-using-python",
    "title": "LanguageTranslator Using Python",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"LanguageTranslator Using Python\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/LanguageTranslator-Using-Python. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/LanguageTranslator-Using-Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-leetcode",
    "title": "Leetcode",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Leetcode\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Leetcode. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Leetcode",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-library-management",
    "title": "Library Management",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Library Management\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Library Management. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Library%20Management",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-libraryapp",
    "title": "LibraryApp",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"LibraryApp\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/LibraryApp. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/LibraryApp",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-librarymangement",
    "title": "LibraryMangement",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"LibraryMangement\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/LibraryMangement. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/LibraryMangement",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-listscanner",
    "title": "ListScanner",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"ListScanner\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/ListScanner. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/ListScanner",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-lost-and-found-application",
    "title": "Lost and found application",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Lost and found application\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Lost and found application. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Lost%20and%20found%20application",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-lucas-numbers",
    "title": "Lucas Numbers",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Lucas Numbers\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Lucas Numbers. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Lucas%20Numbers",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-maildemo",
    "title": "maildemo",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"maildemo\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/maildemo. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/maildemo",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-marvel-avengers-game",
    "title": "Marvel Avengers Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Marvel Avengers Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Marvel Avengers Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Marvel%20Avengers%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-math",
    "title": "Math",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Math\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Math. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Math",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-medical-store-shop-system-database-jar-files",
    "title": "Medical Store Shop System + Database + Jar Files",
    "category": "backend",
    "categoryLabel": "Healthcare & Clinical Management",
    "summary": "A medical-store management project with a database and packaged application files, included in the repository.",
    "description": "A project related to medical-store operations. Its folder name indicates that database resources and JAR files are included; review the source folder for verified implementation details and setup instructions.",
    "stack": [
      "Java",
      "Database",
      "JAR Files",
      "Project Documentation"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Medical%20Store%20Shop%20System%20%2B%20Database%20%2B%20Jar%20Files",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Medical-store management focus.",
      "The folder name indicates database resources and JAR files.",
      "Review the project folder for implementation details and setup instructions."
    ],
    "classification": "Healthcare / Academic Project"
  },
  {
    "slug": "repo-meditation-app",
    "title": "meditation app",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"meditation app\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/meditation-app. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/meditation-app",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-meme-generator",
    "title": "MEME GENERATOR",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"MEME GENERATOR\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/MEME GENERATOR. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/MEME%20GENERATOR",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-metal",
    "title": "Metal",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Metal\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Metal. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Metal",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-mims-master",
    "title": "MIMS master",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"MIMS master\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/MIMS-master. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/MIMS-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-minesweeper-using-python",
    "title": "MineSweeper Using Python",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"MineSweeper Using Python\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/MineSweeper Using Python. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/MineSweeper%20Using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-movie-ticket-booking-system",
    "title": "Movie Ticket Booking System",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Movie Ticket Booking System\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Movie Ticket Booking System. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Movie%20Ticket%20Booking%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-nbproject",
    "title": "nbproject",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"nbproject\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/nbproject. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/nbproject",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-online-book-store",
    "title": "Online Book Store",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Online Book Store\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Online Book Store. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Online%20Book%20Store",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-online-event-management-system",
    "title": "Online Event Management System",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Online Event Management System\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Online Event Management System. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Online%20Event%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-online-exam",
    "title": "online exam",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"online exam\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/online exam. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/online%20exam",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-online-voting-system",
    "title": "Online Voting System",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Online Voting System\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Online Voting System. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Online%20Voting%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-onlinebookstore-master",
    "title": "onlinebookstore master",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"onlinebookstore master\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/onlinebookstore-master. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/onlinebookstore-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-orderbook",
    "title": "OrderBook",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"OrderBook\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/OrderBook. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/OrderBook",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-otp-generator",
    "title": "OTP generator",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"OTP generator\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/OTP generator. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/OTP%20generator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-otp-generator-2",
    "title": "OTP generator",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"OTP generator\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/OTP-generator. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/OTP-generator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-password-generator",
    "title": "Password Generator",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Password Generator\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Password_Generator. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Password_Generator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-patience-game",
    "title": "Patience game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Patience game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Patience_game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Patience_game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-patterns",
    "title": "Patterns",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Patterns\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Patterns. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Patterns",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-petshop",
    "title": "petshop",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"petshop\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/petshop. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/petshop",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-pirate-adventure-game",
    "title": "Pirate Adventure Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Pirate Adventure Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Pirate_Adventure_Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Pirate_Adventure_Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-pong-game",
    "title": "Pong Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Pong Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Pong Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Pong%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-puzzle-game",
    "title": "Puzzle Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Puzzle Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Puzzle Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Puzzle%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-quiz-management-system",
    "title": "Quiz Management System",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Quiz Management System\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Quiz Management System. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Quiz%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-quiz-project",
    "title": "Quiz project",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Quiz project\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Quiz project. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Quiz%20project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-quizup",
    "title": "QuizUp",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"QuizUp\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/QuizUp. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/QuizUp",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-quotes",
    "title": "Quotes",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Quotes\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Quotes. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Quotes",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-randompasswordgenerator",
    "title": "RandomPasswordGenerator",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"RandomPasswordGenerator\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/RandomPasswordGenerator. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/RandomPasswordGenerator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-restaurant-management-system",
    "title": "Restaurant management system",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Restaurant management system\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Restaurant-management-system. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Restaurant-management-system",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-resume-builder",
    "title": "Resume Builder",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Resume Builder\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Resume Builder. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Resume%20Builder",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-resume-builder-java",
    "title": "resume builder Java",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"resume builder Java\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/resume-builder-java. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/resume-builder-java",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-riddle-game",
    "title": "Riddle Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Riddle Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Riddle Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Riddle%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-riddlequestgame",
    "title": "RiddleQuestGame",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"RiddleQuestGame\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/RiddleQuestGame. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/RiddleQuestGame",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-scientific-calculator",
    "title": "Scientific Calculator",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Scientific Calculator\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Scientific Calculator. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Scientific%20Calculator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-screenshot-using-python",
    "title": "Screenshot using Python",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Screenshot using Python\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Screenshot using Python. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Screenshot%20using%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-search",
    "title": "Search",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Search\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Search. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Search",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-shop-management-system",
    "title": "Shop Management System",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Shop Management System\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Shop Management System. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Shop%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-simple-adventure-game",
    "title": "Simple Adventure Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Simple Adventure Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Simple Adventure Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Simple%20Adventure%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-simple-plagiarism-checker-project",
    "title": "Simple Plagiarism Checker Project",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Simple Plagiarism Checker Project\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Simple-Plagiarism-Checker-Project. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Simple-Plagiarism-Checker-Project",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-snake-game",
    "title": "Snake game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Snake game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Snake game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Snake%20game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-software-piracy-control",
    "title": "Software Piracy Control",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Software Piracy Control\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Software Piracy Control. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Software%20Piracy%20Control",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-sorting",
    "title": "Sorting",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Sorting\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Sorting. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Sorting",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-src",
    "title": "src",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"src\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/src. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/src",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-stock-algorithm-js-sandbox",
    "title": "stock algorithm js sandbox",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"stock algorithm js sandbox\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/stock-algorithm-js-sandbox. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/stock-algorithm-js-sandbox",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-student-management-system",
    "title": "Student Management System",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Student Management System\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Student Management System. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Student%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-svg-file-generator",
    "title": "Svg File Generator",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Svg File Generator\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Svg File Generator. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Svg%20File%20Generator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-task-list",
    "title": "Task list",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Task list\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Task list. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Task%20list",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-task-tracker",
    "title": "Task Tracker",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Task Tracker\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Task_Tracker. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Task_Tracker",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-task-1-online-reservation-system",
    "title": "TASK 1 (Online Reservation System)",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"TASK 1 (Online Reservation System)\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/TASK-1 (Online Reservation System). This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/TASK-1%20(Online%20Reservation%20System)",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-temperature-converter",
    "title": "Temperature Converter",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Temperature Converter\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Temperature Converter. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Temperature%20Converter",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-temperatureconverter",
    "title": "TemperatureConverter",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"TemperatureConverter\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/TemperatureConverter. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/TemperatureConverter",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-the-metro-app",
    "title": "the metro app",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"the metro app\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/the_metro_app. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/the_metro_app",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-tic-tac-toe-python",
    "title": "Tic Tac Toe Python",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Tic Tac Toe Python\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Tic Tac Toe Python. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Tic%20Tac%20Toe%20Python",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-tic-tac-toe-game",
    "title": "Tic  Tac  Toe Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Tic  Tac  Toe Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Tic- Tac- Toe Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Tic-%20Tac-%20Toe%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-tic-tac-toe",
    "title": "Tic Tac Toe",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Tic Tac Toe\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Tic-Tac-Toe. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Tic-Tac-Toe",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-tictactoe",
    "title": "TicTacToe",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"TicTacToe\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/TicTacToe. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/TicTacToe",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-tictactoe-android-apk",
    "title": "TicTacToe Android apk",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"TicTacToe Android apk\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/TicTacToe Android apk. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/TicTacToe%20Android%20apk",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-todoapp-js",
    "title": "ToDoApp JS",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"ToDoApp JS\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/ToDoApp_JS. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/ToDoApp_JS",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-train-reservation",
    "title": "Train Reservation",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Train Reservation\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Train Reservation. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Train%20Reservation",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-train-ticket-reservation-system-master",
    "title": "Train Ticket Reservation System master",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Train Ticket Reservation System master\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Train-Ticket-Reservation-System-master. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Train-Ticket-Reservation-System-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-tribonacci-series",
    "title": "Tribonacci series",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Tribonacci series\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Tribonacci series. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Tribonacci%20series",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-utilities",
    "title": "Utilities",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Utilities\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Utilities. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Utilities",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-vehicle-management-system",
    "title": "Vehicle Management System",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Vehicle Management System\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Vehicle Management System. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Vehicle%20Management%20System",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-velocity-calculator",
    "title": "velocity calculator",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"velocity calculator\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/velocity-calculator. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/velocity-calculator",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-wack-a-mole-game",
    "title": "Wack a mole game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Wack a mole game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Wack-a-mole-game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Wack-a-mole-game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-water-gun-game",
    "title": "water gun game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"water gun game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/water_gun_game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/water_gun_game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-weatherapp-android-master",
    "title": "WeatherApp Android master",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"WeatherApp Android master\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/WeatherApp-Android-master. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/WeatherApp-Android-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-web-browser",
    "title": "Web Browser",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Web Browser\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Web Browser. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Web%20Browser",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-websiteping",
    "title": "Websiteping",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Websiteping\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Websiteping. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Websiteping",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-women-safety-app-master",
    "title": "Women Safety App master",
    "category": "fullstack",
    "categoryLabel": "Application",
    "summary": "\"Women Safety App master\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Women-Safety-App-master. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Women-Safety-App-master",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-word-guess-game",
    "title": "Word Guess Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Word Guess Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Word Guess Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Word%20Guess%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-word-riddle-game",
    "title": "Word Riddle Game",
    "category": "fullstack",
    "categoryLabel": "Game / Simulator",
    "summary": "\"Word Riddle Game\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Word Riddle Game. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Word%20Riddle%20Game",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-youtube-playlist-length-cal",
    "title": "youtube playlist length cal",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"youtube playlist length cal\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/youtube-playlist-length-cal. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/youtube-playlist-length-cal",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  },
  {
    "slug": "repo-zeros-and-one-s-pattern",
    "title": "Zeros and One's Pattern",
    "category": "desktop",
    "categoryLabel": "Academic Application",
    "summary": "\"Zeros and One's Pattern\" is part of the project archive. Open its original folder to review the source code, assets, and available instructions.",
    "description": "Archive entry for Projects/Zeros and One's Pattern. This page links to the original project directory so the source remains accessible. Specific features and technologies are not inferred when they have not been verified.",
    "stack": [
      "See project README"
    ],
    "repository": "https://github.com/Pudin0120/Portafolio/tree/main/Projects/Zeros%20and%20One's%20Pattern",
    "repositoryLabel": "Carpeta original en GitHub",
    "highlights": [
      "Direct access to the original project folder.",
      "Review the README and configuration files for verified requirements and technologies.",
      "The original source files are preserved without modification."
    ],
    "classification": "Complete Repository Catalog"
  }
];
