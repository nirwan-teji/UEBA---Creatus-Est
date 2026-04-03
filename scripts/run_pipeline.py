"""Run normalization, model training, and streaming outputs in a single pass."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.normalizer import generate_daily_feature_pipeline
from scripts.run_streaming_demo import build_alerts, compute_scores, summarize_department
from scripts.train_baseline_model import build_model, load_feature_matrix

DEFAULT_RAW_ROOT = Path("data/subsets/new_users")
DEFAULT_PROCESSED_ROOT = Path("data/processed/new_users")
DEFAULT_MODEL_PATH = Path("artifacts/isolation_forest.joblib")
DEFAULT_SCHEMA_PATH = Path("artifacts/feature_columns.txt")
DEFAULT_ALERT_THRESHOLD = 70.0


def run_pipeline_workflow(
    raw_root: Path = DEFAULT_RAW_ROOT,
    processed_root: Path | None = None,
    chunk_size: int = 250_000,
    contamination: float = 0.08,
    random_state: int = 42,
    model_output: Path = DEFAULT_MODEL_PATH,
    schema_output: Path = DEFAULT_SCHEMA_PATH,
    alert_threshold: float = DEFAULT_ALERT_THRESHOLD,
    skip_training: bool = False,
) -> dict[str, Path | None]:
    """Execute the end-to-end pipeline and return generated artifact paths."""

    raw_root = Path(raw_root)
    processed_root_path = Path(processed_root) if processed_root is not None else None
    model_output = Path(model_output)
    schema_output = Path(schema_output)

    resolved_processed_root = resolve_processed_root(raw_root, processed_root_path)
    features_path = run_normalization(raw_root, resolved_processed_root, chunk_size)

    if skip_training:
        if not model_output.exists() or not schema_output.exists():
            raise FileNotFoundError("Cannot skip training; model or schema artifact is missing.")
        print("[train] Skipping training step, using existing artifacts.")
    else:
        run_training(features_path, contamination, random_state, model_output, schema_output)

    outputs = run_streaming(
        features_path=features_path,
        model_path=model_output,
        schema_path=schema_output,
        processed_root=resolved_processed_root,
        alert_threshold=alert_threshold,
    )

    outputs["features"] = features_path
    outputs["processed_root"] = resolved_processed_root
    return outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run complete UEBA pipeline for a dataset.")
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT, help="Directory containing raw CERT CSV files.")
    parser.add_argument(
        "--processed-root",
        type=Path,
        default=None,
        help="Directory to write normalized artifacts (defaults to data/processed/<raw-folder-name>).",
    )
    parser.add_argument("--chunk-size", type=int, default=250_000, help="Chunk size for streaming CSV reads during normalization.")
    parser.add_argument("--contamination", type=float, default=0.08, help="IsolationForest contamination proportion.")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed for model reproducibility.")
    parser.add_argument("--model-output", type=Path, default=DEFAULT_MODEL_PATH, help="Path to serialize the model pipeline.")
    parser.add_argument("--schema-output", type=Path, default=DEFAULT_SCHEMA_PATH, help="Path to write numeric feature column list.")
    parser.add_argument("--alert-threshold", type=float, default=DEFAULT_ALERT_THRESHOLD, help="Risk score threshold for alert generation.")
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Reuse existing model artifacts instead of retraining. Requires model/schema to exist.",
    )
    return parser.parse_args()


def resolve_processed_root(raw_root: Path, processed_root: Path | None) -> Path:
    if processed_root is not None:
        return processed_root
    return Path("data/processed") / raw_root.name


def run_normalization(raw_root: Path, processed_root: Path, chunk_size: int) -> Path:
    processed_root.mkdir(parents=True, exist_ok=True)
    outputs = generate_daily_feature_pipeline(raw_root=raw_root, processed_root=processed_root, chunk_size=chunk_size)
    features_path = outputs.get("features_daily", processed_root / "features_daily.csv")
    if not features_path.exists():
        raise FileNotFoundError(f"Normalization did not produce features table at {features_path}")
    print(f"[normalize] Features written to {features_path}")
    return features_path


def run_training(features_path: Path, contamination: float, random_state: int, model_output: Path, schema_output: Path) -> None:
    features, _, columns = load_feature_matrix(features_path)
    model = build_model(contamination=contamination, random_state=random_state)
    model.fit(features)

    model_output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_output)
    schema_output.parent.mkdir(parents=True, exist_ok=True)
    schema_output.write_text("\n".join(columns))
    print(f"[train] Model saved to {model_output}")
    print(f"[train] Feature schema saved to {schema_output}")


def run_streaming(
    features_path: Path,
    model_path: Path,
    schema_path: Path,
    processed_root: Path,
    alert_threshold: float,
) -> dict[str, Path | None]:
    streaming_dir = processed_root / "streaming"
    streaming_dir.mkdir(parents=True, exist_ok=True)

    scores = compute_scores(features_path, model_path, schema_path)
    scores_path = streaming_dir / "daily_scores.csv"
    scores.to_csv(scores_path, index=False)

    alerts = build_alerts(scores, threshold=alert_threshold)
    alerts_path = streaming_dir / "alerts.csv"
    alerts.to_csv(alerts_path, index=False)

    dept_summary = summarize_department(scores)
    dept_path = streaming_dir / "department_summary.csv"
    if not dept_summary.empty:
        dept_summary.to_csv(dept_path, index=False)
        dept_summary_path: Path | None = dept_path
        print(f"[stream] Department summary -> {dept_path}")
    else:
        dept_summary_path = None
        if dept_path.exists():
            dept_path.unlink()
        print("[stream] Department summary not generated (department column missing).")

    print(f"[stream] Daily scores -> {scores_path}")
    print(f"[stream] Alerts ({len(alerts)} rows) -> {alerts_path}")

    return {
        "daily_scores": scores_path,
        "alerts": alerts_path,
        "department_summary": dept_summary_path,
    }


def main() -> None:
    args = parse_args()
    start = datetime.now()

    print(
        "[pipeline] Starting run with raw_root="
        f"{args.raw_root}, processed_root={resolve_processed_root(args.raw_root, args.processed_root)}"
    )

    outputs = run_pipeline_workflow(
        raw_root=args.raw_root,
        processed_root=args.processed_root,
        chunk_size=args.chunk_size,
        contamination=args.contamination,
        random_state=args.random_state,
        model_output=args.model_output,
        schema_output=args.schema_output,
        alert_threshold=args.alert_threshold,
        skip_training=args.skip_training,
    )

    elapsed = datetime.now() - start
    print(f"[pipeline] Completed in {elapsed}")
    print(f"[pipeline] Features -> {outputs['features']}")
    print(f"[pipeline] Alerts ready at {outputs['alerts']}")


if __name__ == "__main__":
    main()
