# Employer & Worker Registration System

A Java desktop application built with Swing and PostgreSQL for managing employers, workers, jobs, work groups, work records, prices, invoices, and payments. The application uses a DAO layer, entity builders, and in-memory caches to support its CRUD screens.

## Technology stack

| Component | Version / detail |
| --- | --- |
| Language | Java 17 |
| UI | Java Swing |
| Database | PostgreSQL |
| JDBC driver | PostgreSQL JDBC 42.5.1 |
| Build | Maven |
| Main entry point | com.cbozan.main.Main |

## Requirements

- JDK 17
- Maven 3.8+
- PostgreSQL server
- A database matching the existing application schema
- Database account with only the permissions required by the application

## Database configuration

The old source contained a hard-coded PostgreSQL username and password. These values have been removed. Configure the connection with environment variables:

| Variable | Purpose |
| --- | --- |
| EMPLOYER_DB_URL | JDBC URL (defaults to jdbc:postgresql://localhost:5432/Hesap-eProject) |
| EMPLOYER_DB_USER | PostgreSQL username |
| EMPLOYER_DB_PASSWORD | PostgreSQL password |

PowerShell example:

    $env:EMPLOYER_DB_URL = "jdbc:postgresql://localhost:5432/Hesap-eProject"
    $env:EMPLOYER_DB_USER = "your_local_user"
    $env:EMPLOYER_DB_PASSWORD = "your_local_password"

Linux/macOS example:

    export EMPLOYER_DB_URL="jdbc:postgresql://localhost:5432/Hesap-eProject"
    export EMPLOYER_DB_USER="your_local_user"
    export EMPLOYER_DB_PASSWORD="your_local_password"

The same values can be supplied as JVM system properties using employer.db.url, employer.db.user, and employer.db.password.

**The repository does not contain the PostgreSQL schema or seed data.** You must restore/provision the database expected by the original application before running it. Do not assume that an empty database is sufficient.

## Build

From this directory:

    mvn clean package

Run the application with the PostgreSQL JDBC dependency on the classpath, or import the project into an IDE as a Maven project:

    mvn dependency:build-classpath -Dmdep.outputFile=target/classpath.txt

The main class is:

    com.cbozan.main.Main

The GitHub Actions workflow compiles the project with Java 17. It does not connect to a live PostgreSQL database or validate the missing schema.

## Security and reliability improvements in this revision

- Removed hard-coded database credentials from DB.java.
- Added environment-variable and JVM-property based database configuration.
- Added a clear, non-secret connection error message when credentials or PostgreSQL are unavailable.
- Replaced the login query's string concatenation with a PreparedStatement.
- Closed the login ResultSet and PreparedStatement with try-with-resources.
- Added basic empty username/password validation.
- Cleared the password input field and the temporary character array after each login attempt.
- Removed an absolute Windows path to a local PostgreSQL JAR from the Eclipse classpath.
- Added a Maven build descriptor with the PostgreSQL JDBC dependency.

## Known limitations requiring further work

- The original auth query compares the stored pass column directly with the submitted password. The schema and registration flow are not included, so password hashing cannot safely be introduced without a coordinated database migration. Do not use this legacy authentication design for production accounts.
- The application uses one shared JDBC connection and several DAO methods do not close statements/result sets. Replace this with a connection pool or connection-per-operation design and migrate every DAO to try-with-resources.
- Several DAO methods construct SQL with concatenated identifiers or values. Audit and parameterize all user-controlled query inputs.
- Some CRUD methods fetch the last inserted row with ORDER BY id DESC instead of using generated keys; concurrent writes can associate the wrong entity with the cache.
- The database schema and test fixtures must be added before end-to-end tests can run.
- The Swing UI should display actionable connection errors rather than relying on modal dialogs or console output.

## Author

Joseff Antonio Laverde Avendaño
