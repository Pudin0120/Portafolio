# Java Gradle WebDriver Example

This independent example demonstrates browser automation with Selenium and JUnit.

## Declared dependencies

- Selenium Java 2.41.0
- JUnit 4.10
- Gradle Java plugin

The dependency declarations use Gradle's legacy `compile` configuration. The repository does not contain a Gradle wrapper in this nested example.

## Source layout

- `src/main/java/pages/` — page-object classes.
- `src/main/java/flow/` — browser workflow helpers.
- `src/main/java/support/` — WebDriver lifecycle and browser helpers.
- `src/main/resources/config.properties` — browser choice and target URL.
- `src/test/java/` — example test classes.

## Build status

This is an archived Selenium 2-era project. Browser-driver management and APIs have changed substantially. A modern version should use a current Selenium release, JUnit 5 (or intentionally retain JUnit 4), an explicit browser/driver strategy, and a Gradle wrapper.

No build or browser test was executed as part of this repository review.
