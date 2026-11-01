# SmartHome V1.1 — Struts / Spring / Hibernate Application

This topic contains the most complete server-side Java application in the Graduation Project archive: a legacy smart-home administration web application with JSP views, Struts actions, Spring services, and Hibernate entity mappings.

## Source project

The application is located at:

`Code/SmartHomeV1.1(struts2+spring3+hibernate3)/SmartHome/`

Read the [SmartHome application guide](Code/SmartHomeV1.1(struts2+spring3+hibernate3)/SmartHome/README.md) before attempting to open or run it.

## Architecture visible in the source

- **Presentation:** JSP CRUD screens under `WebRoot/`.
- **Routing:** Struts 2 action mappings in `src/struts.xml`, registered by the Servlet filter in `WebRoot/WEB-INF/web.xml`.
- **Actions:** `src/com/rh/ssh/action/`.
- **Services:** `src/com/rh/ssh/service/` and implementation classes.
- **Persistence:** Hibernate 3 XML mappings under `src/com/rh/ssh/model/`.
- **Dependency wiring:** `src/spring-dao.xml`, `spring-service.xml`, and `spring-action.xml`.

The entities cover devices, users, projects, tasks, messages, background information, and related types/details.

## Toolchain and build limitation

The Eclipse project metadata references Tomcat 8.0, the web descriptor uses Servlet 2.4, and the Spring DAO layer uses Hibernate 3. There is no Maven POM, Gradle build file, or wrapper in the source project, and the Eclipse classpath relies on a locally installed server/runtime.

This is a legacy prototype, not a currently supported production application. Use an isolated legacy development environment and plan a staged migration before exposing it to a network.

## Security changes in this review

- Removed the hard-coded MySQL root credentials from Spring DAO XML.
- Added tracked, credential-free DB defaults and ignored local DB overrides.
- Disabled Hibernate SQL logging by default.
- Disabled Struts development mode by default.

Dynamic Method Invocation remains enabled pending review of every JSP action URL. Do not treat this as a production security certification.
