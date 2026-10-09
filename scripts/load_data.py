"""Shared data-loading helpers for the Peacock analytics project."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def load_monthly_viewing() -> pd.DataFrame:
    path = DATA_DIR / "peacock_marketing_analytics_2024_2026_monthly_viewing.csv"
    df = pd.read_csv(path)
    df["period_month"] = pd.to_datetime(df["period_month"])
    df["period_start"] = pd.to_datetime(df["period_start"])
    df["period_end"] = pd.to_datetime(df["period_end"])
    return df


def load_quarterly_subscribers() -> pd.DataFrame:
    path = DATA_DIR / "peacock_marketing_analytics_2024_2026_quarterly_subscribers.csv"
    df = pd.read_csv(path)
    df["quarter_end_date"] = pd.to_datetime(df["quarter_end_date"])
    return df


def load_tentpole_events() -> pd.DataFrame:
    path = DATA_DIR / "peacock_marketing_analytics_2024_2026_tentpole_events.csv"
    df = pd.read_csv(path)
    df["event_start_date"] = pd.to_datetime(df["event_start_date"])
    df["event_end_date"] = pd.to_datetime(df["event_end_date"])
    df["primary_month"] = pd.to_datetime(df["primary_month"])
    return df


def load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return load_monthly_viewing(), load_quarterly_subscribers(), load_tentpole_events()

