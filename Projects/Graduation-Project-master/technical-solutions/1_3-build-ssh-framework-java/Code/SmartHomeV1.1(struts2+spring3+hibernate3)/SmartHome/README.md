# SmartHome V1.1 — Struts 2 / Spring 3 / Hibernate 3 Web Application

This subproject is a legacy Java web application for administering smart-home content and entities. Its source includes Struts actions, Spring services, Hibernate mappings, and JSP CRUD screens.

## Application structure

| Layer | Source location | Responsibility |
| --- | --- | --- |
| Web views | WebRoot/ | JSP screens for device, message, project, task, user, and background-content records |
| Web routing | src/struts.xml and WebRoot/WEB-INF/web.xml | Struts 2 action mappings and servlet filter |
| Actions | src/com/rh/ssh/action/ | Request/action controllers |
| Services | src/com/rh/ssh/service/ | Business service interfaces and implementations |
| DAO | src/com/rh/ssh/dao/ | Hibernate persistence access |
| Models | src/com/rh/ssh/model/ | Java entities and Hibernate mapping XML |
| Dependency wiring | src/spring-*.xml | Spring bean and transaction configuration |

The visible entity/mapping set includes background information/images/types, devices, messages/types, project and task details, projects, tasks, and users.

## Legacy toolchain evidence

The checked-in Eclipse classpath references Apache Tomcat 8.0. The web descriptor uses Servlet 2.4, and the Struts configuration uses the Struts 2.0 DTD. The Spring configuration uses Hibernate 3 integration. These are legacy dependencies.

The folder contains Eclipse project metadata but no Maven POM, Gradle build file, Gradle wrapper, or vendored dependency set sufficient for a reproducible command-line build. The classpath also relies on Eclipse/Tomcat server runtime configuration.

## Database configuration

The Spring DAO configuration now reads local settings from:

1. classpath:db.properties (tracked defaults with empty credentials)
2. file:db.local.properties (optional local override, not tracked)

Copy `db.local.properties.example` to `db.local.properties` in the SmartHome application's working directory, then set the database URL, user, and password. Use a dedicated local database account with only the required schema privileges. Do not use MySQL root.

Hibernate SQL and formatted SQL logging are disabled by default to reduce accidental disclosure of data in logs.

## Importing into a legacy IDE

1. Work on a separate copy of the source.
2. Use an environment compatible with the historical Eclipse Web Tools Project metadata and Tomcat 8 runtime.
3. Import the SmartHome folder as an existing Eclipse web project.
4. Restore the exact Struts/Spring/Hibernate libraries required by the imports and XML configuration.
5. Configure the local database properties and schema before launching.
6. Deploy only to an isolated local environment until dependencies and security have been reviewed.

There is no one-line Maven or Gradle command for this project in the current repository snapshot.

## Security and maintenance findings

- The tracked Spring DAO XML previously contained a hard-coded MySQL root account and password. These are now read from local configuration and must not be reintroduced into source control.
- Struts development mode is disabled in the action configuration.
- Dynamic Method Invocation is still enabled in struts.xml because the existing JSP/action call patterns have not yet been fully audited. Review action mappings and disable it if no routes depend on it.
- Review every JSP output for HTML escaping and every action method for authorization and input validation.
- Review Hibernate DAO operations for transaction and ownership boundaries.
- Upgrade Struts, Spring, Hibernate, Servlet APIs, and the Java runtime only in a separate migration with integration tests.
- Use HTTPS and authenticated/authorized device-control endpoints before connecting this prototype to real hardware.

## Verification status

This review externalized database credentials and disabled SQL logging and Struts development mode. It did not compile the application, connect to a database, or verify the full UI/CRUD workflow.
