# inventory-management-system-main

## Description
Project inventory-management-system-main: management system built with Java, HTML/CSS, XML, SQL. This folder contains the source code and resources needed to review, run, and adapt the solution as part of the portfolio.

## What It Does
- Provides a practical solution related to the project name: inventory-management-system-main.
- Includes source files, resources, and configuration needed to study or run the application.
- Works as an individual project entry in Joseff Antonio Laverde Avendano's portfolio.

## Detected Technologies
- Java
- HTML/CSS
- XML
- SQL

## Requirements
- JDK 8 or newer
- A database engine compatible with the included SQL scripts

## Installation
1. Clone or download this portfolio repository.
2. Open the Projects/inventory-management-system-main folder.
3. Download dependencies and build with `mvn clean install`.

## Usage
- `mvn clean install`
- `mvn exec:java  # if the pom defines a main class`

## Main Structure
- `.gitignore`
- `database/inventory_management_system.sql`
- `dependency-reduced-pom.xml`
- `pom.xml`
- `README.md`
- `src/main/java/com/inventorymanagementsystem/app/Launcher.java`
- `src/main/java/com/inventorymanagementsystem/Application.java`
- `src/main/java/com/inventorymanagementsystem/BillsController.java`
- `src/main/java/com/inventorymanagementsystem/config/Database.java`
- `src/main/java/com/inventorymanagementsystem/DashboardController.java`
- `src/main/java/com/inventorymanagementsystem/entity/Billing.java`
- `src/main/java/com/inventorymanagementsystem/entity/Customer.java`
- `src/main/java/com/inventorymanagementsystem/entity/Invoice.java`
- `src/main/java/com/inventorymanagementsystem/entity/Product.java`
- `src/main/java/com/inventorymanagementsystem/entity/Purchase.java`
- `src/main/java/com/inventorymanagementsystem/entity/Sales.java`
- `src/main/java/com/inventorymanagementsystem/entity/User.java`
- `src/main/java/com/inventorymanagementsystem/LoginController.java`
- `src/main/java/module-info.java`
- `src/main/resources/application.properties`
- `src/main/resources/com/inventorymanagementsystem/bills.css`
- `src/main/resources/com/inventorymanagementsystem/bills.fxml`
- `src/main/resources/com/inventorymanagementsystem/dashboard.css`
- `src/main/resources/com/inventorymanagementsystem/dashboard.fxml`
- `src/main/resources/com/inventorymanagementsystem/login.css`

## Notes
- If the project uses a database, review the `.sql` files, connection properties, or internal documentation before running it.
- If compiled output exists (.class, 	arget, build, bin), rebuild from source to ensure compatibility with your local environment.
- Some academic projects may need to be opened with an IDE such as NetBeans, Eclipse, IntelliJ IDEA, or Android Studio.

## Author
Joseff Antonio Laverde Avendano
