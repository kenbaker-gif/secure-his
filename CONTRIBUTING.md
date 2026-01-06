Thank you for contributing!

Quick setup steps for local development:

1. Copy the environment example:
   cp .env.example .env
   Fill in the values in `.env` (do NOT commit `.env`).

2. Install dev dependencies and enable the pre-commit hooks:
   pip install -r requirements-dev.txt
   pre-commit install

3. The repo includes a small pre-commit hook that scans staged files for common secret patterns.
   If you see a false positive, either adjust the script `scripts/check_secrets.py` or commit with `--no-verify`.

If you have questions, open an issue or ping the repository owner.