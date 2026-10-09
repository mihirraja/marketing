"""Summarize first-pass marketing insights from the Peacock analysis panels."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from load_data import PROJECT_ROOT


ANALYSIS_DIR = PROJECT_ROOT / "analysis"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
RUNS_DIR = OUTPUT_DIR / "runs"
MONTHLY_PANEL = ANALYSIS_DIR / "monthly_peacock_panel.csv"
QUARTERLY_PANEL = ANALYSIS_DIR / "quarterly_subscriber_panel.csv"
CONCISE_REPORT_PATH = OUTPUT_DIR / "peacock_marketing_insights_concise.md"
MEMO_REPORT_PATH = OUTPUT_DIR / "peacock_marketing_insights_memo.md"
TIMEZONE = ZoneInfo("America/Los_Angeles")


def format_bool(value: object) -> str:
    return "yes" if bool(value) else "no"


def section(title: str, lines: list[str]) -> list[str]:
    return [f"## {title}", "", *lines, ""]


def bullets(lines: list[str]) -> list[str]:
    return [f"- {line}" for line in lines]


def load_panels() -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly = pd.read_csv(MONTHLY_PANEL, parse_dates=["period_month"])
    quarterly = pd.read_csv(QUARTERLY_PANEL, parse_dates=["quarter_end_date"])
    return monthly, quarterly


def category_label(row: pd.Series) -> str:
    categories = []
    if row["has_sports_tentpole"]:
        categories.append("Sports")
    if row["has_entertainment_tentpole"]:
        categories.append("Entertainment")
    if row["has_mixed_tentpole"]:
        categories.append("Mixed")
    return " + ".join(categories) if categories else "No mapped tentpole"


def summarize_executive_summary(
    monthly: pd.DataFrame, quarterly: pd.DataFrame
) -> list[str]:
    top_month = monthly.sort_values(
        "share_of_total_tv_viewing", ascending=False
    ).iloc[0]
    strongest_sub_quarter = quarterly.sort_values(
        "net_adds_millions", ascending=False, na_position="last"
    ).iloc[0]
    q3_2024 = quarterly[quarterly["fiscal_quarter"] == "2024-Q3"].iloc[0]

    lines = bullets(
        [
            f"Peacock's highest observed monthly TV share in this public panel is "
            f"{top_month['share_of_total_tv_viewing']:.1f}% in "
            f"{top_month['period_month']:%Y-%m}, a Sports + Entertainment month anchored by "
            "Super Bowl and Winter Olympics programming.",
            "The strongest repeat pattern is sports-led reach, with the largest TV-share "
            "months tied to Olympics, Super Bowl, World Cup, and NFL tentpoles.",
            "Love Island appears to be Peacock's clearest repeat entertainment tentpole, "
            "showing up in both 2025 and 2026 summer viewing lifts.",
            f"The cleanest content-linked subscriber case is 2024-Q3, when Peacock moved "
            f"from 33M to {q3_2024['paid_subscribers_millions']:g}M paid subscribers "
            "alongside Paris Olympics and Love Island momentum.",
            f"The largest reported quarterly subscriber increase is "
            f"{strongest_sub_quarter['fiscal_quarter']} at "
            f"{strongest_sub_quarter['net_adds_millions']:g}M net adds, but that quarter "
            "is marked as Mixed because Comcast tied the growth to Charter bundle entitlements.",
        ]
    )
    return section("Executive Summary", lines)


def summarize_top_viewing_months(monthly: pd.DataFrame) -> list[str]:
    top_months = monthly.sort_values(
        "share_of_total_tv_viewing", ascending=False
    ).head(5)

    lines = [
        "| Month | TV share | Tentpole category | Related tentpoles |",
        "| --- | ---: | --- | --- |",
    ]
    for _, row in top_months.iterrows():
        lines.append(
            f"| {row['period_month']:%Y-%m} | "
            f"{row['share_of_total_tv_viewing']:.1f}% | "
            f"{category_label(row)} | "
            f"{row['related_tentpole_id']} |"
        )
    return section("Evidence: Top Peacock TV Share Months", lines)


def summarize_top_viewing_months_concise(monthly: pd.DataFrame) -> list[str]:
    top_months = monthly.sort_values(
        "share_of_total_tv_viewing", ascending=False
    ).head(5)

    lines = []
    for _, row in top_months.iterrows():
        lines.append(
            f"{row['period_month']:%Y-%m}: "
            f"{row['share_of_total_tv_viewing']:.1f}% TV share "
            f"({category_label(row)})"
        )
    return section("Top Peacock TV Share Months", lines)


def summarize_tentpole_patterns(monthly: pd.DataFrame) -> list[str]:
    flag_cols = [
        ("Sports", "has_sports_tentpole"),
        ("Entertainment", "has_entertainment_tentpole"),
        ("Mixed", "has_mixed_tentpole"),
    ]

    lines = [
        "| Category | Observed months | Average TV share | Max TV share |",
        "| --- | ---: | ---: | ---: |",
    ]
    for label, column in flag_cols:
        subset = monthly[monthly[column]]
        if subset.empty:
            lines.append(f"| {label} | 0 | n.a. | n.a. |")
            continue
        avg_share = subset["share_of_total_tv_viewing"].mean()
        max_share = subset["share_of_total_tv_viewing"].max()
        lines.append(
            f"| {label} | {len(subset)} | {avg_share:.2f}% | {max_share:.1f}% |"
        )

    both = monthly[
        monthly["has_sports_tentpole"] & monthly["has_entertainment_tentpole"]
    ]
    if not both.empty:
        months = ", ".join(both["period_month"].dt.strftime("%Y-%m"))
        lines.extend(["", f"Sports + Entertainment overlap months: {months}"])
    return section("Tentpole Pattern", lines)


def summarize_tentpole_patterns_concise(monthly: pd.DataFrame) -> list[str]:
    flag_cols = [
        ("Sports", "has_sports_tentpole"),
        ("Entertainment", "has_entertainment_tentpole"),
        ("Mixed", "has_mixed_tentpole"),
    ]

    lines = []
    for label, column in flag_cols:
        subset = monthly[monthly[column]]
        if subset.empty:
            lines.append(f"{label}: no observed months")
            continue
        avg_share = subset["share_of_total_tv_viewing"].mean()
        max_share = subset["share_of_total_tv_viewing"].max()
        lines.append(
            f"{label}: {len(subset)} observed months, "
            f"average TV share {avg_share:.2f}%, max {max_share:.1f}%"
        )

    both = monthly[
        monthly["has_sports_tentpole"] & monthly["has_entertainment_tentpole"]
    ]
    if not both.empty:
        months = ", ".join(both["period_month"].dt.strftime("%Y-%m"))
        lines.append(f"Sports + Entertainment overlap months: {months}")
    return section("Tentpole Pattern", lines)


def summarize_subscribers(quarterly: pd.DataFrame) -> list[str]:
    display = quarterly[
        [
            "fiscal_quarter",
            "paid_subscribers_millions",
            "net_adds_millions",
            "calculated_sequential_change_millions",
            "has_sports_tentpole",
            "has_entertainment_tentpole",
            "has_mixed_tentpole",
        ]
    ].copy()

    lines = [
        "| Quarter | Paid subs | Reported net adds | Sequential change | Category flags |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for _, row in display.iterrows():
        net_adds = row["net_adds_millions"]
        reported_net = "not reported" if pd.isna(net_adds) else f"{net_adds:g}M"
        calculated = row["calculated_sequential_change_millions"]
        calculated_text = "n.a." if pd.isna(calculated) else f"{calculated:g}M"
        flags = []
        if row["has_sports_tentpole"]:
            flags.append("Sports")
        if row["has_entertainment_tentpole"]:
            flags.append("Entertainment")
        if row["has_mixed_tentpole"]:
            flags.append("Mixed")
        flag_text = " + ".join(flags) if flags else "None"
        lines.append(
            f"| {row['fiscal_quarter']} | "
            f"{row['paid_subscribers_millions']:g}M | "
            f"{reported_net} | "
            f"{calculated_text} | "
            f"{flag_text} |"
        )
    return section("Evidence: Quarterly Subscriber Movement", lines)


def summarize_subscribers_concise(quarterly: pd.DataFrame) -> list[str]:
    display = quarterly[
        [
            "fiscal_quarter",
            "paid_subscribers_millions",
            "net_adds_millions",
            "calculated_sequential_change_millions",
            "has_sports_tentpole",
            "has_entertainment_tentpole",
            "has_mixed_tentpole",
        ]
    ].copy()

    lines = []
    for _, row in display.iterrows():
        net_adds = row["net_adds_millions"]
        reported_net = "not reported" if pd.isna(net_adds) else f"{net_adds:g}M"
        calculated = row["calculated_sequential_change_millions"]
        calculated_text = "n.a." if pd.isna(calculated) else f"{calculated:g}M"
        lines.append(
            f"{row['fiscal_quarter']}: "
            f"{row['paid_subscribers_millions']:g}M paid subs, "
            f"reported net adds {reported_net}, "
            f"sequential change {calculated_text}, "
            f"sports={format_bool(row['has_sports_tentpole'])}, "
            f"entertainment={format_bool(row['has_entertainment_tentpole'])}, "
            f"mixed={format_bool(row['has_mixed_tentpole'])}"
        )
    return section("Quarterly Subscriber Movement", lines)


def summarize_early_takeaways_concise(
    monthly: pd.DataFrame, quarterly: pd.DataFrame
) -> list[str]:
    top_month = monthly.sort_values(
        "share_of_total_tv_viewing", ascending=False
    ).iloc[0]
    strongest_sub_quarter = quarterly.sort_values(
        "net_adds_millions", ascending=False, na_position="last"
    ).iloc[0]

    lines = [
        f"1. The highest observed Peacock viewing month is "
        f"{top_month['period_month']:%Y-%m} at "
        f"{top_month['share_of_total_tv_viewing']:.1f}% TV share.",
        "2. Sports tentpoles dominate the largest TV-share observations, "
        "while Love Island adds repeatable summer entertainment lift.",
        f"3. The largest reported quarterly paid-subscriber gain in this panel is "
        f"{strongest_sub_quarter['fiscal_quarter']} with "
        f"{strongest_sub_quarter['net_adds_millions']:g}M net adds.",
        "4. Treat this as directional public-source analysis: Nielsen months and "
        "Comcast quarters are different grains, and missing public values are not estimated.",
    ]
    return section("Early Takeaways", lines)


def summarize_interpretation() -> list[str]:
    lines = bullets(
        [
            "Sports tentpoles appear to be Peacock's strongest reach events. They line up "
            "with the largest monthly viewing-share observations and several reported "
            "subscriber-add quarters.",
            "Entertainment tentpoles appear to work differently. Love Island is less like "
            "a one-day acquisition event and more like a recurring summer engagement engine.",
            "Mixed and distribution-driven rows should be interpreted separately from "
            "content-led demand. The 2025-Q1 Charter bundle row is important, but it is not "
            "the same mechanism as Olympics or Love Island viewing lift.",
        ]
    )
    return section("Interpretation", lines)


def summarize_limitations() -> list[str]:
    lines = bullets(
        [
            "Nielsen viewing rows are monthly or Nielsen measurement-month observations; "
            "Comcast subscriber rows are quarterly observations.",
            "The dataset does not interpolate monthly subscribers and does not estimate "
            "missing values.",
            "Subscriber counts are rounded public disclosures, so small sequential moves "
            "can be hidden by rounding.",
            "The analysis is directional and source-grounded; it should not be read as "
            "causal proof without deeper campaign, spend, conversion, and retention data.",
        ]
    )
    return section("Limitations", lines)


def build_concise_report(monthly: pd.DataFrame, quarterly: pd.DataFrame) -> str:
    lines = [
        "# Peacock Marketing Insights",
        "",
        *summarize_top_viewing_months_concise(monthly),
        *summarize_tentpole_patterns_concise(monthly),
        *summarize_subscribers_concise(quarterly),
        *summarize_early_takeaways_concise(monthly, quarterly),
    ]
    return "\n".join(lines).rstrip() + "\n"


def build_memo_report(monthly: pd.DataFrame, quarterly: pd.DataFrame) -> str:
    lines = [
        "# Peacock Marketing Insights Memo",
        "",
        *summarize_executive_summary(monthly, quarterly),
        *summarize_top_viewing_months(monthly),
        *summarize_tentpole_patterns(monthly),
        *summarize_subscribers(quarterly),
        *summarize_interpretation(),
        *summarize_limitations(),
    ]
    return "\n".join(lines).rstrip() + "\n"


def create_run_dir() -> tuple[str, Path]:
    run_id = datetime.now(TIMEZONE).strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_id, run_dir


def write_latest_reports(concise_report: str, memo_report: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    CONCISE_REPORT_PATH.write_text(concise_report, encoding="utf-8")
    MEMO_REPORT_PATH.write_text(memo_report, encoding="utf-8")


def write_archived_run(
    run_id: str,
    run_dir: Path,
    concise_report: str,
    memo_report: str,
    monthly: pd.DataFrame,
    quarterly: pd.DataFrame,
) -> None:
    concise_path = run_dir / "peacock_marketing_insights_concise.md"
    memo_path = run_dir / "peacock_marketing_insights_memo.md"
    manifest_path = run_dir / "run_manifest.json"

    concise_path.write_text(concise_report, encoding="utf-8")
    memo_path.write_text(memo_report, encoding="utf-8")
    manifest = {
        "run_id": run_id,
        "created_at_local": datetime.now(TIMEZONE).isoformat(timespec="seconds"),
        "timezone": str(TIMEZONE),
        "monthly_panel_rows": int(len(monthly)),
        "quarterly_panel_rows": int(len(quarterly)),
        "latest_outputs": {
            "concise_report": str(CONCISE_REPORT_PATH.relative_to(PROJECT_ROOT)),
            "memo_report": str(MEMO_REPORT_PATH.relative_to(PROJECT_ROOT)),
        },
        "archived_outputs": {
            "concise_report": str(concise_path.relative_to(PROJECT_ROOT)),
            "memo_report": str(memo_path.relative_to(PROJECT_ROOT)),
        },
        "source_panels": {
            "monthly": str(MONTHLY_PANEL.relative_to(PROJECT_ROOT)),
            "quarterly": str(QUARTERLY_PANEL.relative_to(PROJECT_ROOT)),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    monthly, quarterly = load_panels()
    concise_report = build_concise_report(monthly, quarterly)
    memo_report = build_memo_report(monthly, quarterly)
    run_id, run_dir = create_run_dir()
    write_latest_reports(concise_report, memo_report)
    write_archived_run(run_id, run_dir, concise_report, memo_report, monthly, quarterly)
    print(concise_report)
    print(f"Saved concise report to {CONCISE_REPORT_PATH}")
    print(f"Saved memo report to {MEMO_REPORT_PATH}")
    print(f"Archived run {run_id} to {run_dir}")


if __name__ == "__main__":
    main()
