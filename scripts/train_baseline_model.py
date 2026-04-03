"""Train a baseline IsolationForest model on normalized UEBA features."""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

DEFAULT_FEATURES_PATH = Path("data/processed/20_users/features_daily.csv")
DEFAULT_ARTIFACT_PATH = Path("artifacts/isolation_forest.joblib")
DEFAULT_SCHEMA_PATH = Path("artifacts/feature_columns.txt")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train baseline anomaly detection model.")
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES_PATH, help="Path to normalized feature table.")
    parser.add_argument("--output", type=Path, default=DEFAULT_ARTIFACT_PATH, help="Destination for serialized model pipeline.")
    parser.add_argument("--schema-output", type=Path, default=DEFAULT_SCHEMA_PATH, help="File to record numeric feature columns.")
    parser.add_argument("--contamination", type=float, default=0.08, help="Estimated anomaly ratio for IsolationForest.")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed for reproducibility.")
    return parser.parse_args()


def load_feature_matrix(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    frame = pd.read_csv(path)
    if "event_date" in frame.columns:
        frame["event_date"] = pd.to_datetime(frame["event_date"], errors="coerce")
    numeric_cols = frame.select_dtypes(include=["number"]).columns.tolist()
    features = frame[numeric_cols].copy().replace([np.inf, -np.inf], np.nan).fillna(0.0)
    metadata_cols = [col for col in frame.columns if col not in numeric_cols]
    metadata = frame[metadata_cols].copy()
    return features, metadata, numeric_cols


def build_model(contamination: float, random_state: int) -> Pipeline:
    forest = IsolationForest(n_estimators=300, contamination=contamination, random_state=random_state)
    return Pipeline([("scaler", StandardScaler()), ("model", forest)])


def main() -> None:
    args = parse_args()
    features, _, columns = load_feature_matrix(args.features)
    model = build_model(contamination=args.contamination, random_state=args.random_state)
    model.fit(features)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, args.output)
    args.schema_output.parent.mkdir(parents=True, exist_ok=True)
    args.schema_output.write_text("\n".join(columns))

    print(f"Model trained and saved to {args.output}")
    print(f"Feature schema captured at {args.schema_output}")


if __name__ == "__main__":
    main()
