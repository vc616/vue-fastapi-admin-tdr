# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

vue-fastapi-admin is a FastAPI + Vue3 admin panel with RBAC permissions, dynamic routing, and JWT authentication. Default credentials: admin / 123456.

## Backend Commands

```sh
# Install dependencies (uv recommended)
uv add pyproject.toml

# Run development server
make run        # or: python run.py

# Lint and format
make check      # black, isort, ruff
make format     # auto-fix formatting

# Database migrations (aerich)
make migrate    # generate migrations
make upgrade    # apply migrations
make clean-db   # remove migrations and db.sqlite3

# Run tests
make test
```

API docs available at http://localhost:9999/docs

## Frontend Commands (web/ directory)

```sh
cd web
pnpm install
pnpm dev      # development server
pnpm build    # production build
pnpm lint     # eslint
pnpm lint:fix # auto-fix
```

## Architecture

### Backend (app/)

- `app/api/v1/` — API route handlers (users, roles, menus, apis, depts, auditlog)
- `app/controllers/` — Business logic layer between API routes and models
- `app/models/` — Tortoise ORM models (User, Role, Menu, Api, Dept, AuditLog)
- `app/schemas/` — Pydantic schemas for request/response validation
- `app/core/` — Core modules: dependency.py (auth), crud.py, middlewares.py, exceptions.py
- `app/settings/config.py` — Configuration via pydantic-settings

### Frontend (web/src/)

- `web/src/views/system/` — Admin pages (user, role, menu, api, dept management)
- `web/src/store/modules/` — Pinia stores (user, permission, app, tags)
- `web/src/router/guard/` — Route guards for auth and permissions
- `web/src/components/table/` — CrudTable, CrudModal for list/detail patterns
- `web/src/composables/useCRUD.js` — CRUD composition utility

## Key Patterns

### API Authorization
`DependAuth` (auth) and `DependPermission` (RBAC) are injected via FastAPI Depends in route handlers. Non-superusers are checked against role-api permissions.

### Database
Tortoise ORM with aerich for migrations. Default: SQLite (db.sqlite3). MySQL/PostgreSQL configs commented in settings.

### Audit Logging
`HttpAuditLogMiddleware` logs all requests except `/api/v1/base/access_token` and docs endpoints.

### Initial Data
On first startup, `init_app.py` creates: superuser (admin/123456), default menus, API list (scraped from FastAPI routes), and default roles (管理员 with all permissions, 普通用户 with basic GET APIs).