# Web-Service Integration Research

This folder currently contains Spring XML schema files (`core.xsd` and `servlet.xsd`) and historical notes. It does not contain a complete SOAP/REST service implementation, controller, build descriptor, or deployable web-service application.

## What is present

- `webservice+spring/core.xsd`
- `webservice+spring/servlet.xsd`

These are schema resources for Spring XML configuration, not service endpoints by themselves.

## How to continue this topic

1. Define the service contract and request/response schemas.
2. Decide whether the integration should be REST/JSON or SOAP/XML.
3. Add a reproducible build and maintained framework dependencies.
4. Implement validation, authentication, authorization, error mapping, and integration tests.
5. Document endpoint URLs and versioning only after a runnable service exists.

This folder is kept as a research reference. No web-service runtime or API is claimed here.
