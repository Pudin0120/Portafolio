# Project Improvement Log

This document tracks the ongoing review of the 160 project folders under Projects/. Work is prioritized by application scope, architectural complexity, security exposure, and value as a portfolio project.

The repository is being improved incrementally. Original source folders are preserved; changes are limited to concrete issues found during review. A project is not marked as tested or production-ready unless its build and relevant runtime behavior have actually been verified.

## Batch 1 — high-priority projects

| Project | Review status | Improvements applied | Verification status |
| --- | --- | --- | --- |
| Metal / ServiPerfiles | Improved | Rewrote root/backend/frontend documentation; clarified FastAPI hexagonal architecture and React frontend setup; corrected the Vite config to load VITE_ environment values in config and omit the API proxy when no target is configured. | Not built or integration-tested in this review. |
| BankingPortal-API-main | Improved | Aligned Docker runtime with Java 17; moved DB/JWT/mail/geolocation values to environment variables; replaced wildcard CORS with a configurable allow-list; limited the public actuator route to health; restricted local Docker port bindings; removed a tracked mail credential; replaced invalid PMD ruleset locations; documented setup and limitations. | Maven package passed in Java batch 1 CI (tests skipped). Existing test configuration and external service assumptions still need review. |
| inventory-management-system-main | Improved | Removed duplicate Maven dependencies and a conflicting JavaFX version; standardized Java 11 compiler release; moved JDBC credentials to environment variables; parameterized invoice lookup in JasperReports; removed the weak admin/admin SQL seed; rewrote setup and security documentation. | Maven package passed in Java batch 1 CI (tests skipped). Password storage in the current login flow is still plain text and must be redesigned before real-user use. |
| MIMS-master | Improved | Removed embedded SQL credentials from Web.config and test App.config using external configSource files; added safe local Integrated Security examples; ignored local credential files; documented the legacy .NET Framework 4.5 solution and maintenance risks. | Not built; requires Windows/Visual Studio and the .NET Framework targeting pack. Previously committed SQL credentials must be rotated. |
| FOTA_Graduation-Project-2022-main | Improved | Rewrote project overview and the NodeMCU/Server setup guides; documented ARM firmware layers, ESP32 telematics, Raspberry Pi UI entry point, server integration, and firmware-update safety checks. | No firmware build, board flash, Firebase integration, or end-to-end test executed. |
| E-commerce-project-springBoot-master | Improved | Externalized datasource credentials and SQL logging defaults; removed predictable demo account seeds; rewrote setup/authentication/security documentation. Source already hashes new passwords with BCrypt and upgrades legacy plain-text records on user load. | Maven package passed in Java batch 1 CI (tests skipped); no runtime or database migration test executed. |
| Train-Ticket-Reservation-System-master | Improved | Added PBKDF2-HMAC-SHA-256 salted password storage; migrate legacy passwords on successful login; corrected INSERT execution; made password change persist and verify old password; moved Oracle credentials to environment variables; removed credential logging; reduced schema grants from DBA; removed public demo account seeds; widened password columns. | Maven WAR package passed in Java batch 1 CI (tests skipped); Oracle database and servlet-container workflows not executed. DBUtil still uses a single static connection and needs a connection-pool refactor. |
| JavaCodes | Improved / Java source archive | Replaced generic README with a navigable index across 228 source files; recorded 41 groups of exact byte-for-byte duplicates without deleting files; improved OpenWeatherMap example to use HTTPS, environment-based API key, URL encoding, timeouts and safe error handling; improved host checker with URL validation, HTTPS default, timeouts, HEAD/GET fallback and safe disconnect. | The two reviewed utility classes are being added to a Java 8 compilation check; the remaining 226 source files have not been compiled as a group because they are independent programs with duplicate classes and inconsistent filenames. Password-manager experiments remain educational only; one uses obsolete PBEWithMD5AndDES with a fixed salt and very low iteration count. |
| back-end--chat-api | Documentation improved / build blocked | Rewrote README to describe the Spring/Jakarta, DDD and SSE architecture and explicitly record that no Maven/Gradle build descriptor or wrapper is present. | Cannot compile reproducibly until dependency versions and a build descriptor are added. |
| Graduation-Project-master | Improved / archived multi-project workspace | Replaced generic root README and broken topic READMEs with a verified map; documented the offline GitBook, SQL/Python exercises, legacy Android client, Gradle examples, Struts/Spring/Hibernate SmartHome web application, and research-only WebSocket/WebRTC, web-service, device-presence, server-push, and cloud topics. Removed a hard-coded MySQL account/password from SmartHome Spring XML; added ignored local DB overrides; disabled Hibernate SQL logging and Struts dev mode; removed a private HTTP Maven repository/JCenter from the sample Gradle build; fixed a malformed Android manifest tag. | Not compiled. No root build descriptor; nested examples use legacy toolchains. Credentials removed from current tree may remain in Git history and must be rotated if real. |

## Build verification — Java batch 1

GitHub Actions run: https://github.com/Pudin0120/Portafolio/actions/runs/41273225712

| Project | Result | Scope |
| --- | --- | --- |
| Banking Portal API | Success | Maven package with Java 17; test execution skipped. |
| E-commerce application | Success | Maven package with Java 11; test execution skipped. |
| Inventory desktop app | Success | Maven package with Java 11; test execution skipped. |
| Train reservation application | Success | Maven package with Java 8; test execution skipped. |

All four compile/package jobs completed successfully after the Banking Portal import fix. This is a compile/package check only, not functional QA or a security certification.

## Batch 2 — next review queue

The next projects to inspect are:

1. onlinebookstore-master — inspect web stack, authentication, database configuration, and checkout/cart flows.
2. employer-worker-registration-system-main — inspect data validation, account handling, and database access.
3. WeatherApp-Android-master — inspect Android Gradle configuration, API keys, lifecycle, and network handling.
4. Women-Safety-App-master — inspect permissions, location/safety workflows, API usage, and privacy.
5. Lost and Found — inspect persistence, identity handling, and input validation.
6. Remaining reservation, inventory, education, and CRUD applications — review by completeness and reuse potential.

## Engineering baseline for every project

- Confirm the actual language/runtime/framework versions from build files.
- Make setup instructions reproducible and remove generated or incorrect README boilerplate.
- Keep passwords, tokens, private keys, database credentials, and service-account files outside version control.
- Prefer parameterized SQL and validated DTOs over string-built queries.
- Close file, database, and network resources reliably.
- Add focused tests for domain rules and critical user workflows.
- Document known gaps rather than inventing features or claiming unverified deployments.
- Keep original project data and source files unless there is a clear, reviewed reason to change them.

## Security follow-up required

Some credentials removed from current files were already present in previous Git commits (including legacy SQL/database configuration values). Removing them from the latest version does not erase the old history. Rotate any real credentials that were committed, then consider a coordinated history cleanup only after backups and collaborators are prepared.

## Important status rule

“Improved” means that code, configuration, or documentation changes were made. It does not mean that a project has passed compilation, automated tests, manual QA, security review, or production-readiness assessment. The GitHub Actions workflow added in this batch performs build-only checks for the Java projects listed above; it skips test execution.
