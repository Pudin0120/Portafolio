# Loop Backend — Real-Time Messaging API

Loop Backend is a Java/Spring Boot application organized around a messaging domain. The source tree includes user and conversation aggregates, message handling, persistence adapters, application services, and server-sent event (SSE) notifications.

## What is present in this repository

- Spring Boot application entry point: java/com/abe762/loop_backend/LoopBackendApplication.java
- Messaging domain: conversations, messages, message identifiers, message states, and repository contracts.
- User domain: user aggregates and value objects.
- Persistence adapters: Jakarta Persistence entities and repository implementations.
- Real-time notifications: Spring application events and Spring MVC SseEmitter.
- Auditing base entity and builder generation annotations.

## Architecture

The source follows a domain-oriented / ports-and-adapters structure:

| Area | Responsibility |
| --- | --- |
| messaging/domain | Message and conversation aggregates, value objects, services, and repository interfaces |
| user/domain | User aggregate and user value objects |
| infrastructure/secondary/entity | Persistence entities and ORM mappings |
| infrastructure/secondary/message | Notification delivery and infrastructure adapters |
| application services | Coordinate use cases and domain operations |
| shared | Shared state/result and auditing abstractions |

The application class is annotated with SpringBootApplication. The code also imports Spring MVC, Spring Scheduling, Jakarta Persistence, Hibernate, SLF4J, and Jilt builder annotations.

## Important build gap

No Maven POM, Gradle build file, wrapper, or dependency lock file was found in this project folder during the repository review. The source therefore does not currently provide a reproducible build command.

The project appears to use Jakarta Persistence and Spring Boot-era APIs. Do not try to compile individual entity files with javac; they depend on framework classes and annotation processing.

Before adding a build descriptor, confirm and pin:
- Spring Boot and Java target versions.
- Spring Data JPA / Hibernate and database driver.
- Jilt annotation processor configuration for generated builders.
- Database configuration and migration approach.
- Test framework and any external integrations.

## Recommended next steps

1. Add a Maven or Gradle build with pinned dependencies and annotation processing.
2. Add externalized datasource settings and a local example configuration; never commit database passwords.
3. Add schema migrations and define the supported database engine.
4. Add unit tests for message/conversation domain rules and integration tests for persistence adapters.
5. Test SSE emitter registration, disconnect cleanup, heartbeat scheduling, and concurrent access to emitter collections.
6. Document authentication and authorization boundaries, especially which users can read or delete conversations.
7. Add health checks, structured logging, request validation, and API documentation.

## Verification status

This page documents the source structure and the missing build metadata. No dependency versions, build command, runtime deployment, or test result is claimed until a reproducible build is added and run.
