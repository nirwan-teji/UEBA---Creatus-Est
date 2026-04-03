from __future__ import annotations

import asyncio
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from scripts.run_pipeline import (  # noqa: E402
    DEFAULT_ALERT_THRESHOLD,
    DEFAULT_MODEL_PATH,
    DEFAULT_RAW_ROOT,
    DEFAULT_SCHEMA_PATH,
    run_pipeline_workflow,
)

app = FastAPI(title="UEBA Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_PIPELINE_LOCK = asyncio.Lock()

DEFAULT_RAW_DIR = PROJECT_ROOT / DEFAULT_RAW_ROOT
DEFAULT_MODEL_FILE = PROJECT_ROOT / DEFAULT_MODEL_PATH
DEFAULT_SCHEMA_FILE = PROJECT_ROOT / DEFAULT_SCHEMA_PATH
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

METRIC_COLUMNS = [
    "logon_logon_events",
    "logon_logoff_events",
    "logon_total_events",
    "device_connect_events",
    "device_disconnect_events",
    "file_open_events",
    "file_write_events",
    "file_copy_events",
    "file_delete_events",
    "file_to_removable_events",
    "file_from_removable_events",
    "email_send_events",
    "email_view_events",
    "email_total_size",
    "email_attachment_count",
    "email_total_events",
    "http_request_count",
    "http_unique_domain_count",
]


class PipelineRequest(BaseModel):
    dataset: str | None = Field(
        default=None, pattern=r"^[A-Za-z0-9_-]+$", description="Folder name under data/subsets."
    )
    raw_root: str | None = Field(default=None, description="Override path to raw CERT CSV folder.")
    processed_root: str | None = Field(
        default=None, description="Override path for normalized outputs."
    )
    model_output: str | None = Field(
        default=None, description="Override model artifact path (joblib)."
    )
    schema_output: str | None = Field(
        default=None, description="Override feature schema path."
    )
    chunk_size: int = Field(default=250_000, ge=1)
    contamination: float = Field(default=0.08, gt=0.0, lt=1.0)
    random_state: int = Field(default=42)
    alert_threshold: float = Field(default=DEFAULT_ALERT_THRESHOLD)
    skip_training: bool = Field(default=False)


def _normalise_path(value: str | Path | None, fallback: Path | None = None) -> Path:
    if value is None:
        if fallback is None:
            raise ValueError("Path value is required")
        return fallback
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def _resolve_paths(request: PipelineRequest) -> tuple[Path, Path, Path, Path]:
    if request.dataset:
        raw_candidate = PROJECT_ROOT / "data" / "subsets" / request.dataset
        processed_candidate = DEFAULT_PROCESSED_DIR / request.dataset
    else:
        raw_candidate = DEFAULT_RAW_DIR
        processed_candidate = None

    raw_root = _normalise_path(request.raw_root, raw_candidate)
    processed_root = (
        _normalise_path(request.processed_root)
        if request.processed_root is not None
        else (processed_candidate or (DEFAULT_PROCESSED_DIR / raw_root.name))
    )
    model_path = _normalise_path(request.model_output, DEFAULT_MODEL_FILE)
    schema_path = _normalise_path(request.schema_output, DEFAULT_SCHEMA_FILE)
    return raw_root, processed_root, model_path, schema_path


def _metric_value(value: Any) -> int | float:
    if pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return int(value) if float(value).is_integer() else float(value)
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0
    return int(numeric) if numeric.is_integer() else numeric


def _load_alerts(processed_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    alerts_path = processed_root / "streaming" / "alerts.csv"
    if not alerts_path.exists():
        raise HTTPException(status_code=404, detail=f"Alerts not found at {alerts_path}")

    try:
        frame = pd.read_csv(alerts_path)
    except Exception as exc:  # pragma: no cover - passthrough for visibility
        raise HTTPException(status_code=500, detail=f"Unable to read alerts: {exc}") from exc

    alerts: list[dict[str, Any]] = []
    for idx, row in frame.iterrows():
        event_date = row.get("event_date")
        if pd.isna(event_date):
            event_iso = None
        else:
            try:
                event_iso = pd.to_datetime(event_date).date().isoformat()
            except Exception:  # pragma: no cover - defensive fallback
                event_iso = str(event_date)

        user = row.get("user", "unknown")
        anomaly_score = float(row.get("anomaly_score", 0.0) or 0.0)
        risk_score = float(row.get("risk_score", 0.0) or 0.0)
        severity = str(row.get("severity", "medium") or "medium").strip().title()

        metrics = {
            column: _metric_value(row.get(column, 0))
            for column in METRIC_COLUMNS
            if column in frame.columns
        }

        alerts.append(
            {
                "id": f"{user}-{event_iso or idx}",
                "user": user,
                "department": row.get("department") or "Unknown",
                "functional_unit": row.get("functional_unit") or None,
                "event_date": event_iso,
                "anomaly_score": anomaly_score,
                "risk_score": risk_score,
                "severity": severity,
                "metrics": metrics,
            }
        )

    meta = {
        "dataset": processed_root.name,
        "record_count": len(alerts),
        "source": str(alerts_path.relative_to(PROJECT_ROOT)),
        "generated_at": datetime.fromtimestamp(alerts_path.stat().st_mtime, tz=timezone.utc).isoformat(),
    }
    return alerts, meta


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/alerts")
async def get_alerts(
    dataset: str | None = Query(default=None, pattern=r"^[A-Za-z0-9_-]+$"),
    processed_root: str | None = Query(default=None),
) -> dict[str, Any]:
    request = PipelineRequest(dataset=dataset, processed_root=processed_root)
    _, resolved_processed_root, _, _ = _resolve_paths(request)
    alerts, meta = await run_in_threadpool(_load_alerts, resolved_processed_root)
    return {"alerts": alerts, "meta": meta}


@app.post("/pipeline/run")
async def run_pipeline(request: PipelineRequest) -> dict[str, Any]:
    if _PIPELINE_LOCK.locked():
        raise HTTPException(status_code=409, detail="Pipeline is already running")

    raw_root, processed_root, model_path, schema_path = _resolve_paths(request)

    start = time.perf_counter()
    async with _PIPELINE_LOCK:
        try:
            outputs = await run_in_threadpool(
                run_pipeline_workflow,
                raw_root,
                processed_root,
                request.chunk_size,
                request.contamination,
                request.random_state,
                model_path,
                schema_path,
                request.alert_threshold,
                request.skip_training,
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - propagate unexpected errors
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    duration = time.perf_counter() - start
    response_outputs = {
        name: str(path) if isinstance(path, Path) else None for name, path in outputs.items()
    }

    alerts, meta = await run_in_threadpool(_load_alerts, processed_root)
    meta.update({"duration_seconds": round(duration, 3)})

    return {"status": "completed", "outputs": response_outputs, "alerts": alerts, "meta": meta}
