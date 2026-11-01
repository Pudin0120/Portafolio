# Smart Home Graduation Project Archive

This directory preserves an **archived smart-home prototype workspace** and its supporting technical research. It is not one single application with a root-level build. The repository contains design documents, a rendered GitBook manual, Android client prototypes, database scripts, and separate examples used to investigate web services, WebSocket/WebRTC communication, Django, Spring/Hibernate, Gradle, Jenkins, and Git.

## Project context

The original notes describe a connected smart-home concept combining a mobile client, a server/web layer, communication services, and embedded/ARM Wi-Fi components. The included materials are a mixture of design artifacts, tutorials, experiments, and partial implementations from different development stages.

The project should therefore be treated as a **historical prototype and engineering research archive**, not as a verified end-to-end smart-home product.

## Repository map

| Folder | What it contains |
| --- | --- |
| development-documents/ | Design notes, task lists, phase-one prototype diagrams, and a generated GitBook |
| development-documents/_book/ | Locally rendered HTML documentation; open index.html in a browser |
| development-documents/phase-one-prototype-documents/ | Smart-home prototype diagrams and modeling source files |
| module-prototype-development/ | Early WebSocket and Android integration notes |
| technical-solutions/ | Topic-based research and isolated implementation examples |
| related-assets/ | UI reference images, icons, fonts, and design material |
| technical-solutions/1_0-jenkins-git-maven-gradle/ | Historical CI/CD, Git, Maven, and Gradle notes plus example Gradle projects |
| technical-solutions/1_1-build-django-framework-and-admin-system-python/ | Django research notes, Python exercises, and smart-home SQL design scripts |
| technical-solutions/1_2-android-music-player-implementation/ | Legacy Android client/menu prototypes and Android SDK references |
| technical-solutions/1_3-build-ssh-framework-java/ | SSH/MVC framework research |
| technical-solutions/1_4-implement-webservice/ | Web-service research and Spring XML schemas |
| technical-solutions/1_5-implement-websocket-webrtc/ | WebSocket/WebRTC research |
| technical-solutions/1_6-smart-home-website-design/ | Website design research |
| technical-solutions/1_7-detect-device-online-status/ | Device presence/online-status research |
| technical-solutions/1_8-implement-server-push/ | Server-push research |
| technical-solutions/1_9-cloud-platform-selection/ | Cloud-platform selection notes |

## Start here

1. Read this overview to understand the archive boundaries.
2. Open [the generated project documentation](development-documents/_book/index.html) for the available design and requirements notes.
3. Review [the prototype diagrams](development-documents/phase-one-prototype-documents/) before studying implementation experiments.
4. Use the [technical solutions index](technical-solutions/README.md) to choose an individual topic.
5. For the legacy Android modules, start with [the Android client notes](technical-solutions/1_2-android-music-player-implementation/README.md).

## Build and runtime status

There is no root Maven POM, Gradle settings file, Gradle wrapper, Django manage.py project, or single application entry point at this directory level. The command `mvn clean install` is **not** a valid universal build command for this archive.

Some nested examples have their own build files:

- The Selenium/Gradle example declares Selenium 2.41.0 and JUnit 4.10.
- The Spring/Hibernate example is a legacy Java 7-era WAR project with Spring 3.2.0-era dependencies and MySQL Connector/J 5.1.33.
- The Android client uses the old Android Gradle plugin syntax in one submodule and legacy Android SDK/Ant metadata in related modules. The checked-in manifest targets Android API 18 and declares a minimum API 8.

Those dependencies and SDK levels are historical. They may not build with current JDK, Android Gradle Plugin, Android SDK, or repository services without a migration.

## Data, secrets, and safe usage

- Treat SQL files as schema/design samples. Inspect them and import only into a disposable local database.
- Do not put actual database passwords, API keys, Firebase credentials, signing keys, or Wi-Fi credentials into tracked properties/XML/Gradle files.
- Replace old dependency repositories and unmaintained packages only as part of a tested migration; do not upgrade a legacy framework blindly.
- Do not flash or connect prototype embedded hardware to real installations until communication security, authentication, firmware integrity, recovery behavior, and electrical safety have been validated.
- UI images and third-party design resources are retained as historical assets; review their licenses before redistribution.

## Recommended modernization sequence

1. Identify one deployable vertical slice (mobile client, service API, or embedded control path).
2. Write down the supported hardware and protocol contracts before changing code.
3. Create reproducible builds with pinned, maintained toolchains for that slice.
4. Move all credentials and environment-specific values to ignored local configuration or a secrets manager.
5. Add tests for protocol parsing, authentication, and device state transitions.
6. Replace legacy Android/Java dependencies only after the selected slice is covered by tests.
7. Keep design artifacts, examples, and complete applications clearly separated.

## Verification statement

This archive review improves navigation and setup guidance and removes a tracked local database username from one legacy example configuration. It does not claim that the full smart-home prototype compiles, that hardware is connected, or that the end-to-end system has been deployed or tested.
