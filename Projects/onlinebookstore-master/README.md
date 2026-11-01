# Online Bookstore

A Java 8 / Servlet 3.1 web application for browsing and managing a book catalogue, customer accounts, seller accounts, shopping carts, and checkout/order workflows. The project is packaged as a WAR and uses MySQL JDBC for persistence.

## Technology stack

| Component | Version / detail |
| --- | --- |
| Java | 8 (Maven compiler source/target) |
| Packaging | Maven WAR |
| Servlet API | 3.1.0 |
| Database | MySQL 8 / Connector-J 8.0.28 |
| Web runtime | webapp-runner 8.0.30.2 (Tomcat-based) |
| Frontend | HTML, CSS, JSP/Servlet responses, static web assets |

The POM also declares PostgreSQL JDBC 42.3.7, but the supplied MySQL setup script and application configuration use MySQL.

## Main features visible in the source

- Book catalogue lookup and display.
- Customer and seller account registration/login.
- Book management operations for seller workflows.
- Cart contents stored in the HTTP session.
- Checkout and order/payment demonstration screens.
- SQL scripts for creating the book and user tables and loading sample books.

The current payment flow is a demonstration workflow; no verified payment-gateway integration is configured.

## Prerequisites

- JDK 8
- Maven 3.6 or newer
- MySQL 8.x
- A dedicated local database account with access limited to the onlinebookstore schema

## 1. Create the database

Use the Dummy_Database.md file as the MySQL setup guide. It creates the onlinebookstore database, books and users tables, and sample book rows. Public demo accounts with predictable passwords have been removed.

Create a dedicated database account and grant it only the privileges needed by the application. Do not run the application as MySQL root.

Note: setup/CreateDatastore.sql contains PostgreSQL-specific syntax (\\c) and should not be executed as a MySQL script. The documented MySQL schema is in Dummy_Database.md.

## 2. Configure the database connection

The tracked src/main/resources/application.properties contains no database username or password. Provide these environment variables:

| Variable | Purpose |
| --- | --- |
| DB_DRIVER | JDBC driver class (defaults to com.mysql.cj.jdbc.Driver) |
| DB_URL | Full JDBC URL |
| DB_USERNAME | Dedicated database username |
| DB_PASSWORD | Database password |

Linux/macOS example:

    export DB_URL='jdbc:mysql://localhost:3306/onlinebookstore?useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC'
    export DB_USERNAME='bookstore_app'
    export DB_PASSWORD='your-local-password'

PowerShell example:

    $env:DB_URL = 'jdbc:mysql://localhost:3306/onlinebookstore?useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC'
    $env:DB_USERNAME = 'bookstore_app'
    $env:DB_PASSWORD = 'your-local-password'

Never commit local credentials, environment files, database dumps containing real user information, or production secrets.

## 3. Build the WAR

From this directory:

    mvn clean package

The main artifact is target/onlinebookstore.war. The Maven dependency plugin also downloads the configured webapp-runner JAR under target/dependency/.

For a local standalone run, after packaging:

    java -jar target/dependency/webapp-runner.jar target/onlinebookstore.war

Open the local address printed by the runner. The exact context path depends on the webapp-runner configuration.

## Account security changes

- New account passwords are stored as salted PBKDF2-HMAC-SHA-256 hashes (120,000 iterations, 256-bit derived key).
- Existing plaintext account values are compared during login and upgraded to PBKDF2 after a successful login when the password is at least 8 characters.
- The login flow rotates the HTTP session after successful customer or seller authentication to reduce session-fixation risk.
- Dynamic account display names are HTML-escaped before inclusion in login responses.
- Book IDs in the cart lookup query are bound as prepared-statement parameters.
- The sample database no longer creates predictable demo accounts.

Short legacy plaintext passwords (under 8 characters) can still authenticate so existing data is not silently locked out, but they are not upgraded automatically. Reset those accounts to a strong password before using them beyond a disposable local environment.

## Important limitations / next improvements

- DBUtil still holds one process-wide JDBC connection. Replace it with a connection pool and obtain/close a connection per service operation before using the app with concurrent users.
- Review all remaining DAO/service methods for try-with-resources; several legacy methods still need consistent statement/result cleanup and structured error handling.
- Audit all pages and servlet responses for output encoding, authorization checks, CSRF protection, and input validation. Escaping login display names does not complete a full XSS audit.
- The cart remains session-backed. Validate product quantities and available stock on the server at checkout.
- Wrap order creation and inventory decrements in a database transaction with row-level stock checks to avoid overselling.
- Replace the demonstration checkout with a properly integrated, provider-hosted payment flow. Do not collect or store raw card numbers in this application.
- Add account recovery, rate limiting, stronger session cookie settings (Secure, HttpOnly, SameSite), and audit logging.
- Review old libraries and the webapp-runner/Tomcat version before public deployment.

## Verification status

The current source changes have not yet been confirmed by a Maven WAR build or an integration test against MySQL. The first validation should be the Java 8 CI build and the password-hashing smoke test.
