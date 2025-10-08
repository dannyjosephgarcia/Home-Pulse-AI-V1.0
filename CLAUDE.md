# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Home Pulse AI is a property management application that helps track appliances and structures across multiple properties, with AI-powered lifecycle predictions and price analysis. The system consists of a Python Flask backend API and a React TypeScript frontend.

## Architecture

### Backend (Flask + Python)

The backend follows a layered service-oriented architecture with dependency injection:

- **`backend/app/app.py`**: Flask application entry point. Registers all blueprints and wires dependency injection container.
- **`backend/app/container.py`**: Dependency injection container using `dependency-injector`. All services are configured as singletons here.
- **Routes**: Flask blueprints organized by domain (db, payment, data_harvesting, home_bot_model)
- **Services**: Business logic layer, injected via the container
- **Clients**: External integrations (MySQL, S3, Sagemaker, Stripe, Lowes scraping)
- **Models**: Request/response data models
- **`backend/db/model/query/sql_statements.py`**: Centralized SQL query definitions

Key domains:
- **db**: Core database operations for customers, properties, appliances, structures, tenants
- **payment**: Stripe integration for subscriptions
- **data_harvesting**: Lowes price analysis via web scraping
- **home_bot_model**: AI chatbot using RAG (FAISS vector search) and Sagemaker LLM endpoints

### Frontend (React + TypeScript + Vite)

- **`frontend/src/lib/api.ts`**: Centralized API client with JWT token management. All backend requests go through this.
- **Pages**: Main application routes (Login, Dashboard, Properties, PropertyDetail, Profile)
- **Components**: Reusable UI components including HomeBot chatbot
- **UI library**: Radix UI components with Tailwind CSS styling

### Common

Shared utilities used across the backend:
- **`common/decorators`**: Python decorators
- **`common/helpers`**: Utility functions
- **`common/logging`**: Structured logging configuration

## Development Commands

### Backend

Run tests with coverage:
```bash
tox
```

Run specific test file:
```bash
pytest backend/tests/test_file_name.py
```

Run backend locally (requires ENV and PORT environment variables):
```bash
python backend/app/app.py
```

Install backend dependencies:
```bash
pip install -r backend/app/requirements.txt
```

### Frontend

Install dependencies:
```bash
cd frontend && npm install
```

Run development server:
```bash
cd frontend && npm run dev
```

Build for production:
```bash
cd frontend && npm run build
```

Run linter:
```bash
cd frontend && npm run lint
```

Preview production build:
```bash
cd frontend && npm run preview
```

Deploy to gh-pages:
```bash
cd frontend && npm run deploy
```

## Environment Configuration

The backend uses environment-specific YAML configs:
- **`backend/app/config-local.yaml`**: Local development
- **`backend/app/config-prod.yaml`**: Production

Configuration is loaded based on `ENV` environment variable in `container.py`.

## Database Schema

The MySQL database (`home_pulse_ai`) contains the following core tables:
- **users**: Customer accounts with authentication, Stripe integration, and company relationships
- **properties**: Property records linked to users via `user_id`
- **units**: Unit records for multifamily properties, linked via `property_id`
- **appliances**: Appliance records with optional `unit_id` (multifamily) or `property_id` only (single-family)
- **structures**: Structure records linked to properties via `property_id` (always property-level)
- **appliance_information**: Reference table for appliance pricing data
- **tenants**: Tenant information with optional `unit_id` (multifamily) or `property_id` only (single-family)
- **property_images**: S3 image keys linked to properties

All SQL statements are centralized in `backend/db/model/query/sql_statements.py` for maintainability.

### Multifamily vs Single-Family Architecture

Properties are dynamically classified as multifamily or single-family based on the presence of units:

**Multifamily Properties:**
- Have one or more records in the `units` table with non-null `unit_number`
- Appliances are associated with specific units via `unit_id`
- Tenants are associated with specific units via `unit_id`
- Structures remain at property level (no `unit_id`)

**Single-Family Properties:**
- Have NO records in the `units` table
- Appliances have `unit_id = NULL`, associated only with `property_id`
- Tenants have `unit_id = NULL`, associated only with `property_id`
- Structures are at property level

The `isMultifamily` field is computed dynamically in SQL queries using:
```sql
CASE WHEN EXISTS (
    SELECT 1 FROM units u
    WHERE u.property_id = p.id
    AND u.unit_number IS NOT NULL
) THEN 1 ELSE 0 END as is_multifamily
```

This computed field must be included in all property retrieval queries to ensure frontend can properly differentiate property types.

## Testing

- Tests are in `backend/tests/`
- Coverage reports generated in `.coverage-reports/coverage.xml`
- Use `tox.ini` for test configuration
- `PYTHONPATH` is set to root directory for imports

## Schema Documentation

A schema extraction script is available to generate up-to-date database documentation:

```bash
DB_HOST=your-endpoint DB_USER=user DB_PASSWORD=pass DB_NAME=home_pulse_ai python scripts/dump_schema.py
```

This generates:
- `backend/db/schema.md`: Human-readable markdown documentation with tables, columns, types, foreign keys, and indexes
- `backend/db/schema.sql`: SQL CREATE TABLE statements

Run this script whenever the database schema changes to keep documentation in sync. These files provide Claude Code with complete schema context without requiring database credentials.

## API Structure

The API follows RESTful conventions with versioned endpoints under `/v1/`:

- Customer/Auth: `/v1/customers/*`
- Properties: `/v1/properties/*`
  - `GET /v1/properties/{property_id}` - Must return `isMultifamily` field
  - `GET /v1/properties/{property_id}/units` - Returns units for multifamily properties
  - `GET /v1/properties/{property_id}/appliances` - Returns property-level appliances (single-family)
  - `GET /v1/properties/{property_id}/structures` - Returns structures (all property types)
- Units: `/v1/units/*`
  - `GET /v1/units/{unit_id}/appliances` - Returns unit-level appliances (multifamily)
- Payments: Stripe webhooks and session creation
- Appliances: Price analysis and updates
- Home Bot: AI chatbot endpoints

Authentication uses JWT tokens stored in localStorage on the frontend. Token validation happens in the `CustomerAuthenticationService`.

**Frontend-Backend Contract**: The frontend (`PropertyDetail.tsx`) uses the `isMultifamily` field to determine which appliances endpoint to call:
- If `isMultifamily === true`: Fetches units, then unit appliances for each unit
- If `isMultifamily === false`: Fetches property-level appliances directly

## Key Integration Points

- **AWS S3**: Property image storage via `S3Client`
- **AWS Sagemaker**: LLM inference via `SagemakerClient`
- **Stripe**: Subscription payments with webhook handlers
- **Lowes**: Appliance price scraping via Playwright
- **MySQL**: Database connection pooling via `HpAIDbConnectionPool`
- **FAISS**: Vector similarity search for HomeBot RAG system

## Git Workflow

- Branch naming follows pattern `HP-XX` where XX is the issue/task number
- Main branch for PRs: `main`
- Commit messages should be descriptive and reference the issue number

## Notes for Development

- **IMPORTANT**: The frontend API base URL is configured in `frontend/src/lib/api.ts` (line 1). Currently set to production (`https://home-pulse-api.onrender.com`). Comment/uncomment to switch between production and local (`http://localhost:5000`). This is a common source of connection issues during local development.
- CSRF protection is enabled via `flask-wtf` but exempted for the healthcheck endpoint.
- The application uses Waitress server for local development and native Flask for production (see `app.py`).
- Dependency injection wiring must be updated in `app.py` when adding new route modules.
- When adding new property retrieval queries, always include the computed `isMultifamily` field to maintain frontend-backend contract.
- Units table should only contain entries for multifamily properties with valid `unit_number` values.
- Single-family properties should never have records in the `units` table.
- Property-level appliances (single-family) have `unit_id = NULL`; unit-level appliances (multifamily) have `unit_id` set.

## Claude Code Agents

Five custom agents are configured to maintain code quality, automated test coverage, contract consistency, and third-party integrations. Some agents trigger automatically via hooks, while others should be manually invoked:

### ethan-hunt-backend-coder (`.claude/agents/ethan-hunt-backend-coder.md`) [MANUAL]
**When to use**: Creating or updating backend service code that interacts with the database:
- Implements CRUD operations connecting models to database tables (properties, appliances, structures, appliance_information)
- Maintains consistency with schema definitions in `backend/db/model/query/sql_statements.py`
- Updates service layer logic in `backend/db/service/`
- Follows existing naming conventions and logging patterns
- **DO NOT** modify test files with this agent
- Automatically triggers `jason-bourne-backend-test-updater` via PostAgentRun hook when complete

### jason-bourne-backend-test-updater (`.claude/agents/jason-bourne-backend-test-updater.md`) [AUTO]
**When it triggers**: Automatically after backend code changes via PostFileSave or PostAgentRun hooks.
**What it does**:
- Updates unit tests in `backend/tests/` to align with backend code changes
- Adjusts test assertions when database schema or models change
- Creates integration tests for new API endpoints
- Adds newly created test files to git
- Triggered by: (1) PostFileSave hook when any `backend/**/*.py` file is saved, or (2) PostAgentRun hook after `ethan-hunt-backend-coder` completes

### james-bond-frontend-coder (`.claude/agents/james-bond-frontend-coder.md`) [MANUAL]
**When to use**: Creating or updating React frontend code:
- Creates and updates React components, hooks, and utilities under `frontend/`
- Ensures API calls align with backend endpoints defined in `frontend/src/lib/api.ts`
- Maintains consistent naming conventions, file structure, and styling patterns
- **DO NOT** modify backend code or test files with this agent
- Automatically triggers `jack-reacher-contract-enforcer` after modifying files in `frontend/src`

### jack-reacher-contract-enforcer (`.claude/agents/jack-reacher-contract-enforcer.md`) [AUTO]
**When it triggers**: Automatically after `james-bond-frontend-coder` modifies frontend files.
**What it does**:
- Validates API contract consistency between frontend and backend
- Detects breaking changes such as renamed fields, missing attributes, or type mismatches
- Compares frontend API usage against backend definitions
- Generates reports of inconsistencies and delegates fixes to `ethan-hunt-backend-coder` when needed
- Triggered by: PostAgentRun hook after `james-bond-frontend-coder` completes

### jack-ryan-integration-specialist (`.claude/agents/jack-ryan-integration-specialist.md`) [MANUAL]
**When to use**: Research and plan third-party integrations:
- Reads and analyzes documentation for third-party APIs and services
- Creates integration plans with detailed implementation steps
- Identifies required dependencies, authentication patterns, and API endpoints
- Delegates implementation tasks to `ethan-hunt-backend-coder` with clear specifications
- Use when integrating services like payment processors, external APIs, or cloud services
