# Testing and Seeding Guide

This guide explains how to run tests and seed the database with sample data.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.12+ (for local testing)
- PostgreSQL running (either in Docker or locally)

## Running Tests

### Option 1: Inside Docker Container (Recommended)

This is the simplest option and ensures the environment matches production:

```bash
# Start the development environment
task dev-up

# Run tests inside the container
task dev-test

# Or run specific tests
task dev-test -- tests/infrastructure/test_product_repository.py -v
```

### Option 2: Locally (Outside Docker)

If you want to run tests on your local machine:

1. **Start the PostgreSQL database:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d db
   ```

2. **Run the tests:**
   ```bash
   ./scripts/run-tests-locally.sh
   ```
   
   Or manually:
   ```bash
   export TEST_LOCAL=true
   pytest
   ```

The test configuration will automatically detect if you're running outside Docker and use `localhost` instead of `db` for the database connection.

## Seeding the Database

### Option 1: Inside Docker Container

```bash
# Ensure the development environment is running
task dev-up

# Run the seed script
task seed-materials-dev
```

### Option 2: Locally (Outside Docker)

1. **Start the PostgreSQL database:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d db
   ```

2. **Run the seed script:**
   ```bash
   ./scripts/run-seed-locally.sh
   ```
   
   Or manually:
   ```bash
   python seed_materials_products.py
   ```

The seed script will automatically detect if you're running outside Docker and use `localhost` for the database connection.

## Seed Data Overview

The seed script creates:

### Materials (with different measurement strategies):
- **Acero galvanizado** (SHEET strategy)
  - Calibre 14 (1.9mm) - $2.50/m
  - Calibre 16 (1.5mm) - $2.00/m
  - Calibre 18 (1.2mm) - $1.75/m

- **Tubo rectangular** (TUBE strategy)
  - 1" x 1" x 1.5mm - $8.50/m
  - 1" x 2" x 1.5mm - $9.75/m
  - 2" x 2" x 2mm - $15.00/m

- **Pintura** (LIQUID strategy)
  - Esmalte industrial negro - $12.50/L
  - Anticorrosivo rojo - $11.00/L

- **Tornillos** (SOLID strategy)
  - M6 x 20mm - $0.15/unit
  - M8 x 25mm - $0.25/unit

### Products:

#### Simple Products (individual components):
- **Puerta corrediza simple** - $350.00
  - Panel de acero calibre 14
  - Marco de tubo rectangular 2"x2"
  - Pintura anticorrosivo y esmalte
  - Tornillos de montaje

- **Ventana abatible** - $280.00
  - Panel de acero calibre 16
  - Marco de tubo rectangular 1"x2"
  - Pintura y tornillos

#### Composite Products (complete assemblies):
- **Porton residencial completo** - $1,250.00
  - 2x Puerta corrediza simple
  - 1x Ventana abatible
  - Guias superiores e inferiores
  - Kit de herrajes

## Verifying the Data

After seeding, you can verify the data:

1. **Using the API:**
   ```bash
   # Start the backend if not already running
   task dev-up
   
   # Visit the API docs
   open http://localhost/docs
   
   # Or use curl (requires authentication)
   curl http://localhost/api/materials
   curl http://localhost/api/products
   ```

2. **Using psql:**
   ```bash
   docker exec -it postgres-db psql -U user -d serviperfiles_db
   ```
   
   Then run:
   ```sql
   SELECT * FROM materials;
   SELECT * FROM products;
   SELECT * FROM product_components;
   ```

## Troubleshooting

### Database Connection Error: "could not translate host name 'db'"

This means you're trying to run tests/seed locally but the database URL is configured for Docker.

**Solution:**
- Use the helper scripts: `./scripts/run-tests-locally.sh` or `./scripts/run-seed-locally.sh`
- Or set the environment variable: `export TEST_LOCAL=true`

### Port 5432 Already in Use

If you have PostgreSQL already running locally:
- Either stop your local PostgreSQL
- Or modify `docker-compose.dev.yml` to use a different port (e.g., `5433:5432`)

### Permission Errors

If you get permission errors running the scripts:
```bash
chmod +x ./scripts/run-tests-locally.sh
chmod +x ./scripts/run-seed-locally.sh
```

## Authentication Note

All product and material API endpoints require authentication. To test the API:

1. Create a user (or use the seeded manager account)
2. Get a Firebase token
3. Include the token in the Authorization header:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost/api/products
   ```

See `docs/AUTHENTICATION_README.md` for more details on authentication.
