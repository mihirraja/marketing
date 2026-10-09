#!/usr/bin/env python3
"""Validate the Peacock marketing analytics CSV dataset."""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

FILES = {
    "monthly": DATA / "peacock_marketing_analytics_2024_2026_monthly_viewing.csv",
    "subscribers": DATA / "peacock_marketing_analytics_2024_2026_quarterly_subscribers.csv",
    "events": DATA / "peacock_marketing_analytics_2024_2026_tentpole_events.csv",
}

REQUIRED_COLUMNS = {
    "monthly": [
        "period_month",
        "platform",
        "metric_name",
        "metric_value",
        "metric_unit",
        "related_tentpole_id",
        "source_title",
        "source_publisher",
        "source_url",
        "verification_status",
    ],
    "subscribers": [
        "fiscal_quarter",
        "quarter_end_date",
        "platform",
        "paid_subscribers_millions",
        "related_tentpole_id",
        "source_title",
        "source_publisher",
        "source_url",
        "verification_status",
    ],
    "events": [
        "tentpole_id",
        "event_name",
        "event_category",
        "event_start_date",
        "event_end_date",
        "source_title",
        "source_publisher",
        "source_url",
        "verification_status",
    ],
}

NUMERIC_COLUMNS = {
    "monthly": [
        "metric_value",
        "month_over_month_change_value",
        "year_over_year_change_value",
    ],
    "subscribers": [
        "paid_subscribers_millions",
        "net_adds_millions",
        "revenue_usd_billions",
        "ebitda_usd_millions",
    ],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def check_columns(name: str, rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    if not rows:
        return [f"{name}: file is empty"]
    columns = set(rows[0])
    for column in REQUIRED_COLUMNS[name]:
        if column not in columns:
            errors.append(f"{name}: missing required column {column}")
    return errors


def check_numeric(name: str, rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for idx, row in enumerate(rows, start=2):
        for column in NUMERIC_COLUMNS.get(name, []):
            value = row.get(column, "")
            if value == "":
                continue
            try:
                float(value)
            except ValueError:
                errors.append(f"{name}: line {idx} has nonnumeric {column}={value!r}")
    return errors


def check_urls(name: str, rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for idx, row in enumerate(rows, start=2):
        parsed = urlparse(row.get("source_url", ""))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append(f"{name}: line {idx} has invalid source_url")
    return errors


def split_ids(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def check_tentpole_links(rows_by_name: dict[str, list[dict[str, str]]]) -> list[str]:
    errors: list[str] = []
    event_ids = {row["tentpole_id"] for row in rows_by_name["events"]}
    for table_name in ("monthly", "subscribers"):
        for idx, row in enumerate(rows_by_name[table_name], start=2):
            for tentpole_id in split_ids(row.get("related_tentpole_id", "")):
                if tentpole_id not in event_ids:
                    errors.append(
                        f"{table_name}: line {idx} references unknown tentpole_id {tentpole_id}"
                    )
    return errors


def main() -> int:
    rows_by_name = {name: read_csv(path) for name, path in FILES.items()}
    errors: list[str] = []

    for name, rows in rows_by_name.items():
        errors.extend(check_columns(name, rows))
        errors.extend(check_numeric(name, rows))
        errors.extend(check_urls(name, rows))

    errors.extend(check_tentpole_links(rows_by_name))

    if errors:
        print("Dataset validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    for name, rows in rows_by_name.items():
        print(f"{name}: {len(rows)} rows OK")
    print("Dataset validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

