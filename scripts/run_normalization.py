"""Execute chunked normalization pipeline for a given CERT data directory."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.normalizer import generate_daily_feature_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize CERT UEBA datasets.")
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=Path("data/subsets/new_users"),
        help="Directory containing raw CERT CSV files.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/processed/new_users"),
        help="Directory to write normalized outputs.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=250_000,
        help="Chunk size for streaming CSV reads.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    outputs = generate_daily_feature_pipeline(
        raw_root=args.raw_root,
        processed_root=args.output_root,
        chunk_size=args.chunk_size,
    )
    print("Normalization complete.")
    for name, path in outputs.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
