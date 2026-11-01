# Legacy Android Smart-Home Client Prototype

This folder preserves Android client prototypes and UI components associated with the smart-home graduation archive. Despite the historical folder name referring to a music player, the checked-in code includes a smart-home client with login, registration, a main activity, a menu/navigation library, and UI fragments.

## What is included

- `MyCode/SmartHomeControlClientV1.0/SmartHomeControlClient/` — Android client source with MainActivity, LoginActivity, RegActivity, Android resources, and manifest.
- `MyCode/SmartHomeControlClientV1.0/MenuActivity/` — a separate Android menu/activity module with home, profile, settings, and calendar fragments.
- `MyCode/SmartHomeControlClientV1.0/ResideMenu/` — reusable sliding navigation component.
- Android SDK/API documentation references and historical developer notes.

## Legacy toolchain evidence

The MenuActivity module uses the old `apply plugin: 'android'` Gradle plugin syntax and references a root project configuration that is not present in this folder snapshot. Its `project.properties` targets Android API 17 and marks the module as an Android library.

The client manifest declares minimum API 8 and target API 18. These values and the plugin generation are obsolete. The client folder does not contain a standalone modern Gradle build or wrapper.

## Build status

This is not currently a reproducible modern Android Studio project. A build requires reconstructing the original root project settings, Android Gradle Plugin version, SDK/build-tools versions, dependency JARs, and project module graph.

Recommended recovery sequence:

1. Import a copy of the project into a legacy-compatible environment, not the only copy of the source.
2. Record the original package names, activities, manifest permissions, and resource references.
3. Reconstruct the root Gradle settings and module references from the original project layout.
4. Migrate the old Android plugin and support libraries in a separate branch.
5. Replace deprecated APIs and add tests before changing the authentication or network flows.

## Security and compatibility

- The manifest requests/uses internet-capable client behavior; verify all network endpoints before running the app.
- Do not add Wi-Fi passwords, server credentials, API keys, or device-control secrets to Java source, XML resources, or Gradle files.
- Use HTTPS with certificate validation for remote services.
- Review login and registration logic before using real accounts; a UI login screen alone does not establish secure authentication.
- Verify that any smart-home command is authenticated and authorized at the service/device boundary.

This folder is preserved as an archived implementation/reference, not a currently supported Android release.
