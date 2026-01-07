# Secure HIS — Secure Hospital Information System (Reference Implementation)

Secure HIS is a compact, opinionated reference implementation of a Hospital Information System (HIS) built with FastAPI. It demonstrates practical, security-focused patterns and best practices useful for learning or as a starter template, including secure authentication, password reset flows, audit logging, and role-based access control. This project is intended for demonstration and development purposes — it is not a production-ready clinical system.

**Key features:**
- Authentication with JWT-based sessions and secure password hashing
- Password reset with hashed, single-use tokens
- Role-Based Access Control (RBAC) and admin endpoints
- Audit logging for security-sensitive events
- Tests and pre-commit secret scanning included
- Alembic migrations and DB seed scripts for easy setup

## Quick links
- API: `app/main.py`
- Models: `app/models/`
- CRUD helpers: `app/crud/`
- Tests: `tests/`
- Streamlit UI: `app.py`
- DB: PostgreSQL (Supabase by default)
- Docs: `docs/REFERENCE.md`

---

## Quick commands
- Install: `python -m pip install -r requirements.txt`
- Dev tools: `python -m pip install -r requirements-dev.txt`
- Run API (dev): `uvicorn app.main:app --reload`
- Run UI: `streamlit run app.py`
- Run tests: `python -m pytest -q`
- Seed data: `python seed_users.py` / `python seed_patients.py`
- Admin reset CLI: `python scripts/admin_reset_user.py --username <user> --password <temp>`

## Getting started
Follow these minimal steps to run the project locally:

1. Copy and configure environment variables:
   - `cp .env.example .env` and edit `.env` (do **not** commit `.env`).
2. Install dependencies:
   - `python -m pip install -r requirements.txt`
   - (optional) `python -m pip install -r requirements-dev.txt` for development tools and tests
3. Prepare the database:
   - Use a local PostgreSQL instance or Supabase; run Alembic migrations: `alembic upgrade head`
   - For quick development only: the app may call `Base.metadata.create_all()` when enabled
4. Seed example data (optional):
   - `python seed_users.py` and `python seed_patients.py`
5. Run the API (development):
   - `uvicorn app.main:app --reload`
6. Run the Streamlit UI (optional):
   - `streamlit run app.py`
7. Run tests:
   - `python -m pytest -q`

> Tip: For tests and CI you can set `SKIP_DB_CREATE=true` to skip automatic `create_all` during import.

---

## Environment
- Copy `.env.example` -> `.env` and fill real values. **Do not commit `.env`**.
- `.env.example` contains the minimal set of env vars required.
- Pre-commit secret scanning is included and runs locally via `.pre-commit-config.yaml` and `scripts/check_secrets.py`.

---

## Architecture & Design
- FastAPI-based back-end with role-based access control (router modules under `app/api/`).
- SQLAlchemy ORM models in `app/models/`; `Base.metadata.create_all()` used for dev convenience.
- `user_flags` table holds per-user flags (e.g., `must_change_password`) to avoid altering an externally-managed `users` table.
- Password reset tokens are stored hashed and single-use (`password_reset_tokens` table).
- Audit logs capture key events and are stored in `audit_logs`.

---

## Important files (quick reference)
- `app/main.py`: app entry, router registration, optional `Base.metadata.create_all`
- `app/database.py`: engine, `SessionLocal`, `Base`
- `app/core/security.py`: password hashing and JWT helpers
- `app/api/auth.py`: login, register, forgot/reset password
- `app/api/admin.py`: admin-only endpoints (roles, audit logs, admin reset)
- `app/crud/`: helpers for data access (user, audit, password_reset, user_flags)
- `app/models/`: DB tables (`user`, `audit`, `patient`, `password_reset`, `user_flags`)
- `tests/`: test coverage for audit login and password reset flows

---

## Database & Migrations
- Recommended: use Alembic for migrations (there is an `alembic/` folder and migration to create `user_flags` and `password_reset_tokens`).
- For local tests we use `SKIP_DB_CREATE=true` to skip `create_all` during import if needed.

---

## Security Notes
- Store production secrets in a secrets manager; use strong `SECRET_KEY`.
- Implement email delivery for password resets and never log raw tokens in production.

---

## Contributing & Dev Setup
- Copy and set `.env`: `cp .env.example .env` and fill values.
- Install dev tools: `pip install -r requirements-dev.txt`
- Install pre-commit: `pre-commit install` and run `pre-commit run --all-files`.

---
