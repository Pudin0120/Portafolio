# CI/CD, Git, Maven, and Gradle Research

This section preserves historical notes about source control, Jenkins pipelines, Maven, Gradle, Eclipse integration, and Java web application builds.

## Included examples

- **JavaGradleWebDriver-master/** — a standalone Gradle Java project using Selenium 2.41.0 and JUnit 4.10.
- **Spring-Hibernate-Example-master/** — a legacy Gradle WAR example using Java 7-era compatibility, Spring MVC 3.2.0, Hibernate 3 annotations, MySQL Connector/J 5.1.33, and DBCP2.
- **Historical references** — older tutorials and links for Git, Jenkins, Maven and Gradle integration.

## Current condition

- The nested examples do not include Gradle wrappers.
- The Gradle files use the removed `compile` and `testCompile` dependency configurations.
- The Spring/Hibernate example's original private HTTP Maven repository and JCenter entry were removed. Maven Central remains configured.
- Old tutorial links may be unavailable or obsolete.
- Dependency resolution and a WAR/JAR build have not been verified.

## Recommended use

Use these projects as reference material for understanding earlier Java build pipelines. For a new project, prefer a checked-in Gradle wrapper, maintained plugins, pinned dependencies, HTTPS repositories, and an automated build/test workflow. Do not copy old dependency versions into a new application without a compatibility and security review.
