# DF-021 portfolio demo

## Problem and architecture

The demo shows the existing DocumentFlow API accepting a digital PDF, selecting native text extraction through PyMuPDF, recording the result, serving history and summary endpoints, and persisting the successful processing row in PostgreSQL. It uses the existing FastAPI, service/repository, and Docker Compose stack; it adds no runtime feature.

## Reproduce

From the repository root, use the project's existing Python environment and Docker Compose installation:

```powershell
.\.venv\Scripts\python.exe tools\df021_portfolio_demo.py
```

The runner generates a synthetic one-page PDF, uses a unique Compose project and database, waits for services, performs HTTP checks, verifies the database row, saves the extracted TXT and a run report, and normally removes only that run's Compose resources. Its normal cleanup uses `down --rmi local --volumes --remove-orphans` for its unique project, so it removes that run's named volume too. To deliberately retain a run for a separate operator-led visual capture, pass `--keep-stack`; then inspect the exact reported project after capture. For manual cleanup, preserve volumes by default and remove only the exact project resources:

```powershell
docker compose --progress=plain -p <exact-project-name> -f compose.yaml ps -a
docker compose --progress=plain -p <exact-project-name> -f compose.yaml down --rmi local --remove-orphans
```

Do not use a generic Compose cleanup command. Add `--volumes` only when removal of that project's database volume is explicitly intended and its data is no longer needed.

Provide an existing empty artifact directory with `--artifact-dir <path>` when a different output location is required. Review local artifact handling before sharing; reports contain local paths, ports, and a processing UUID.

## Recorded result

The evidence below is from run `b34a99c8` on 2026-11-06, not a rerun in this closeout. The recorded report is `passed`: Compose build and startup returned exit code 0; API root returned HTTP 200 and reported 0.11.0; synthetic PDF upload returned 201; automatic processing returned 200; UUID retrieval, history, and summary returned 200. The result used PyMuPDF for one page and 119 characters, and the expected text matched. PostgreSQL contained the corresponding row with status `sucesso` and mechanism `pymupdf`. This is historical demonstration evidence; it does not establish current service state.

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

This proves a happy-path digital PDF through the recorded local Compose run. It does not prove OCR on scanned documents or images, authentication, production hardening, external release availability, or a current rerun. The demo data is synthetic. The historical `run-report.json` records Compose project `df021-demo-19040-b34a99c8` as retained for visual capture. The later operational cleanup verification confirmed that its API and PostgreSQL containers and its dedicated network were removed. The named volume `df021-demo-19040-b34a99c8_documentflow_pgdata` was intentionally preserved. The demonstration was not rerun during that cleanup verification.

The historical `closeout.json` still records cleanup as blocked/unverified because that was the result at the time it was written; it is preserved unchanged. Do not treat that historical field as the later operational result. The current cleanup result above comes from the subsequent operator inspection.

To independently inspect the exact project if needed, run from the repository root:

```powershell
docker compose --progress=plain -p df021-demo-19040-b34a99c8 -f compose.yaml ps -a
```

If project resources are present and removal is intended, the volume-preserving command is:

```powershell
docker compose --progress=plain -p df021-demo-19040-b34a99c8 -f compose.yaml down --rmi local --remove-orphans
```

The named volume is preserved by that command. Add `--volumes` only after confirming the exact project and explicitly deciding that its PostgreSQL data can be deleted. The later operator cleanup was already completed; these commands are instructions for a future reproduction or inspection. Neither the demo nor its tests were rerun during this closeout.
