"""Utilities for converting raw CERT CSV logs into daily feature tables."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

import pandas as pd
from pandas import DataFrame
from urllib.parse import urlsplit


def _normalize_event_date(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series, errors="coerce", utc=True)
    return dt.dt.tz_convert(None).dt.normalize()


def _count_attachments(cell: str | float | int | None) -> int:
    if not isinstance(cell, str) or not cell:
        return 0
    return len([part for part in str(cell).split(";") if part])


def _extract_domain(url: str | float | int | None) -> str | None:
    if not isinstance(url, str) or not url:
        return None
    parsed = urlsplit(url)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host or None


def _load_selected_users(raw_root: Path) -> set[str]:
    path = raw_root / "selected_users.csv"
    if not path.exists():
        return set()
    frame = pd.read_csv(path)
    if "user" in frame.columns:
        column = "user"
    else:
        column = "user_id"
    return set(frame[column].dropna().astype(str))


def _load_user_metadata(raw_root: Path) -> DataFrame:
    candidates = [
        raw_root / "users.csv",
        raw_root.parent / "users.csv",
        Path("data/raw/users.csv"),
    ]
    for candidate in candidates:
        if candidate.exists():
            frame = pd.read_csv(candidate)
            column_map = {}
            if "user_id" in frame.columns:
                column_map["user_id"] = "user"
            if "department" in frame.columns:
                column_map["department"] = "department"
            if "functional_unit" in frame.columns:
                column_map["functional_unit"] = "functional_unit"
            if not column_map:
                continue
            renamed = frame.rename(columns=column_map)
            return renamed.get([col for col in ["user", "department", "functional_unit"] if col in renamed.columns])
    return pd.DataFrame(columns=["user", "department", "functional_unit"])


def _aggregate_counts(path: Path, chunk_size: int, mapping: dict[str, str]) -> DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["user", "event_date", *mapping.values()])

    frames: list[DataFrame] = []
    usecols = ["date", "user", "activity"]
    for chunk in pd.read_csv(path, usecols=usecols, chunksize=chunk_size):
        chunk["event_date"] = _normalize_event_date(chunk["date"])
        chunk = chunk.dropna(subset=["user", "event_date"])
        chunk["activity"] = chunk["activity"].astype(str).str.strip().str.lower()
        for raw_value, normalized in mapping.items():
            chunk[normalized] = (chunk["activity"] == raw_value).astype(int)
        grouped = chunk.groupby(["user", "event_date"])[list(mapping.values())].sum().reset_index()
        frames.append(grouped)

    if not frames:
        return pd.DataFrame(columns=["user", "event_date", *mapping.values()])

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.groupby(["user", "event_date"], as_index=False)[list(mapping.values())].sum()
    return combined


def _aggregate_logon(raw_root: Path, chunk_size: int) -> DataFrame:
    path = raw_root / "logon.csv"
    mapping = {
        "logon": "logon_logon_events",
        "logoff": "logon_logoff_events",
    }
    frame = _aggregate_counts(path, chunk_size, mapping)
    if frame.empty:
        return frame
    frame["logon_total_events"] = frame[["logon_logon_events", "logon_logoff_events"]].sum(axis=1)
    return frame


def _aggregate_device(raw_root: Path, chunk_size: int) -> DataFrame:
    path = raw_root / "device.csv"
    mapping = {
        "connect": "device_connect_events",
        "disconnect": "device_disconnect_events",
    }
    return _aggregate_counts(path, chunk_size, mapping)


def _aggregate_file(raw_root: Path, chunk_size: int) -> DataFrame:
    path = raw_root / "file.csv"
    if not path.exists():
        columns = [
            "user",
            "event_date",
            "file_open_events",
            "file_write_events",
            "file_copy_events",
            "file_delete_events",
            "file_to_removable_events",
            "file_from_removable_events",
        ]
        return pd.DataFrame(columns=columns)

    frames: list[DataFrame] = []
    usecols = [
        "date",
        "user",
        "activity",
        "to_removable_media",
        "from_removable_media",
    ]
    activity_map = {
        "file open": "file_open_events",
        "file write": "file_write_events",
        "file copy": "file_copy_events",
        "file delete": "file_delete_events",
    }

    for chunk in pd.read_csv(path, usecols=usecols, chunksize=chunk_size):
        chunk["event_date"] = _normalize_event_date(chunk["date"])
        chunk = chunk.dropna(subset=["user", "event_date"])
        chunk["activity"] = chunk["activity"].astype(str).str.strip().str.lower()
        for raw, normalized in activity_map.items():
            chunk[normalized] = (chunk["activity"] == raw).astype(int)
        chunk["file_to_removable_events"] = (
            chunk["to_removable_media"].astype(str).str.lower() == "true"
        ).astype(int)
        chunk["file_from_removable_events"] = (
            chunk["from_removable_media"].astype(str).str.lower() == "true"
        ).astype(int)
        grouped = chunk.groupby(["user", "event_date"])[
            list(activity_map.values()) + ["file_to_removable_events", "file_from_removable_events"]
        ].sum().reset_index()
        frames.append(grouped)

    if not frames:
        return pd.DataFrame(columns=list(activity_map.values()))

    combined = pd.concat(frames, ignore_index=True)
    columns = list(activity_map.values()) + ["file_to_removable_events", "file_from_removable_events"]
    combined = combined.groupby(["user", "event_date"], as_index=False)[columns].sum()
    return combined


def _aggregate_email(raw_root: Path, chunk_size: int) -> DataFrame:
    path = raw_root / "email.csv"
    if not path.exists():
        columns = [
            "user",
            "event_date",
            "email_send_events",
            "email_view_events",
            "email_total_size",
            "email_attachment_count",
        ]
        return pd.DataFrame(columns=columns)

    frames: list[DataFrame] = []
    usecols = ["date", "user", "activity", "size", "attachments"]
    for chunk in pd.read_csv(path, usecols=usecols, chunksize=chunk_size):
        chunk["event_date"] = _normalize_event_date(chunk["date"])
        chunk = chunk.dropna(subset=["user", "event_date"])
        chunk["activity"] = chunk["activity"].astype(str).str.strip().str.lower()
        chunk["email_send_events"] = (chunk["activity"] == "send").astype(int)
        chunk["email_view_events"] = (chunk["activity"] == "view").astype(int)
        chunk["email_total_size"] = pd.to_numeric(chunk["size"], errors="coerce").fillna(0)
        chunk["email_attachment_count"] = chunk["attachments"].map(_count_attachments).astype(int)
        grouped = chunk.groupby(["user", "event_date"])[
            [
                "email_send_events",
                "email_view_events",
                "email_total_size",
                "email_attachment_count",
            ]
        ].sum().reset_index()
        frames.append(grouped)

    if not frames:
        return pd.DataFrame(columns=["user", "event_date"])

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.groupby(["user", "event_date"], as_index=False)[
        ["email_send_events", "email_view_events", "email_total_size", "email_attachment_count"]
    ].sum()
    combined["email_total_events"] = combined[["email_send_events", "email_view_events"]].sum(axis=1)
    return combined


def _aggregate_http(raw_root: Path, chunk_size: int) -> DataFrame:
    path = raw_root / "http.csv"
    if not path.exists():
        columns = [
            "user",
            "event_date",
            "http_request_count",
            "http_unique_domain_count",
        ]
        return pd.DataFrame(columns=columns)

    frames: list[DataFrame] = []
    domain_tracker: dict[tuple[str, pd.Timestamp], set[str]] = defaultdict(set)
    usecols = ["date", "user", "url"]
    for chunk in pd.read_csv(path, usecols=usecols, chunksize=chunk_size):
        chunk["event_date"] = _normalize_event_date(chunk["date"])
        chunk = chunk.dropna(subset=["user", "event_date"])
        chunk["http_request_count"] = 1
        grouped = chunk.groupby(["user", "event_date"])["http_request_count"].sum().reset_index()
        frames.append(grouped)
        chunk["domain"] = chunk["url"].map(_extract_domain)
        for (user, event_date), group in chunk.groupby(["user", "event_date"]):
            domains = set(domain for domain in group["domain"] if isinstance(domain, str) and domain)
            if domains:
                domain_tracker[(user, event_date)].update(domains)

    if frames:
        counts = pd.concat(frames, ignore_index=True)
        counts = counts.groupby(["user", "event_date"], as_index=False)["http_request_count"].sum()
    else:
        counts = pd.DataFrame(columns=["user", "event_date", "http_request_count"])

    domain_rows = [
        {"user": key[0], "event_date": key[1], "http_unique_domain_count": len(domains)}
        for key, domains in domain_tracker.items()
    ]
    domain_df = (
        pd.DataFrame(domain_rows)
        if domain_rows
        else pd.DataFrame(columns=["user", "event_date", "http_unique_domain_count"])
    )

    merged = counts.merge(domain_df, on=["user", "event_date"], how="left")
    merged["http_unique_domain_count"] = merged["http_unique_domain_count"].fillna(0).astype(int)
    return merged


def _merge_features(frames: Iterable[DataFrame]) -> DataFrame:
    valid_frames = [frame for frame in frames if frame is not None and not frame.empty]
    if not valid_frames:
        return pd.DataFrame(columns=["user", "event_date"])

    index_df = (
        pd.concat([frame[["user", "event_date"]] for frame in valid_frames], ignore_index=True)
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dataset = index_df
    for frame in valid_frames:
        dataset = dataset.merge(frame, on=["user", "event_date"], how="left")

    numeric_cols = dataset.select_dtypes(include=["float", "int"]).columns
    dataset[numeric_cols] = dataset[numeric_cols].fillna(0)
    dataset = dataset.sort_values(["event_date", "user"]).reset_index(drop=True)
    return dataset


def generate_daily_feature_pipeline(*, raw_root: Path, processed_root: Path, chunk_size: int = 250_000) -> dict[str, Path]:
    processed_root.mkdir(parents=True, exist_ok=True)
    selected_users = _load_selected_users(raw_root)

    logon_df = _aggregate_logon(raw_root, chunk_size)
    device_df = _aggregate_device(raw_root, chunk_size)
    file_df = _aggregate_file(raw_root, chunk_size)
    email_df = _aggregate_email(raw_root, chunk_size)
    http_df = _aggregate_http(raw_root, chunk_size)

    frames = [logon_df, device_df, file_df, email_df, http_df]
    if selected_users:
        frames = [frame[frame["user"].isin(selected_users)] if not frame.empty else frame for frame in frames]

    feature_table = _merge_features(frames)
    user_metadata = _load_user_metadata(raw_root)
    if not user_metadata.empty:
        feature_table = feature_table.merge(user_metadata, on="user", how="left")

    feature_table["event_date"] = pd.to_datetime(feature_table["event_date"], errors="coerce").dt.date

    outputs: dict[str, Path] = {}

    if not logon_df.empty:
        logon_path = processed_root / "logon_daily.csv"
        logon_df.sort_values(["event_date", "user"]).to_csv(logon_path, index=False)
        outputs["logon_daily"] = logon_path

    if not device_df.empty:
        device_path = processed_root / "device_daily.csv"
        device_df.sort_values(["event_date", "user"]).to_csv(device_path, index=False)
        outputs["device_daily"] = device_path

    if not file_df.empty:
        file_path = processed_root / "file_daily.csv"
        file_df.sort_values(["event_date", "user"]).to_csv(file_path, index=False)
        outputs["file_daily"] = file_path

    if not email_df.empty:
        email_path = processed_root / "email_daily.csv"
        email_df.sort_values(["event_date", "user"]).to_csv(email_path, index=False)
        outputs["email_daily"] = email_path

    if not http_df.empty:
        http_path = processed_root / "http_daily.csv"
        http_df.sort_values(["event_date", "user"]).to_csv(http_path, index=False)
        outputs["http_daily"] = http_path

    features_path = processed_root / "features_daily.csv"
    feature_table.sort_values(["event_date", "user"]).to_csv(features_path, index=False)
    outputs["features_daily"] = features_path

    return outputs
