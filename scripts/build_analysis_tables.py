"""Build analysis-ready panels from the public Peacock source tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from load_data import PROJECT_ROOT, load_all


ANALYSIS_DIR = PROJECT_ROOT / "analysis"


def split_ids(value: object) -> list[str]:
    if pd.isna(value):
        return []
    return [item.strip() for item in str(value).split(";") if item.strip()]


def category_flags(related_ids: object, events_by_id: dict[str, str]) -> dict[str, bool]:
    categories = {events_by_id.get(tentpole_id) for tentpole_id in split_ids(related_ids)}
    return {
        "has_sports_tentpole": "Sports" in categories,
        "has_entertainment_tentpole": "Entertainment" in categories,
        "has_mixed_tentpole": "Mixed" in categories,
    }


def build_monthly_panel(monthly: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    events_by_id = events.set_index("tentpole_id")["event_category"].to_dict()

    index_cols = ["period_month", "period_start", "period_end"]
    value_panel = (
        monthly.pivot_table(
            index=index_cols,
            columns="metric_name",
            values="metric_value",
            aggfunc="first",
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )

    context = (
        monthly.groupby(index_cols, as_index=False)
        .agg(
            related_tentpole_id=("related_tentpole_id", lambda values: ";".join(sorted(set(";".join(values.dropna()).split(";"))))),
            source_titles=("source_title", lambda values: " | ".join(sorted(set(values.dropna())))),
            source_urls=("source_url", lambda values: " | ".join(sorted(set(values.dropna())))),
        )
    )

    panel = value_panel.merge(context, on=index_cols, how="left")
    flags = panel["related_tentpole_id"].apply(lambda value: category_flags(value, events_by_id))
    flags_df = pd.DataFrame(flags.tolist())
    panel = pd.concat([panel, flags_df], axis=1)

    ordered_cols = [
        "period_month",
        "period_start",
        "period_end",
        "share_of_total_tv_viewing",
        "usage_change_mom",
        "title_viewing_minutes",
        "has_sports_tentpole",
        "has_entertainment_tentpole",
        "has_mixed_tentpole",
        "related_tentpole_id",
        "source_titles",
        "source_urls",
    ]
    return panel.reindex(columns=ordered_cols).sort_values("period_month")


def build_quarterly_panel(subscribers: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    events_by_id = events.set_index("tentpole_id")["event_category"].to_dict()
    panel = subscribers.copy().sort_values("quarter_end_date")

    flags = panel["related_tentpole_id"].apply(lambda value: category_flags(value, events_by_id))
    panel = pd.concat([panel, pd.DataFrame(flags.tolist())], axis=1)

    panel["prior_quarter_paid_subscribers_millions"] = panel[
        "paid_subscribers_millions"
    ].shift(1)
    panel["calculated_sequential_change_millions"] = (
        panel["paid_subscribers_millions"]
        - panel["prior_quarter_paid_subscribers_millions"]
    )
    panel["net_adds_source_type"] = panel["net_adds_millions"].apply(
        lambda value: "not_reported" if pd.isna(value) else "reported_or_rounded_source"
    )

    ordered_cols = [
        "fiscal_quarter",
        "quarter_end_date",
        "paid_subscribers_millions",
        "prior_quarter_paid_subscribers_millions",
        "net_adds_millions",
        "calculated_sequential_change_millions",
        "net_adds_source_type",
        "revenue_usd_billions",
        "ebitda_usd_millions",
        "has_sports_tentpole",
        "has_entertainment_tentpole",
        "has_mixed_tentpole",
        "related_tentpole_id",
        "reported_context",
        "missing_value_note",
        "source_title",
        "source_publisher",
        "source_url",
    ]
    return panel.reindex(columns=ordered_cols)


def main() -> None:
    monthly, subscribers, events = load_all()
    ANALYSIS_DIR.mkdir(exist_ok=True)

    monthly_panel = build_monthly_panel(monthly, events)
    quarterly_panel = build_quarterly_panel(subscribers, events)

    monthly_path = ANALYSIS_DIR / "monthly_peacock_panel.csv"
    quarterly_path = ANALYSIS_DIR / "quarterly_subscriber_panel.csv"

    monthly_panel.to_csv(monthly_path, index=False)
    quarterly_panel.to_csv(quarterly_path, index=False)

    print(f"Wrote {len(monthly_panel)} rows to {monthly_path}")
    print(f"Wrote {len(quarterly_panel)} rows to {quarterly_path}")


if __name__ == "__main__":
    main()

