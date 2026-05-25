# AGENTS.md

## Project

FastAPI + Vue3 + Naive UI admin panel. RBAC permissions, dynamic routing, JWT auth. Default admin / 123456.

## Backend

```sh
uv add pyproject.toml        # install deps
make run                     # uvicorn app:app on 0.0.0.0:9999 (reload)
make check                   # black --check + isort --check + ruff check ./app
make format                  # black ./ + isort ./ --profile black
make migrate                 # aerich migrate
make upgrade                 # aerich upgrade
make clean-db                # rm -rf migrations/ db.sqlite3*
make test                    # pytest -vv -s --cache-clear ./ (reads .env, may fail without it)
python run.py                # alternative: uvicorn app:app --reload port 9999
```

API docs: `http://localhost:9999/docs`

**Architecture**: `app/api/v1/` (routers) → `app/controllers/` (business logic, extends `CRUDBase[Model,Create,Update]`) → `app/models/` (Tortoise ORM). `app/core/dependency.py`: `DependAuth` (JWT) and `DependPermission` (RBAC) injected via FastAPI Depends. `token: "dev"` skips JWT validation (first user).

**DB**: Tortoise ORM + aerich. Default SQLite (`db.sqlite3`). First startup auto-migrates and seeds (superuser, menus, API list, roles) via `app/__init__.py` lifespan.

**Line length**: 120 (black/ruff config in pyproject.toml). `ruff check ./app` only (not root). No type checker configured.

## Frontend (`web/`)

```sh
pnpm install
pnpm dev                    # vite on port 3100, proxy /api/v1 -> http://127.0.0.1:9999
pnpm build
pnpm lint                   # eslint --ext .js,.vue .
pnpm lint:fix
```

Stack: Vue 3 (Options API), Vite 4, Pinia, Naive UI, UnoCSS, Axios. **No TypeScript** (plain `.js`). ESLint config extends `@zclzone` + `@unocss`.

**Key files**: `web/src/composables/useCRUD.js` (CRUD pattern for list/detail), `web/src/utils/http/` (Axios wrapper), `web/src/store/modules/` (Pinia stores user/permission/app/tags).

## Notes

- `.gitignore` excludes `migrations/` and `db.sqlite3*` (generated).
- `make clean-db` uses `find` (Unix only; fails on Windows).
- No test suite exists beyond `test_mysql.py` (utility script, not a real test).
- `test_mysql.py` has hardcoded credentials — do not commit changes to it.
- `make test` requires `.env` file; the repo does not ship one.
