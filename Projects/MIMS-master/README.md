# MIMS — Medical Inventory Management System

MIMS is a legacy ASP.NET application for managing medical and pharmacy inventory workflows. The Visual Studio solution is split into web, business, service, entity, interface, utility, and test projects.

## Solution structure

| Project | Responsibility |
| --- | --- |
| MIMS.Web | ASP.NET MVC 5 / Web API application, controllers, views, and browser assets |
| MIMS.Business | Business logic and business-layer services |
| MIMS.IBusiness | Business interfaces and contracts |
| MIMS.Service | Service-layer components |
| MIMS.Entity | Shared entities and data models |
| MIMS.Utilities | Shared utilities |
| MIMS.Web.Tests | MSTest-based unit and controller tests |

## Technology detected in the project files

- C# and .NET Framework 4.5
- ASP.NET MVC 5.2.3 and ASP.NET Web API 2.2 (5.2.3 packages)
- Dapper 1.42
- Newtonsoft.Json 8.0.3
- Razor / WebPages 3.2.3
- SQL Server through System.Data.SqlClient
- Visual Studio solution format from the Visual Studio 2013 generation

These are the versions declared by the checked-in project and NuGet configuration files. This is a legacy stack and should be treated as a maintenance/learning project until dependencies and runtime support are modernized.

## Prerequisites

- Windows
- Visual Studio with the ASP.NET and web development workload
- The .NET Framework 4.5 targeting/developer pack required by the solution
- SQL Server with the MIMS and PharmacySystem databases provisioned
- NuGet package restore access

## Open and build

1. Open MIMS.sln in Visual Studio.
2. Restore NuGet packages for the solution.
3. Create the local SQL Server connection configuration as described below.
4. Select MIMS.Web as the startup project.
5. Build the solution, then run it using IIS Express or the configured local IIS profile.

The solution uses old non-SDK-style project files and .NET Framework 4.5. It is not a cross-platform .NET CLI project.

## Local SQL Server configuration

The tracked Web.config and test App.config reference an external file named connectionStrings.config. This keeps environment-specific database credentials out of the tracked application configuration.

For local development:

1. Copy MIMS.Web/connectionStrings.config.example to MIMS.Web/connectionStrings.config.
2. Copy MIMS.Web.Tests/connectionStrings.config.example to MIMS.Web.Tests/connectionStrings.config.
3. Edit each local file for your SQL Server instance and database authentication method.
4. Keep the real connectionStrings.config files untracked; the root .gitignore excludes them.

The examples use Windows Integrated Security. If you need SQL authentication, put the username and password only in your local ignored files or a deployment secret store. Never put production credentials in Web.config, App.config, screenshots, issue comments, or commits.

The application expects two named connections: MIMS and PharmacySystem. Ensure the corresponding databases and schema exist before running the application or its integration tests.

## Tests

MIMS.Web.Tests is a classic MSTest project targeting .NET Framework 4.5. Open the solution in a compatible Visual Studio installation, restore packages, configure the local test connection strings, and run tests through Test Explorer.

Test execution has not been verified as part of this repository review. Older test projects may require a compatible Visual Studio Test Adapter and local database fixtures.

## Security and maintenance backlog

- Rotate any SQL Server credentials that were previously committed. Removing a password from the current files does not remove it from earlier Git commits.
- Review every database query for parameterization; replace any SQL string concatenation that uses request or form input.
- Audit authentication, authorization attributes, role filters, and session handling across controllers.
- Set debug=false for production builds and review error handling and sensitive-data disclosure.
- Upgrade the application from .NET Framework 4.5 to a supported target where feasible; plan a staged migration from ASP.NET MVC 5 / Web API 2 to modern ASP.NET Core.
- Review old frontend dependencies (including bundled jQuery and EasyUI assets) for known security and compatibility issues.
- Add automated integration tests using disposable databases rather than shared development or production data.

## Scope note

This update improves repository configuration hygiene and project documentation. It does not modernize the legacy framework or certify the application as production-ready.
