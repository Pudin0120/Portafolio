# Technical Solutions Index

This folder collects research notes and separate implementation experiments for the smart-home graduation prototype. These are not modules in a single root build.

| Topic | Folder | Scope in this archive |
| --- | --- | --- |
| CI/CD and build tools | 1_0-jenkins-git-maven-gradle/ | Git, Jenkins, Maven/Gradle references and sample Java projects |
| Django and database design | 1_1-build-django-framework-and-admin-system-python/ | Django learning notes, Python exercises, SQL schema/design files |
| Android client | 1_2-android-music-player-implementation/ | Legacy Android menu/client projects, ResideMenu library, SDK references |
| SSH / MVC framework | 1_3-build-ssh-framework-java/ | Framework research notes and links |
| Web services | 1_4-implement-webservice/ | Spring/web-service references and XML schema files |
| WebSocket and WebRTC | 1_5-implement-websocket-webrtc/ | Communication protocol research |
| Smart-home website design | 1_6-smart-home-website-design/ | Web interface design references |
| Device online status | 1_7-detect-device-online-status/ | Presence and status research |
| Server push | 1_8-implement-server-push/ | Push notification and server-event research |
| Cloud platform | 1_9-cloud-platform-selection/ | Hosting/cloud selection notes |

## How to use these materials

- Treat links and tutorial references as historical research, not necessarily current documentation.
- Read the README inside the topic folder before opening its sample code.
- The Gradle examples are independent projects with separate build files; they do not share one root Gradle wrapper.
- The Android client is based on old Android tooling and SDK metadata. Modern Android Studio may require a migration before it can build.
- The SQL files are design samples; inspect statements and run only against disposable development databases.

## Known archive limitations

- Several README files inherited from the original archive contain incomplete or garbled text. This index replaces the former generic topic README with a usable navigation map.
- Some nested examples depend on old repositories, old JDK/Android versions, or unpinned transitive dependencies.
- No end-to-end smart-home backend/mobile/embedded integration test is included in this archive review.
