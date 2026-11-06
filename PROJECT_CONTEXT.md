# DocumentFlow Project Context

## Identity
- Project: DocumentFlow Automation
- Directory: `C:\Projetos\automacao_documentos`
- Release candidate: v0.11.0 (prepared locally; not published)

## Current State (DF-017 merge preparation)
- Branch: `main`, local HEAD `92b2ae92168b9718161dcbdef1937e47995281c1`; fetched `origin/main` is `0b4e2a5dad39cc808c4cfd6472977bf244fd862d`.
- The histories share ancestor `dd89127bd555c446762a3b3a8116bef68c0b9fb1`. Local `main` retains DF-011 and DF-015; remote `main` has one separate README commit.
- A no-commit merge is prepared with the README conflict resolved. `README.md` and `PROJECT_CONTEXT.md` are staged; the authorized merge commit is not yet created.
- `df011-host-report.txt` and `automacao_documentos.code-workspace` remain local, untracked, and excluded from the merge.
- Architecture: FastAPI, service/repository layers, SQLAlchemy Core, SQLite default, PostgreSQL via `DATABASE_URL`, JSON processing records.
- Current persistence repository: `app/repositories/processamento_repository.py`; database setup: `app/database.py`.
- OCR executable selection uses `TESSERACT_CMD`, then `PATH`, then the legacy Windows path.
- `requirements.txt` is UTF-8 and contains SQLAlchemy 2.1.8 and Psycopg 3.3.8.

## Environment Evidence
- Executor identity is `DARTH-VADER/CodexSandboxOffline` (Windows access-denied diagnostic), distinct from the HOST user reported in the prior mission.
- `.venv/Scripts/python.exe` is a Windows Python launcher with product version 3.14.6; invoking pytest attempted to access `C:\Users\Usuario\AppData\Local\Python\pythoncore-3.14-64\python.exe` and was denied.
- `py -0p` reports no installed Python interpreters in this executor.
- `docker` is absent from PATH and the usual Docker Desktop executable paths checked are absent. This does not establish Docker is absent on HOST.
- Global Codex config observed at `C:\Users\Usuario\.codex\config.toml`: `sandbox_mode = "workspace-write"`, network disabled, and writable roots do not include these project repositories. Do not modify global configuration as part of project work.

## Historical Reports (not current verification)
- A previous DF-011 mission reported 19 passing tests, PostgreSQL 17 in Docker, and SQLAlchemy/Psycopg installed. Those results were not reproducible in the current executor and are not treated as current VERIFIED evidence.

## Active Slice
- DF-018: complete the authorized local merge checkpoint, preserving the remote English portfolio highlights and v0.11.0 documentation. The merge commit is not yet created.

## Blockers
- The DF-018 merge commit is authorized locally; push, tag, release, and deploy remain unauthorized.
- No product or validation blocker was found in the documentation-only reconciliation. Push, tag, release, and deploy remain unauthorized.
- RDS governance repository and Raul Studio are readable but outside the writable root for this session; their state was inspected read-only.

## Evidence and Next Action
- The remote branch was fetched read-only. Both candidate histories and the common ancestor are recorded in DF-017 below.
- DF-013 HOST results remain historical evidence for the same v0.11.0 code; DF-017 did not change implementation or tests.
- Next: complete the pre-commit gates and verify the local merge commit. No commit, push, tag, PR, deploy, or release has been performed.

## Finding HOST-001 (2026-11-05)
- Symptom: HOST runner failed during parameter binding because `Split-Path` received an empty path.
- Root cause: parameter defaults evaluated `Split-Path -Parent $PSScriptRoot` before the script body established its path context. `ReportPath` used the same fragile initialization.
- Fix: resolve `$PSCommandPath` (with `$MyInvocation.MyCommand.Path` fallback) after `param`, then take the parent of the script's `tools` directory; validate the project directory and `app\main.py`. Explicit `-ProjectPath` and `-ReportPath` remain supported.
- Additional bootstrap guard: missing `DATABASE_URL` now fails the runner rather than logging pending integration and continuing. Docker discovery includes a per-user install path.
- Verification: PowerShell parser passed; default and explicit project paths both resolved to this checkout before the Python probe. An explicit nonexistent project path was rejected. Full HOST checks remain pending because the Python launcher is denied in this executor.

## Finding HOST-002 (2026-11-06)
- Audit found the SQLite test fixture did not clear inherited `DATABASE_URL`; it now removes that variable for each test while keeping temporary SQLite path injection.
- Audit found the PostgreSQL test used a fixed row ID and unconditional cleanup; it now requires `DF011_TEST_DATABASE_URL`, validates a loopback PostgreSQL URL and test-named database, uses a generated UUID, and deletes only after successful insertion.
- Runner now clears PostgreSQL environment for SQLite regression, starts a unique Compose project with free host ports and a unique `*_test` database, passes that explicit URL to the integration test, classifies skips separately from passes, and fails if PostgreSQL is skipped.
- Runner restores the original process environment and working directory in `finally`; cleanup uses `down --volumes` only for its unique Compose project. Docker discovery checks PATH and per-user locations.
- Static verification on 2026-11-06: Windows PowerShell parser passed, all nine audit assertions passed, and `git diff --check` passed. Pytest/Docker/PostgreSQL were not run in this executor; HOST validation remains pending.

## Finding HOST-003 (2026-11-06)
- Evidence: `df011-host-report.txt` records Python 3.14.6, Docker Engine 29.9.2, and SQLite `19 passed, 1 warning`; the Docker build section contains only `Image ... Building` followed by failure. It records no Docker build exit code or complete stdout/stderr.
- Proven diagnostic root cause: the runner previously piped the native Compose build through `2>&1` while `$ErrorActionPreference = 'Stop'`, and the catch/report path could run before `$LASTEXITCODE` was recorded. The report cannot establish whether the Docker process itself exited successfully or failed.
- Hypothesis: the Compose progress line arrived on stderr and PowerShell treated it as a terminating native-command error. The old report does not preserve stream identity, so that part and the real Docker exit code remain unproven.
- Patch: Docker process capture now redirects stdout and stderr to separate temporary logs, waits for the process, records both complete streams plus the exit code and failed stage, and uses plain build progress. Temporary logs created by the runner are removed in `finally`. Dockerfile was not changed because no build diagnostic demonstrates a Dockerfile defect.
- Validation: PowerShell parser passed; six static assertions passed; `git diff --check` passed. No Docker build was run in this executor, so HOST validation remains pending.

## DF-011 Final Acceptance Audit (2026-11-06)
- Latest `df011-host-report.txt` reports SQLite 19 passed/1 warning, PostgreSQL 1 passed, Docker Engine 29.9.2, Docker build exit code 0, API and PostgreSQL healthy, root/history HTTP 200, and isolated Compose cleanup. Build steps were served from cache.
- Audit gap: the report's container HTTP smoke only performed GETs. The PostgreSQL test inserted through the repository and read through TestClient, but no real POST reached the containerized API. The runner now posts a unique missing-file webhook request (expected 404), verifies the created error event in `GET /processamentos`, and retrieves it through `GET /processamentos/{UUID}`.
- Reproducibility: the successful build had cached all Dockerfile steps, including package installation. The runner now uses `--pull --no-cache` so the next acceptance run exercises the full build path.
- The successful log also reported that `--progress` is a global Compose option. The runner now passes `--progress=plain` before the `build` subcommand.
- Cleanup: prior report showed container/volume/network cleanup but not image removal. The runner now removes the local image scoped to its unique Compose project.
- Documentation now describes SQLite/PostgreSQL selection and Compose; API version stays `0.10.0` through this review checkpoint. Recommendation is to publish `0.11.0` only with a formal release.
- Static checks and HOST execution after those runner changes are complete; see the final validation addendum below.
- Secret review found no tracked `.env`, credential, key, or token files/patterns. Compose contains only a local-development PostgreSQL credential, with its ports bound to loopback; it is not a production secret.
- Proposed checkpoint boundary after the final HOST pass: `.dockerignore`, `AGENTS.md`, `CHANGELOG.md`, `Dockerfile`, `PROJECT_CONTEXT.md`, `README.md`, `app/database.py`, `app/repositories/processamento_repository.py`, `app/services/extrator_ocr.py`, `compose.yaml`, `requirements.txt`, `tests/conftest.py`, `tests/test_postgres_integration.py`, `tools/df011_host_verify.ps1`, and the regenerated `df011-host-report.txt`.
- Exclude the pre-existing untracked `automacao_documentos.code-workspace`. The regenerated report records the final HTTP POST→GET and uncached-build evidence.

## Finding HOST-001 (2026-11-05)
- Symptom: HOST runner failed during parameter binding because `Split-Path` received an empty path.
- Root cause: parameter defaults evaluated `Split-Path -Parent $PSScriptRoot` before the script body established its path context; `ReportPath` had the same fragile default.
- Fix: resolve the script file and project directory after `param`, validate the project directory and DocumentFlow marker, and retain explicit `-ProjectPath`/`-ReportPath` values.
- Additional bootstrap guard: missing `DATABASE_URL` now fails the runner instead of logging a pending PostgreSQL check and continuing; Docker discovery includes a per-user install path.
- Verification status: static checks are pending in this executor; full runner remains HOST PENDING until Python, PostgreSQL, and Docker stages complete.

## Finding HOST-004 (2026-11-06)
- HOST rerun reached the runner and confirmed Python 3.14.6 plus SQLite `19 passed, 1 warning`.
- Docker discovery failed because its installed-by-user executable path was not among the candidates. The previous successful HOST report gives `%LOCALAPPDATA%\Programs\DockerDesktop\resources\bin\docker.exe`.
- Fix: added that exact path and set the failure stage to `Docker CLI discovery` before probing.
- Validation: initially pending after this patch; completed in the final validation below.

## Finding HOST-005 (2026-11-06)
- Evidence: the next cold build exited `1` before loading base image metadata because Docker could not find `docker-credential-desktop`; the helper executable exists beside the per-user Docker CLI under `%LOCALAPPDATA%\Programs\DockerDesktop\resources\bin`.
- Root cause: runner discovery invoked Docker by full path but did not expose its sibling credential helper to the child process `PATH`.
- Patch: prepend the CLI directory to process `PATH` for this runner invocation, record helper presence, and restore the original `PATH` in the existing environment-restoration path. No Docker global configuration or API code changed.
- Validation: the complete runner passed after the patch: Python 3.14.6; SQLite 19 passed/1 warning; Docker Engine 29.9.2; clean `--pull --no-cache` image build exit 0; PostgreSQL 1 passed/1 warning; Compose services healthy; HTTP root 200; container POST expected 404 followed by record recovery through history and UUID GET; isolated containers, network, volume, and image removed. Report: `df011-host-report.txt`.

## DF-011 Final Validation (2026-11-06)
- PowerShell parser and `git diff --check` passed. The only Git output was the existing LF-to-CRLF notice for `app/database.py` and `app/repositories/processamento_repository.py`.
- HOST acceptance passed end-to-end. The runner report includes separate build stdout/stderr, actual exit code, unique Compose project/database, PostgreSQL integration, HTTP write/read recovery, and successful scoped cleanup.
- No commit or push was performed. `automacao_documentos.code-workspace` remains excluded as pre-existing untracked work.
- Checkpoint recommendation: READY FOR CHECKPOINT. Proposed files: `.dockerignore`, `AGENTS.md`, `CHANGELOG.md`, `Dockerfile`, `PROJECT_CONTEXT.md`, `README.md`, `app/database.py`, `app/repositories/processamento_repository.py`, `app/services/extrator_ocr.py`, `compose.yaml`, `requirements.txt`, `tests/conftest.py`, `tests/test_postgres_integration.py`, `tools/df011_host_verify.ps1`, and `df011-host-report.txt`.

## DF-013 Release Preparation
- Version is set to `0.11.0` in FastAPI metadata, root response, and its API test. `0.10.0` remains only as documented history.
- README now owns product, clone setup, runtime, test, privacy, and persistence guidance. CHANGELOG contains concise version entries; `v0.11.0` is explicitly marked prepared and unpublished.
- Compose credentials are identified as development-only. Documentation states that PostgreSQL is persisted by the named volume while API container files in `input/`, `output/`, and `registros/` are ephemeral when the API container is recreated.
- Validation on this candidate: SQLite regression `19 passed, 1 warning`; API root and OpenAPI both reported `0.11.0`; PowerShell runner parse passed; `git diff --check` passed; the five-file allowlist matched and the index was empty.
- Full HOST runner passed with Python 3.14.6, Docker Engine 29.9.2, Docker build `--pull --no-cache` exit 0, PostgreSQL `1 passed, 1 warning`, healthy Compose services, HTTP root `200` with version `0.11.0`, expected webhook `404`, successful record recovery through history and UUID GET, and isolated cleanup.
- Current HOST evidence is in `%TEMP%\df013-host-report-808c5b2cd004453fa59584cba5266aed.txt`; the DF-011 report remains untouched and outside Git.
- Current changed-file boundary: `README.md`, `CHANGELOG.md`, `app/main.py`, `tests/test_api.py`, and `PROJECT_CONTEXT.md`. `df011-host-report.txt` and `automacao_documentos.code-workspace` remain untracked and excluded.
- Recommendation: READY FOR RELEASE CHECKPOINT. No commit, tag, push, PR, deploy, or release was performed. Await human approval for the local preparation commit; publishing v0.11.0 remains a separate authorized mission.

## DF-014 Documentation Integrity Audit
- Compared both 539-line baseline documents from `HEAD` with the DF-013 candidates; baseline README and CHANGELOG were identical. The README now retains product, installation, local/Compose operation, technical architecture and records, HTTP routes/statuses, webhook and summary examples, test coverage, N8N link, privacy, and known persistence/feature limitations without duplicating the detailed N8N guide.
- CHANGELOG is a concise release history with `v0.11.0` marked prepared/unpublished, plus documented `v0.10.0` and `v0.9` entries. Removed duplicate README material rather than deleting distinct release history; baseline had no separate per-version changelog.
- `requirements-dev.txt` exists and includes `-r requirements.txt` plus pinned pytest. A fresh temporary Python 3.14 venv installed it successfully and `pip check` reported no broken requirements; the temporary venv was removed.
- Candidate HOST evidence remains the DF-013 report in `%TEMP%`; no full runner was repeated because this audit changed documentation only. Static `git diff --check` passed.
- No implementation code or test assertion changed in DF-014. `README.md`, `CHANGELOG.md`, `app/main.py`, `tests/test_api.py`, and `PROJECT_CONTEXT.md` remain the only modified tracked files; the local HOST report and workspace file remain untracked and excluded.
- Recommendation: READY FOR LOCAL CHECKPOINT. No commit, push, tag, release, or deploy was performed; local commit authorization remains pending.

## DF-017 GitHub Divergence Reconciliation
- Read-only fetch updated `origin/main` from `dd89127` to `0b4e2a5`. The remote commit is a sibling of local DF-011/DF-015 commits; common ancestor is `dd89127`.
- The remote commit changes only `README.md`, adding English product copy and engineering highlights. The README preserves that content while correcting the stale v0.10.0 and SQLite-only statements for the v0.11.0 candidate.
- A duplicate endpoint-table header discovered during conflict resolution was removed. No functional files changed.
- No-commit merge parents proposed: first parent local `92b2ae92168b9718161dcbdef1937e47995281c1`, second parent remote `0b4e2a5dad39cc808c4cfd6472977bf244fd862d`.
- The merge remains in progress for human review. Staged merge content is limited to `README.md` and this `PROJECT_CONTEXT.md` update. Diff checks pass; no HOST runner was repeated.
- The two excluded local files are unchanged and untracked. No commit, push, tag, release, or deploy was performed.
