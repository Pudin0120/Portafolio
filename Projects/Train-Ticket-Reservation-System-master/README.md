# Train Ticket Reservation System

A Java Servlet/JSP reservation application for customer registration, train search, availability/fare enquiry, ticket booking, booking history, profile management, and administrator train management.

## Technology stack found in the repository

| Technology | Version / configuration |
| --- | --- |
| Java | 8 source/target |
| Servlet API | 3.1.0 |
| Packaging | Maven WAR |
| Application server | Servlet 3.1-compatible container (for example, Tomcat 8.5) |
| Database | Oracle Database |
| JDBC driver | Oracle JDBC; the driver JAR must be provided separately |
| Build tools | Maven Wrapper |

The POM also declares PostgreSQL and MySQL drivers, but the checked-in application.properties selects Oracle. The Oracle JDBC driver is not declared in the POM because it is distributed separately; supply a compatible ojdbc JAR on the runtime/build classpath.

## Prerequisites

- JDK 8 or newer
- Oracle Database with a local schema/user
- A compatible Oracle JDBC driver
- Maven Wrapper (included)
- A Servlet 3.1-compatible web container

## 1. Create the Oracle schema

Follow [Dummy-Database.md](Dummy-Database.md) using a local Oracle development database. The script now requests limited schema-creation privileges rather than granting DBA to the application user.

Use a strong local schema password and do not paste it into a committed file. The SQL script creates customer/admin tables and sample trains; it does not seed shared demo accounts or passwords.

The application stores PBKDF2 password hashes. The PWORD columns must be VARCHAR2(255) to hold the encoded salted hashes; the setup script applies that size.

## 2. Configure database environment variables

The tracked src/application.properties file contains only the driver and local JDBC URL. Supply credentials through environment variables:

| Variable | Purpose |
| --- | --- |
| DB_DRIVER | Oracle JDBC driver class |
| DB_URL | Oracle JDBC URL |
| DB_USERNAME | Local schema username |
| DB_PASSWORD | Local schema password |

PowerShell example:

    $env:DB_DRIVER = 'oracle.jdbc.OracleDriver'
    $env:DB_URL = 'jdbc:oracle:thin:@localhost:1521/orcl'
    $env:DB_USERNAME = 'RESERVATION'
    $env:DB_PASSWORD = 'your-local-schema-password'

Linux/macOS example:

    export DB_DRIVER='oracle.jdbc.OracleDriver'
    export DB_URL='jdbc:oracle:thin:@localhost:1521/orcl'
    export DB_USERNAME='RESERVATION'
    export DB_PASSWORD='your-local-schema-password'

DBUtil no longer prints the JDBC URL, username, or password to standard output.

## 3. Build the WAR

From this directory:

    ./mvnw clean package

On Windows, use mvnw.cmd. Deploy the generated TrainBook.war from target/ to the configured servlet container.

Because the Oracle driver is not included in this repository's Maven dependencies, make sure it is available to the application server or deployment package before starting the application.

## 4. Create an administrator account

1. Register a customer through the application.
2. The application stores a salted PBKDF2-HMAC-SHA-256 password hash.
3. To grant that account administrator access in a local database, copy its already-hashed password and profile row into ADMIN:

    INSERT INTO ADMIN (MAILID, PWORD, FNAME, LNAME, ADDR, PHNO)
    SELECT MAILID, PWORD, FNAME, LNAME, ADDR, PHNO
    FROM CUSTOMER
    WHERE MAILID = 'your-admin-email@example.com';

Do not reuse a public demo password or grant DBA to the application schema.

## Security improvements included in this review

- Database credentials now come from DB_* environment variables.
- JDBC connection information is no longer printed to logs.
- New customer passwords are stored using PBKDF2-HMAC-SHA-256 with a unique random salt.
- Existing plaintext passwords are upgraded to PBKDF2 on successful login.
- Password changes verify the old password and persist a newly hashed password.
- Registration uses executeUpdate for INSERT statements rather than executeQuery.
- Database password columns were widened to hold encoded hashes.
- The demo SQL no longer creates public admin/customer accounts or grants DBA to the schema user.

## Remaining work before production use

- DBUtil still holds one static JDBC connection. Replace it with a connection pool or per-operation connections and close each connection reliably.
- Replace the servlet-context user object and custom cookie-only login checks with session-scoped authentication and secure HttpOnly/SameSite cookies.
- Add CSRF protection to state-changing forms, output encoding for dynamic HTML, request validation, and rate limiting.
- Review every servlet's authorization checks, especially administrative and booking operations.
- Add transaction boundaries for seat reservation and payment operations to prevent overselling.
- Add tests for login, registration, password migration, booking concurrency, and administrator access.
- Provide a reproducible Oracle JDBC dependency/bootstrap procedure for the selected Oracle version.

## Verification status

The repository changes in this review have not been compiled against Oracle or tested in a servlet container. Verify the Maven WAR build and run the security/database flows against a disposable local schema before relying on them.
