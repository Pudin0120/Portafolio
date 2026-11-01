# Banking Portal API

A Spring Boot REST API project for a banking portal. The source tree contains authentication and password-reset controllers, account and transaction services, user/account entities, JWT security, email/OTP support, MySQL persistence, and Redis-backed cache components.

## Technology stack

| Component | Version / dependency |
| --- | --- |
| Java | 17 |
| Spring Boot | 3.3.1 |
| Build | Maven Wrapper |
| Database | MySQL 8.0 |
| Cache | Redis 7 |
| Security | Spring Security, JWT (JJWT 0.11.5), BCrypt |
| API documentation | Springdoc OpenAPI |
| Tests | Spring Boot Test, MockMvc, GreenMail |

The versions above are read from the project POM and Compose configuration. Transitive dependencies are resolved by Maven.

## Prerequisites

- JDK 17
- Docker Engine and Docker Compose
- The Maven Wrapper included in this folder

## 1. Configure local infrastructure

From this project directory, copy the example variables file to the repository root:

    cp docker/.env.example .env

Replace the example passwords with strong, unique local values. The Compose file binds MySQL and Redis to 127.0.0.1 so these development services are not exposed on every network interface.

Start the infrastructure:

    docker compose -f docker/docker-compose.yml up -d

Check service status:

    docker compose -f docker/docker-compose.yml ps

This Compose file starts MySQL and Redis; it does not start the Spring Boot API.

## 2. Configure the API

Copy the sample configuration:

    cp src/main/resources/application.properties.sample src/main/resources/application.properties

Set the required variables in your local environment before starting the API:

- DB_URL
- DB_USERNAME
- DB_PASSWORD
- JWT_SECRET
- MAIL_USERNAME
- MAIL_PASSWORD
- GEO_API_KEY

Optional variables include SERVER_PORT, APP_CORS_ALLOWED_ORIGINS, JWT_EXPIRATION, MAIL_HOST, MAIL_PORT, and GEO_API_URL.

Use a long, randomly generated JWT signing secret. Keep the local application.properties and .env files out of version control. Never reuse the example values as production credentials.

## 3. Build and run

Build the application:

    ./mvnw clean package

Run the packaged application:

    java -jar target/bankingportal-0.0.1-SNAPSHOT.jar

The default API port is 8180. The OpenAPI UI is normally available at:

    http://localhost:8180/swagger-ui/index.html

The actual API endpoints and authorization requirements are defined by the controllers and security configuration.

## 4. Tests

Run the automated test suite:

    ./mvnw test

The test sources use Spring Boot Test and MockMvc. Ensure the test-specific Spring configuration and any required external services are available before interpreting a test failure as an application defect.

## Project structure

- config — CORS, security, cache, Redis, and API documentation configuration.
- controller — HTTP endpoints and centralized exception handling.
- dto — request and response contracts.
- entity — persistence/domain entities.
- exception — application-specific exceptions.
- mapper — object mapping.
- repository — Spring Data repositories.
- security — JWT authentication filter and entry point.
- service — account, authentication, transaction, OTP, email, cache, and user workflows.
- util — shared utility classes.
- src/test — controller, service, cache, token, and exception tests.

## Security and operational notes

- CORS now uses a comma-separated allow-list configured by APP_CORS_ALLOWED_ORIGINS; do not set it to a wildcard for credentialed production clients.
- Only the Actuator health endpoint is intentionally public through the security filter chain. Keep other management endpoints protected.
- Database, mail, geolocation, and JWT credentials must be provided through environment variables or a secrets manager.
- OTP values are generated with SecureRandom, expire after five minutes, and are consumed after successful verification.
- OTP generation lockouts are tracked per account in a local Caffeine cache. This is suitable only for a single application instance; use a shared Redis-backed limiter before running multiple instances.
- Password-reset OTP requests return a generic response so callers cannot determine whether an email or account number is registered.
- Internal server and external-service exception details are not returned to API clients.
- The Docker Compose database and cache ports are bound to localhost for local development. Add authentication, TLS, private networking, backups, and monitored health checks before any non-local deployment.
- The sample configuration is for local development. Review database schema/migration strategy, token lifecycle, rate limits, and audit logging before using the project with real financial data.
- OTP records are still stored as plaintext in the database and should be stored as a keyed digest in a production deployment.

## License and attribution

See the LICENSE file in this directory for the project's licensing terms.
