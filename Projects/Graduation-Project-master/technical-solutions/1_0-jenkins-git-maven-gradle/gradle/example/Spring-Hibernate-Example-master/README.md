# Spring + Hibernate Example (Legacy Gradle WAR)

This nested example is a small Java web application that demonstrates a Spring MVC / Hibernate persistence structure. It is separate from the larger smart-home archive and has its own Gradle build file.

## Technology declared by build.gradle

| Technology | Declared version |
| --- | --- |
| Java source compatibility | 1.7 |
| Spring Web MVC | 3.2.0.RELEASE |
| Spring/Hibernate integration artifact | 2.0.8 (legacy dependency coordinate) |
| Hibernate annotations | 3.4.0.GA |
| MySQL Connector/J | 5.1.33 |
| Apache Commons DBCP2 | 2.0.1 |
| JSTL | 1.2 |
| JUnit | 4.8.2 |
| Packaging | WAR |

This dependency set is historical and should not be used for a new public-facing service without a framework and dependency migration.

## Structure

- `src/main/java/com/lenovo/leoss/controller/` — Spring MVC controllers.
- `src/main/java/com/lenovo/leoss/dao/` — DAO contract and Hibernate DAO implementation.
- `src/main/java/com/lenovo/leoss/model/User.java` — mapped `admin_user` entity.
- `src/main/java/com/lenovo/leoss/service/UserService.java` — service layer.
- `src/main/resources/applicationContext-dao.xml` — datasource, Hibernate SessionFactory, and DAO configuration.
- `src/main/resources/config.properties` — local DB configuration template.
- `src/main/webapp/WEB-INF/` — servlet dispatch and JSP view configuration.

## Database configuration

The DAO context uses Spring's PropertyPlaceholderConfigurer to read `config.properties`. The tracked file now contains no database credentials. Create a local `config.local.properties` file in this folder to override it; that file is excluded by .gitignore.

Expected properties:

- `datasource.jdbc.driverClassName`
- `datasource.jdbc.url`
- `datasource.jdbc.username`
- `datasource.jdbc.password`
- `hibernate.dialect`
- `hibernate.show_sql`
- `hibernate.cache.use_query_cache`
- `hibernate.cache.provider_class`

Never commit a real password. Use a dedicated, least-privilege local database user.

## Build notes

The project has a Gradle build file but no checked-in wrapper. The declared build uses old `compile` and `testCompile` configurations and a private-network HTTP Maven repository in the original file. That repository has been removed; Maven Central remains configured.

The build has not been verified. Some old dependency coordinates may no longer resolve, and the local Gradle version may need to be selected to match the original build scripts. Do not describe it as working until a clean WAR build has passed.

## Next engineering work

1. Replace the legacy Spring/Hibernate dependencies with supported versions in a dedicated migration.
2. Introduce service/DAO transaction boundaries and explicit error handling.
3. Review authentication and password storage before exposing the User entity or DAO.
4. Add tests for user persistence and validation.
5. Replace Hibernate schema assumptions with versioned database migrations.
