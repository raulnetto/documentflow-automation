# DF-021 portfolio demo

## Problem and architecture

The demo shows the existing DocumentFlow API accepting a digital PDF, selecting native text extraction through PyMuPDF, recording the result, serving history and summary endpoints, and persisting the successful processing row in PostgreSQL. It uses the existing FastAPI, service/repository, and Docker Compose stack; it adds no runtime feature.

## Reproduce

From the repository root, use the project's existing Python environment and Docker Compose installation:

```powershell
.\.venv\Scripts\python.exe tools\df021_portfolio_demo.py
```

The runner generates a synthetic one-page PDF, uses a unique Compose project and database, waits for services, performs HTTP checks, verifies the database row, saves the extracted TXT and a run report, and normally removes only that run's Compose resources. To deliberately retain a run for a separate operator-led visual capture, pass `--keep-stack`; then inspect and remove only the exact reported project after capture. The previous run used this option and its cleanup is still unverified. Do not use a generic Compose cleanup command.

Provide an existing empty artifact directory with `--artifact-dir <path>` when a different output location is required. Review local artifact handling before sharing; reports contain local paths, ports, and a processing UUID.

## Recorded result

The evidence below is from run `b34a99c8` on 2026-11-06, not a rerun in this closeout. The recorded report is `passed`: Compose build and startup returned exit code 0; API root returned HTTP 200 and reported 0.11.0; synthetic PDF upload returned 201; automatic processing returned 200; UUID retrieval, history, and summary returned 200. The result used PyMuPDF for one page and 119 characters, and the expected text matched. PostgreSQL contained the corresponding row with status `sucesso` and mechanism `pymupdf`.

The published-release status is supplied by the project owner. This session verified the local `v0.11.0` tag and API response but did not independently query a hosting service.

## Evidence paths

Run directory: `artifacts/df021-portfolio-demo/20261106-022422-b34a99c8/`

- `run-report.json` — command exit codes, run ID, project name, and extraction outcome.
- `http-evidence.json` — sanitized root, upload, processing, retrieval, history, and summary results.
- `documentflow_df021_b34a99c8.pdf` — synthetic input, 740 bytes; SHA-256 `3cf625be5560c9bb75ae242e41213bff2d785cd53d004681948da2e1eabc7235`.
- `documentflow_df021_b34a99c8_extraido.txt` — extracted synthetic text.
- `postgresql-row.txt` — verified row ID, status, and mechanism.
- `docker-commands.json` — captured command outcomes.
- `closeout.json` — closeout verification and cleanup limitation.

The linked SVG is a diagram derived from these saved results. It is not a browser screenshot or a UI capture.

## Limits

This proves a happy-path digital PDF through the recorded local Compose run. It does not prove OCR on scanned documents or images, authentication, production hardening, external release availability, or a current rerun. The demo data is synthetic. The report records Compose project `df021-demo-19040-b34a99c8` as retained for visual capture. In this executor the project-scoped Docker CLI could not be accessed, so the service/volume/image cleanup state remains unknown.

After confirming the exact project still exists, an operator can inspect it from the repository root:

```powershell
docker compose --progress=plain -p df021-demo-19040-b34a99c8 -f compose.yaml ps -a
```

Only if the listed resources belong to that exact project, remove them with:

```powershell
docker compose --progress=plain -p df021-demo-19040-b34a99c8 -f compose.yaml down --rmi local --volumes --remove-orphans
```

This closeout did not run either command. No tests or demo were rerun because the saved end-to-end evidence directly covers the requested flow and rerunning would create another temporary stack.
