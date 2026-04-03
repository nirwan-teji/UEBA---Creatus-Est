"""Simulate a streaming risk scoring pass over normalized UEBA features."""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

DEFAULT_FEATURES_PATH = Path("data/processed/20_users/features_daily.csv")
DEFAULT_MODEL_PATH = Path("artifacts/isolation_forest.joblib")
DEFAULT_SCHEMA_PATH = Path("artifacts/feature_columns.txt")
DEFAULT_OUTPUT_DIR = Path("data/processed/20_users/streaming")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run streaming UEBA risk simulation.")
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES_PATH)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--alert-threshold", type=float, default=70.0)
    return parser.parse_args()


def load_schema(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def compute_scores(features_path: Path, model_path: Path, schema_path: Path) -> pd.DataFrame:
    frame = pd.read_csv(features_path)
    if "event_date" in frame.columns:
        frame["event_date"] = pd.to_datetime(frame["event_date"], errors="coerce")
    frame.sort_values(["event_date", "user"], inplace=True)
    schema = load_schema(schema_path)
    model = joblib.load(model_path)

    X = frame[schema].copy()
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    raw_score = -model.score_samples(X)
    min_score = raw_score.min()
    max_score = raw_score.max()
    if np.isclose(min_score, max_score):
        risk = np.zeros_like(raw_score)
    else:
        risk = (raw_score - min_score) / (max_score - min_score) * 100.0

    frame["anomaly_score"] = raw_score
    frame["risk_score"] = risk
    return frame


def build_alerts(scores: pd.DataFrame, threshold: float) -> pd.DataFrame:
    alerts = scores.loc[scores["risk_score"] >= threshold].copy()
    if alerts.empty:
        return alerts
    bins = [threshold - 1e-6, threshold + 10, threshold + 25, 1000]
    labels = ["medium", "high", "critical"]
    severity = pd.cut(alerts["risk_score"], bins=bins, labels=labels, include_lowest=True)
    if "medium" not in severity.cat.categories:
        severity = severity.cat.add_categories(["medium"])
    alerts["severity"] = severity.fillna("medium")
    return alerts


def summarize_department(scores: pd.DataFrame) -> pd.DataFrame:
    if "department" not in scores.columns:
        return pd.DataFrame()
    summary = (
        scores.groupby(["department", "event_date"], dropna=False)["risk_score"]
        .mean()
        .reset_index()
    )
    summary.rename(columns={"risk_score": "avg_risk"}, inplace=True)
    return summary


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    scores = compute_scores(args.features, args.model, args.schema)
    scores.to_csv(args.output / "daily_scores.csv", index=False)

    alerts = build_alerts(scores, threshold=args.alert_threshold)
    alerts.to_csv(args.output / "alerts.csv", index=False)

    dept_summary = summarize_department(scores)
    if not dept_summary.empty:
        dept_summary.to_csv(args.output / "department_summary.csv", index=False)

    print("Streaming simulation complete.")
    print("- daily scores ->", args.output / "daily_scores.csv")
    print("- alerts ->", args.output / "alerts.csv")
    if not dept_summary.empty:
        print("- department summary ->", args.output / "department_summary.csv")


if __name__ == "__main__":
    main()
