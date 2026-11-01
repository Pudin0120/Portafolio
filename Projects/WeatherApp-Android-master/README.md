# Weather Forecast — Android

A native Android weather application built with Java and AndroidX. It displays current conditions and a multi-day forecast using OpenWeatherMap, supports city search and voice input, and can use the device's foreground location after the user grants permission.

## Technology stack

| Component | Version |
| --- | --- |
| Language | Java 8 |
| Android Gradle Plugin | 7.4.2 |
| Gradle | 7.5 |
| Compile / target SDK | 33 / 33 |
| Minimum SDK | 19 |
| AndroidX AppCompat | 1.6.1 |
| Material Components | 1.9.0 |
| Volley | 1.2.1 |
| Google Play Services Location | 21.0.1 |
| JUnit | 4.13.2 |
| AndroidX Test | 1.1.5 / Espresso 3.5.1 |

## Requirements

- Android Studio with an Android SDK that includes API 33.
- JDK 11 to run the Gradle 7.5 / Android Gradle Plugin 7.4.2 build.
- A valid OpenWeatherMap API key with access to the endpoints used by this application.
- An Android emulator or device for runtime testing.

## Configure the weather API key

The API key is no longer stored in the source code. Supply it locally as a Gradle property named WEATHER_API_KEY.

PowerShell:

    $env:WEATHER_API_KEY = "YOUR_NEW_OPENWEATHERMAP_KEY"
    gradle --no-daemon :app:assembleDebug

Linux/macOS:

    export WEATHER_API_KEY="YOUR_NEW_OPENWEATHERMAP_KEY"
    gradle --no-daemon :app:assembleDebug

Alternatively, add WEATHER_API_KEY=YOUR_NEW_OPENWEATHERMAP_KEY to your user-level Gradle properties file (~/.gradle/gradle.properties), not to the repository.

The value is injected into the generated BuildConfig class at build time. **A key included in a mobile APK can still be extracted.** Use a dedicated key with usage/quota restrictions if supported by the provider, monitor usage, and consider a backend proxy for a production application. Never commit a real key.

The previous source revision contained an exposed API key. Revoke or rotate that key in the OpenWeatherMap account; removing it from the latest source does not erase it from Git history or previously built APKs.

## Build

The repository contains the Gradle wrapper scripts but does not include gradle-wrapper.jar. Install Gradle 7.5 (or use Android Studio's configured Gradle installation), then run:

    gradle --version
    gradle --no-daemon :app:assembleDebug

The debug APK is generated at:

    app/build/outputs/apk/debug/app-debug.apk

A GitHub Actions job also builds the app using Gradle 7.5 and Java 11. The CI build deliberately has no API key: it verifies compilation, not live weather-service access.

## Features

- Current weather conditions and daily forecast.
- Search by city name.
- Device location lookup with foreground location permission.
- Voice-assisted city search.
- Weather condition icons and localized weekday labels.
- Pull-to-refresh and online connectivity checks.

## Improvements in this revision

- Removed the API key from Java source and read it from a local Gradle property or environment variable.
- Encoded URL query parameters using Android's Uri.Builder.
- Requested metric units explicitly and converted wind speed from metres per second to kilometres per hour for the existing UI labels.
- Reused the single forecast response for all forecast rows instead of issuing a separate network request for every row.
- Added null-safe location and geocoder handling.
- Replaced deprecated, null-prone connectivity lookups with NetworkCapabilities on Android 6.0+ and a guarded legacy fallback.
- Added user-facing handling for missing configuration and failed weather requests.
- Removed the duplicate initial weather fetch caused by both onCreate and onResume.

## Known limitations / next steps

- The One Call endpoint and subscription requirements must be confirmed against the current OpenWeatherMap plan; this source still uses the One Call 2.5 endpoint.
- A client-side API key is not a true secret. A backend proxy is the stronger production design.
- Add automated unit tests for URL construction, weather response parsing, and location fallback behavior.
- Consider migrating the deprecated Play Core in-app update dependency to the current Play in-app updates library.
- Replace the fixed six-day forecast count with the number of forecast entries actually returned by the provider.
- Add a user-facing city-only mode when location permission is denied, and test permission revocation while the app is running.
- Run device/emulator tests for Android 13+ notification, location, and network behavior before release.

## Author

Joseff Antonio Laverde Avendaño
