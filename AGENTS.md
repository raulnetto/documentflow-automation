# DocumentFlow Automation — Project Adapter

## Identity
- Project: DocumentFlow Automation
- Repository: `C:\Projetos\automacao_documentos`
- Role: document processing API and workflow integration
- Executor: active RDS Executor, subject to the global RDS constitution

## Sources of truth
- This file is the project entrypoint.
- `README.md` documents current product behavior; inspect relevant code and tests before changes.
- `PROJECT_CONTEXT.md` records factual continuity and environment evidence.
- RDS canonical governance is maintained separately in `C:\Projetos\raul-rds`; do not copy Moonr Studio product policies or implementation into this project.

## Environment adapter
- Project virtual environment: `.venv\Scripts\python.exe` (reported Python 3.14.6; HOST execution must be verified for each run).
- Regression command: `.venv\Scripts\python.exe -m pytest -q`.
- Current database contract: SQLite at `dados/documentflow.db` by default; PostgreSQL is selected with `DATABASE_URL`. JSON records remain part of the existing flow.
- External services: PostgreSQL/Docker only when an explicitly scoped task requires them; never silently substitute SQLite for a PostgreSQL check.
- OCR: Tesseract is an external executable configured by `TESSERACT_CMD`, then `PATH`, then the legacy Windows path; preserve local Windows behavior and verify Linux/container configuration separately.
- HOST-only checks must use one bounded, reproducible runner with isolated data, safe cleanup, logs, and captured evidence. Do not label executor sandbox limitations as project or HOST failures.

## Project invariants and gates
- Preserve existing HTTP routes, response schemas/status codes, JSON persistence, SQLite behavior, and uncommitted work.
- Inspect Git status and relevant source before edits. Do not migrate historical data automatically.
- Use existing repository and service layers; make the smallest coherent change.
- No commit, push, deploy, destructive cleanup, secrets changes, architecture expansion, or unrelated refactor without explicit authorization.
- Report IMPLEMENTED, VERIFIED, BLOCKED, and HUMAN REVIEW PENDING separately. Executed does not mean verified.
