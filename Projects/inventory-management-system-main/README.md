# Inventory Management System

A JavaFX desktop application for inventory, customers, purchases, sales, billing, and invoice/report workflows. The source includes JavaFX views and controllers, entity classes, JasperReports templates, a MySQL JDBC configuration, and a SQL database dump.

## Technology stack

| Technology | Version / detail |
| --- | --- |
| Java | 11 (Maven compiler release) |
| JavaFX | 11.0.2 |
| Build | Maven |
| MySQL JDBC driver | 8.0.33 |
| UI libraries | ControlsFX, FormsFX, ValidatorFX, Ikonli, TilesFX |
| Reporting | JasperReports 6.20.5 |
| Tests | JUnit Jupiter 5.7.1 dependencies are declared |

The Maven configuration includes several additional reporting, document, and database libraries. Their versions are managed in pom.xml.

## Prerequisites

- JDK 11
- Maven (or use the Maven Wrapper if one is added)
- MySQL or a compatible MariaDB server
- A database client to load the provided schema

The included SQL dump records MariaDB 10.4.21 as its source server. Validate the schema on your chosen database version before using it with important data.

## 1. Create the database

Create the database and import the SQL dump:

    mysql -u root -p -e "CREATE DATABASE inventory_management_system CHARACTER SET utf8mb4;"
    mysql -u root -p inventory_management_system < database/inventory_management_system.sql

Create a dedicated local database user and grant it access only to this database. Do not use the database root account for the application.

## 2. Configure the connection

The application reads application.properties from the classpath. The tracked file contains only the JDBC driver; connection URL, username, and password must be provided through environment variables:

| Variable | Purpose |
| --- | --- |
| DB_DRIVER | JDBC driver class |
| DB_URL | JDBC connection URL |
| DB_USERNAME | Database user |
| DB_PASSWORD | Database password |

Example for a local MySQL instance:

    DB_URL=jdbc:mysql://127.0.0.1:3306/inventory_management_system
    DB_USERNAME=inventory_user
    DB_PASSWORD=your-local-password

Set these variables in your operating system or IDE run configuration. Do not commit personal credentials.

## 3. Build and run

From this directory:

    mvn clean package
    mvn javafx:run

The configured JavaFX launcher class is com.inventorymanagementsystem.app.Launcher. The Maven Shade configuration also defines an executable JAR artifact; verify the generated artifact name in target/ after packaging.

## Main features visible in the source

- Login screen and dashboard navigation.
- Product inventory listing and item lookup.
- Customer records.
- Purchase and sales records.
- Billing and invoice search/printing.
- Dashboard totals and monthly summaries.
- JasperReports-based customer, sales, purchase, and invoice reports.

## Source layout

- src/main/java/com/inventorymanagementsystem — application and JavaFX controllers.
- src/main/java/com/inventorymanagementsystem/entity — product, customer, invoice, sales, purchase, billing, and user models.
- src/main/java/com/inventorymanagementsystem/config — JDBC connection setup.
- src/main/resources — FXML, CSS, and application configuration.
- database — database schema and example records.

## Known limitations to address before production use

- New passwords should be stored using salted PBKDF2-HMAC-SHA-256 hashes. The login flow now verifies PBKDF2 values and upgrades legacy plaintext values after a successful login when the password is at least eight characters. Short legacy passwords remain verifiable but must be reset before production use.
- Password reset, registration, and account provisioning are still not implemented in the application UI. Create local test accounts only in a disposable database and use the provided PasswordUtil when generating stored hashes.
- The demonstration database previously included the public default login admin/admin; that seed account has been removed. Create any local test account only in a disposable local database.
- The login query now uses try-with-resources and a prepared statement; review database transaction boundaries, resource closing, validation, and error handling in the remaining controllers.
- Keep database access behind a repository/service layer before extending the application.
- Validate monetary calculations and replace floating-point money values with a decimal type before using real financial records.

## Password hashing verification

A dependency-free smoke test verifies PBKDF2 matching, unique salts, wrong-password rejection, legacy-password verification, and tamper detection:

    javac -d target/password-test src/main/java/com/inventorymanagementsystem/security/PasswordUtil.java tools/PasswordUtilSmokeTest.java
    java -cp target/password-test com.inventorymanagementsystem.security.PasswordUtilSmokeTest

## Project attribution

This project is preserved under the original directory name in Joseff Laverde's portfolio repository. Review the included source and license metadata before redistribution.
