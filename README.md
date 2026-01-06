# Secure HIS — Project Reference

A small FastAPI-based Hospital Information System (HIS) focused on Confidentiality, Integrity, and Availability.

## Quick links
- API: `app/main.py`
- Models: `app/models/`
- CRUD helpers: `app/crud/`
- Tests: `tests/`
- Streamlit UI: `app.py`
- DB: PostgreSQL (Supabase by default)

---

## Quick commands
- Install: `python -m pip install -r requirements.txt`
- Dev tools: `python -m pip install -r requirements-dev.txt`
- Run API (dev): `uvicorn app.main:app --reload`
- Run UI: `streamlit run app.py`
- Run tests: `python -m pytest -q`
- Seed data: `python seed_users.py` / `python seed_patients.py`
- Admin reset CLI: `python scripts/admin_reset_user.py --username <user> --password <temp>`

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

If you want I can add more details (diagrams, flowcharts, or API docs) or move this into `docs/REFERENCE.md` instead.