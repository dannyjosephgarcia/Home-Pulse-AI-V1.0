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
- **appliances**: Appliance records linked to properties via `property_id`
- **structures**: Structure records linked to properties via `property_id`
- **appliance_information**: Reference table for appliance pricing data
- **tenants**: Tenant information linked to properties via `property_id`
- **property_images**: S3 image keys linked to properties

All SQL statements are centralized in `backend/db/model/query/sql_statements.py` for maintainability.

## Testing

- Tests are in `backend/tests/`
- Coverage reports generated in `.coverage-reports/coverage.xml`
- Use `tox.ini` for test configuration
- `PYTHONPATH` is set to root directory for imports

## API Structure

The API follows RESTful conventions with versioned endpoints under `/v1/`:

- Customer/Auth: `/v1/customers/*`
- Properties: `/v1/properties/*`
- Payments: Stripe webhooks and session creation
- Appliances: Price analysis and updates
- Home Bot: AI chatbot endpoints

Authentication uses JWT tokens stored in localStorage on the frontend. Token validation happens in the `CustomerAuthenticationService`.

## Key Integration Points

- **AWS S3**: Property image storage via `S3Client`
- **AWS Sagemaker**: LLM inference via `SagemakerClient`
- **Stripe**: Subscription payments with webhook handlers
- **Lowes**: Appliance price scraping via Playwright
- **MySQL**: Database connection pooling via `HpAIDbConnectionPool`
- **FAISS**: Vector similarity search for HomeBot RAG system

## Notes for Development

- The frontend API base URL is currently set to `http://localhost:5000` in `frontend/src/lib/api.ts` (line 3). Switch to production URL when deploying.
- CSRF protection is enabled via `flask-wtf` but exempted for the healthcheck endpoint.
- The application uses Waitress server for local development and native Flask for production (see `app.py`).
- Dependency injection wiring must be updated in `app.py` when adding new route modules.

## Claude Code Agents

Three custom agents are configured to maintain code quality and automated test coverage:

### ethan-hunt-backend-coder (`.claude/agents/ethan-hunt-backend-coder.md`)
Use this agent when creating or updating backend service code that interacts with the database:
- Implements CRUD operations connecting models to database tables (properties, appliances, structures, appliance_information)
- Maintains consistency with schema definitions in `backend/db/model/query/sql_statements.py`
- Updates service layer logic in `backend/db/service/`
- Follows existing naming conventions and logging patterns
- **DO NOT** modify test files with this agent
- Automatically triggers `jason-bourne-backend-test-updater` via PostAgentRun hook when complete

### jason-bourne-backend-test-updater (`.claude/agents/jason-bourne-backend-test-updater.md`)
Automatically triggers after backend code changes via PostFileSave or PostAgentRun hooks:
- Updates unit tests in `backend/tests/` to align with backend code changes
- Adjusts test assertions when database schema or models change
- Creates integration tests for new API endpoints
- Adds newly created test files to git
- Triggered by: (1) PostFileSave hook when any `backend/**/*.py` file is saved, or (2) PostAgentRun hook after `ethan-hunt-backend-coder` completes

### james-bond-frontend-coder (`.claude/agents/james-bond-frontend-coder.md`)
Use this agent when creating or updating React frontend code:
- Creates and updates React components, hooks, and utilities under `frontend/`
- Ensures API calls align with backend endpoints defined in `frontend/src/lib/api.ts`
- Maintains consistent naming conventions, file structure, and styling patterns
- **DO NOT** modify backend code or test files with this agent
