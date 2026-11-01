# JtSpringProject — E-commerce Web Application

A Spring Boot and JSP web application for a small e-commerce workflow. The source includes product/category persistence, customer accounts, user and admin routes, shopping-cart models, Spring Security, and Hibernate-based database access.

## Technology stack

| Technology | Version / detail |
| --- | --- |
| Java | 11 |
| Spring Boot | 2.6.4 |
| Spring Security | Spring Boot-managed version |
| Persistence | Hibernate / JPA |
| Database | MySQL Connector/J 8.0.33 |
| Views | JSP, JSTL, embedded Tomcat Jasper |
| Build | Maven Wrapper |

The versions are read from pom.xml. Spring Boot 2.6.4 is an older release line; this project should be treated as a learning/maintenance codebase until its framework and dependency versions are upgraded and reviewed.

## Prerequisites

- JDK 11
- MySQL 8.x
- Maven Wrapper (included)

## 1. Configure the database

The basedata.sql script creates the ecommjava database, category and customer tables, and sample product data. It no longer inserts public demo accounts with weak plaintext passwords.

Import the script:

    mysql -u root -p < basedata.sql

For better local security, create a dedicated MySQL user restricted to the ecommjava database rather than running the application as root.

## 2. Configure environment variables

The application reads database settings from environment variables:

| Variable | Purpose |
| --- | --- |
| DB_DRIVER | JDBC driver class |
| DB_URL | JDBC URL |
| DB_USERNAME | Dedicated database user |
| DB_PASSWORD | Database password |
| HIBERNATE_DDL_AUTO | Schema mode; use validate for a controlled deployment |
| HIBERNATE_SHOW_SQL | Enable SQL logging only in local development |
| SERVER_PORT | HTTP port (default 8080) |

Linux/macOS example:

    export DB_URL='jdbc:mysql://localhost:3306/ecommjava'
    export DB_USERNAME='ecommerce_app'
    export DB_PASSWORD='your-local-password'

PowerShell example:

    $env:DB_URL = 'jdbc:mysql://localhost:3306/ecommjava'
    $env:DB_USERNAME = 'ecommerce_app'
    $env:DB_PASSWORD = 'your-local-password'

Do not commit real credentials or place them in screenshots or issue comments.

## 3. Build and run

From this directory:

    ./mvnw clean package
    ./mvnw spring-boot:run

On Windows, use mvnw.cmd instead of ./mvnw. The application is configured for port 8080 by default.

## Authentication notes

- New users are stored with BCrypt-encoded passwords through userService.
- The service also upgrades legacy plain-text passwords to BCrypt when an account is loaded for authentication.
- The SQL setup no longer creates predictable admin/customer demo accounts.
- Register a user through the application, then grant administrator access only to an intentionally selected account in your local database by setting its role to ROLE_ADMIN.
- Review account recovery, input validation, rate limiting, and authorization rules before using real customer accounts.

## Main source areas

- configuration — Spring Security and password encoder configuration.
- controller — customer and admin web routes.
- dao — Hibernate-based database access.
- models — product, category, cart, and user entities.
- services — business operations for users, products, and carts.
- views — JSP templates under the configured /views/ prefix.

## Known limitations and next improvements

- The current project uses the older Spring Boot 2.6.4 generation and javax-era dependencies. Plan an incremental upgrade rather than changing the framework version without integration testing.
- Review Hibernate schema auto-update behavior; use explicit migrations and HIBERNATE_DDL_AUTO=validate for controlled environments.
- Replace the direct DriverManagerDataSource with a managed connection pool before production use.
- Review logout behavior and convert state-changing logout requests to POST forms where the UI permits.
- Add tests for registration, password migration, cart ownership, administrator authorization, and product stock consistency.
- Validate product price/quantity rules and enforce transactional stock updates during checkout.

## Verification

This repository review updated configuration hygiene and the database seed script. The Maven build and application runtime have not been executed as part of this change.
