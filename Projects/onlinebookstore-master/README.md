# onlinebookstore-master

## Description
Project onlinebookstore-master: management system built with Java, HTML/CSS, XML, SQL, DevOps/Cloud. This folder contains the source code and resources needed to review, run, and adapt the solution as part of the portfolio.

## What It Does
- Provides a practical solution related to the project name: onlinebookstore-master.
- Includes source files, resources, and configuration needed to study or run the application.
- Works as an individual project entry in Joseff Antonio Laverde Avendano's portfolio.

## Detected Technologies
- Java
- HTML/CSS
- XML
- SQL
- DevOps/Cloud

## Requirements
- JDK 8 or newer
- A database engine compatible with the included SQL scripts

## Installation
1. Clone or download this portfolio repository.
2. Open the Projects/onlinebookstore-master folder.
3. Download dependencies and build with `mvn clean install`.

## Usage
- `mvn clean install`
- `mvn exec:java  # if the pom defines a main class`
- `Open in a browser: WebContent/index.html`

## Main Structure
- `.classpath`
- `.gitignore`
- `.project`
- `appspec.yaml`
- `buildspec.yaml`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `Dummy_Database.md`
- `Jenkinsfile`
- `pom.xml`
- `Procfile`
- `README.md`
- `scripts/start_server.sh`
- `scripts/stop_server.sh`
- `setup/CreateDatastore.sql`
- `src/main/java/com/bittercode/constant/BookStoreConstants.java`
- `src/main/java/com/bittercode/constant/db/BooksDBConstants.java`
- `src/main/java/com/bittercode/constant/db/UsersDBConstants.java`
- `src/main/java/com/bittercode/constant/ResponseCode.java`
- `src/main/java/com/bittercode/model/Address.java`
- `src/main/java/com/bittercode/model/Book.java`
- `src/main/java/com/bittercode/model/Cart.java`
- `src/main/java/com/bittercode/model/package-info.java`
- `src/main/java/com/bittercode/model/StoreException.java`
- `src/main/java/com/bittercode/model/User.java`

## Notes
- If the project uses a database, review the `.sql` files, connection properties, or internal documentation before running it.
- If compiled output exists (.class, 	arget, build, bin), rebuild from source to ensure compatibility with your local environment.
- Some academic projects may need to be opened with an IDE such as NetBeans, Eclipse, IntelliJ IDEA, or Android Studio.

## Author
Joseff Antonio Laverde Avendano
