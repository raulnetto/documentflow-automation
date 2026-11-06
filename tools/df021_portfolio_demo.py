#!/usr/bin/env python3
"""Run a synthetic, isolated DocumentFlow PostgreSQL portfolio demo."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "artifacts" / "df021-portfolio-demo"
EXPECTED = (
    "DOCUMENTFLOW DF021 PORTFOLIO DEMO",
    "Synthetic digital PDF extraction proves the PyMuPDF route.",
    "Reference: DF021-SAFE-2026",
)


def pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def create_pdf(path: Path) -> None:
    commands = [
        "BT",
        "/F1 18 Tf",
        "72 720 Td",
        f"({pdf_escape(EXPECTED[0])}) Tj",
        "/F1 12 Tf",
        "0 -34 Td",
        f"({pdf_escape(EXPECTED[1])}) Tj",
        "0 -26 Td",
        f"({pdf_escape(EXPECTED[2])}) Tj",
        "ET",
    ]
    stream = ("\n".join(commands) + "\n").encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
        + stream
        + b"endstream",
    ]
    data = bytearray(b"%PDF-1.4\n%DF021\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(data))
        data.extend(f"{index} 0 obj\n".encode("ascii"))
        data.extend(body)
        data.extend(b"\nendobj\n")
    xref_offset = len(data)
    data.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    data.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    data.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    path.write_bytes(data)


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        return int(server.getsockname()[1])


def find_docker() -> str:
    candidates = [os.environ.get("DOCKER", ""), shutil.which("docker") or ""]
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        candidates.extend(
            str(Path(local_app_data) / suffix / "docker.exe")
            for suffix in (
                "Programs/DockerDesktop/resources/bin",
                "Programs/Docker/Docker/resources/bin",
                "Docker/Docker/resources/bin",
            )
        )
    program_files = os.environ.get("ProgramFiles", "")
    if program_files:
        candidates.append(str(Path(program_files) / "Docker/Docker/resources/bin/docker.exe"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("Docker CLI was not found on PATH or in known HOST locations.")


def request_json(url: str, *, method: str = "GET", data: bytes | None = None,
                 headers: dict[str, str] | None = None) -> tuple[int, object]:
    request = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read()
            return response.status, json.loads(body) if body else None
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code} for {method} {url}: {body[:500]}") from error


def multipart_upload(pdf_path: Path, filename: str) -> tuple[bytes, str]:
    boundary = "----DF021" + uuid.uuid4().hex
    content = pdf_path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="arquivo"; filename="{filename}"\r\n'
        "Content-Type: application/pdf\r\n\r\n"
    ).encode("ascii") + content + f"\r\n--{boundary}--\r\n".encode("ascii")
    return body, f"multipart/form-data; boundary={boundary}"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep-stack", action="store_true", help="leave only this run's Compose project up for visual capture")
    parser.add_argument("--artifact-dir", type=Path, help="existing, empty directory for this run's artifacts")
    args = parser.parse_args()

    run_uuid = uuid.uuid4()
    run_id = run_uuid.hex[:8]
    artifact_dir = args.artifact_dir or (ARTIFACT_ROOT / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{run_id}")
    artifact_dir = artifact_dir.resolve()
    if artifact_dir.exists() and any(artifact_dir.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty artifact directory: {artifact_dir}")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    docker = find_docker()
    docker_dir = str(Path(docker).parent)
    compose_project = f"df021-demo-{os.getpid()}-{run_id}"
    database = f"df021demo_{run_id}"
    api_port = free_port()
    pg_port = free_port()
    while pg_port == api_port:
        pg_port = free_port()
    filename = f"documentflow_df021_{run_id}.pdf"
    pdf_path = artifact_dir / filename
    evidence_path = artifact_dir / "http-evidence.json"
    report_path = artifact_dir / "run-report.json"
    docker_log = artifact_dir / "docker-commands.json"
    manifest: dict[str, object] = {
        "run_id": run_id,
        "compose_project": compose_project,
        "database": database,
        "api_url": f"http://127.0.0.1:{api_port}",
        "ports": {"api": api_port, "postgres": pg_port},
        "artifacts": {"pdf": str(pdf_path), "http_evidence": str(evidence_path)},
        "status": "running",
        "commands": [],
    }
    write_json(report_path, manifest)
    command_log: list[dict[str, object]] = []
    started = False
    failure: str | None = None
    cleanup_status = "not-needed"
    env = os.environ.copy()
    env.update(
        {
            "DF011_POSTGRES_DB": database,
            "DF011_API_HOST_PORT": str(api_port),
            "DF011_PG_HOST_PORT": str(pg_port),
            "PATH": docker_dir + os.pathsep + env.get("PATH", ""),
        }
    )
    compose = [docker, "compose", "--progress=plain", "-p", compose_project,
               "-f", str(ROOT / "compose.yaml")]

    def run(label: str, arguments: list[str], *, check: bool = True, timeout: int = 600) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [*compose, *arguments], cwd=ROOT, env=env, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=timeout,
        )
        command_log.append(
            {"label": label, "exit_code": result.returncode,
             "stdout": result.stdout, "stderr": result.stderr}
        )
        write_json(docker_log, command_log)
        if check and result.returncode != 0:
            raise RuntimeError(f"{label} failed with exit code {result.returncode}; see {docker_log}")
        return result

    try:
        create_pdf(pdf_path)
        pdf_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
        manifest["artifacts"]["pdf_sha256"] = pdf_hash  # type: ignore[index]
        write_json(report_path, manifest)

        started = True
        run("build", ["build", "--pull", "api"], timeout=1200)
        run("compose-up", ["up", "-d", "--wait", "--wait-timeout", "180"], timeout=300)

        base_url = str(manifest["api_url"])
        last_error = None
        for _ in range(45):
            try:
                root_status, root = request_json(base_url + "/")
                if root_status == 200 and isinstance(root, dict) and root.get("versao") == "0.11.0":
                    break
            except Exception as error:  # service startup race only
                last_error = str(error)
            time.sleep(2)
        else:
            raise RuntimeError(f"API did not become ready: {last_error or root}")

        upload_body, upload_type = multipart_upload(pdf_path, filename)
        upload_status, upload = request_json(
            base_url + "/documentos/upload", method="POST", data=upload_body,
            headers={"Content-Type": upload_type},
        )
        if upload_status != 201 or not isinstance(upload, dict) or upload.get("status") != "armazenado":
            raise RuntimeError(f"Upload contract failed: HTTP {upload_status} {upload}")

        process_status, processed = request_json(
            base_url + "/documentos/" + urllib.parse.quote(filename, safe="") + "/processar-automaticamente",
            method="POST",
        )
        if process_status != 200 or not isinstance(processed, dict):
            raise RuntimeError(f"Automatic processing failed: HTTP {process_status} {processed}")
        record_id = str(processed.get("id_registro", ""))
        if (processed.get("status") != "processamento_concluido"
                or processed.get("mecanismo") != "pymupdf"
                or processed.get("quantidade_paginas") != 1 or not record_id):
            raise RuntimeError(f"Unexpected processing response: {processed}")

        detail_status, detail = request_json(base_url + "/processamentos/" + record_id)
        history_status, history = request_json(base_url + "/processamentos")
        summary_status, summary = request_json(base_url + "/processamentos/resumo")
        if detail_status != 200 or not isinstance(detail, dict) or detail.get("id") != record_id:
            raise RuntimeError(f"UUID retrieval failed: HTTP {detail_status} {detail}")
        if history_status != 200 or not isinstance(history, list) or not any(item.get("id") == record_id for item in history):
            raise RuntimeError(f"History retrieval failed: HTTP {history_status}")
        if (summary_status != 200 or not isinstance(summary, dict)
                or summary.get("sucessos", 0) < 1
                or summary.get("por_mecanismo", {}).get("pymupdf", 0) < 1):
            raise RuntimeError(f"Summary verification failed: HTTP {summary_status} {summary}")

        evidence = {
            "api_root": {"http_status": root_status, "body": root},
            "upload": {"http_status": upload_status, "body": upload},
            "automatic_processing": {"http_status": process_status, "body": processed},
            "record_by_uuid": {"http_status": detail_status, "body": detail},
            "history": {"http_status": history_status, "contains_demo_record": True,
                        "record_count": len(history)},
            "summary": {"http_status": summary_status, "body": summary},
            "expected_text": list(EXPECTED),
        }
        write_json(evidence_path, evidence)

        copied_text = artifact_dir / str(processed["arquivo_texto"])
        copy_result = run(
            "copy-extracted-text",
            ["cp", f"api:/app/output/{processed['arquivo_texto']}", str(copied_text)],
        )
        if copy_result.returncode != 0 or not copied_text.is_file():
            raise RuntimeError("Could not copy the produced text file from the API container")
        extracted_text = copied_text.read_text(encoding="utf-8")
        missing = [phrase for phrase in EXPECTED if phrase not in extracted_text]
        if missing:
            raise RuntimeError(f"Extracted text did not match synthetic source; missing: {missing}")

        query = f"SELECT id || '|' || status || '|' || mecanismo FROM processamentos WHERE id = '{record_id}';"
        database_result = run(
            "postgresql-row-check",
            ["exec", "-T", "postgres", "psql", "-U", "documentflow", "-d", database,
             "-tA", "-c", query],
        )
        database_row = database_result.stdout.strip()
        if database_row != f"{record_id}|sucesso|pymupdf":
            raise RuntimeError(f"PostgreSQL row did not match expected record: {database_row!r}")
        (artifact_dir / "postgresql-row.txt").write_text(database_row + "\n", encoding="utf-8")

        manifest.update(
            {
                "status": "passed",
                "release": "v0.11.0",
                "pdf": {"filename": filename, "sha256": pdf_hash, "bytes": pdf_path.stat().st_size},
                "upload_http": upload_status,
                "processing_http": process_status,
                "processing_id": record_id,
                "mechanism": processed["mecanismo"],
                "page_count": processed["quantidade_paginas"],
                "extracted_text": copied_text.name,
                "text_matches_expected": True,
                "postgresql_row": database_row,
                "http_evidence": evidence_path.name,
                "database": database,
                "compose_project": compose_project,
                "ports": {"api": api_port, "postgres": pg_port},
                "kept_stack_for_capture": bool(args.keep_stack),
            }
        )
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
        manifest["status"] = "failed"
        manifest["error"] = failure
    finally:
        if started and not args.keep_stack:
            result = run("cleanup", ["down", "--rmi", "local", "--volumes", "--remove-orphans"], check=False, timeout=300)
            cleanup_status = "passed" if result.returncode == 0 else f"failed:{result.returncode}"
            if result.returncode != 0 and not failure:
                failure = "RuntimeError: scoped Compose cleanup failed; see docker-commands.json"
                manifest["status"] = "failed"
                manifest["error"] = failure
        elif started and args.keep_stack:
            cleanup_status = "deferred-for-visual-capture"
        manifest["cleanup"] = cleanup_status
        manifest["commands"] = [{"label": item["label"], "exit_code": item["exit_code"]} for item in command_log]
        write_json(report_path, manifest)

    if failure:
        print(f"DEMO FAILED: {failure}", file=sys.stderr)
        print(f"Evidence directory: {artifact_dir}", file=sys.stderr)
        return 1

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"ARTIFACT_DIR={artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
