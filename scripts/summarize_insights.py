"""Summarize first-pass marketing insights from the Peacock analysis panels."""

from __future__ import annotations

import pandas as pd

from load_data import PROJECT_ROOT


ANALYSIS_DIR = PROJECT_ROOT / "analysis"
MONTHLY_PANEL = ANALYSIS_DIR / "monthly_peacock_panel.csv"
QUARTERLY_PANEL = ANALYSIS_DIR / "quarterly_subscriber_panel.csv"


def format_bool(value: object) -> str:
    return "yes" if bool(value) else "no"


def print_section(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def load_panels() -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly = pd.read_csv(MONTHLY_PANEL, parse_dates=["period_month"])
    quarterly = pd.read_csv(QUARTERLY_PANEL, parse_dates=["quarter_end_date"])
    return monthly, quarterly


def summarize_top_viewing_months(monthly: pd.DataFrame) -> None:
    print_section("Top Peacock TV Share Months")
    top_months = monthly.sort_values(
        "share_of_total_tv_viewing", ascending=False
    ).head(5)

    for _, row in top_months.iterrows():
        categories = []
        if row["has_sports_tentpole"]:
            categories.append("Sports")
        if row["has_entertainment_tentpole"]:
            categories.append("Entertainment")
        if row["has_mixed_tentpole"]:
            categories.append("Mixed")
        category_text = " + ".join(categories) if categories else "No mapped tentpole"
        print(
            f"{row['period_month']:%Y-%m}: "
            f"{row['share_of_total_tv_viewing']:.1f}% TV share "
            f"({category_text})"
        )


def summarize_tentpole_patterns(monthly: pd.DataFrame) -> None:
    print_section("Tentpole Pattern")
    flag_cols = [
        ("Sports", "has_sports_tentpole"),
        ("Entertainment", "has_entertainment_tentpole"),
        ("Mixed", "has_mixed_tentpole"),
    ]

    for label, column in flag_cols:
        subset = monthly[monthly[column]]
        if subset.empty:
            print(f"{label}: no observed months")
            continue
        avg_share = subset["share_of_total_tv_viewing"].mean()
        max_share = subset["share_of_total_tv_viewing"].max()
        print(
            f"{label}: {len(subset)} observed months, "
            f"average TV share {avg_share:.2f}%, max {max_share:.1f}%"
        )

    both = monthly[
        monthly["has_sports_tentpole"] & monthly["has_entertainment_tentpole"]
    ]
    if not both.empty:
        months = ", ".join(both["period_month"].dt.strftime("%Y-%m"))
        print(f"Sports + Entertainment overlap months: {months}")


def summarize_subscribers(quarterly: pd.DataFrame) -> None:
    print_section("Quarterly Subscriber Movement")
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

    for _, row in display.iterrows():
        net_adds = row["net_adds_millions"]
        reported_net = "not reported" if pd.isna(net_adds) else f"{net_adds:g}M"
        calculated = row["calculated_sequential_change_millions"]
        calculated_text = "n.a." if pd.isna(calculated) else f"{calculated:g}M"
        print(
            f"{row['fiscal_quarter']}: "
            f"{row['paid_subscribers_millions']:g}M paid subs, "
            f"reported net adds {reported_net}, "
            f"sequential change {calculated_text}, "
            f"sports={format_bool(row['has_sports_tentpole'])}, "
            f"entertainment={format_bool(row['has_entertainment_tentpole'])}, "
            f"mixed={format_bool(row['has_mixed_tentpole'])}"
        )


def summarize_takeaways(monthly: pd.DataFrame, quarterly: pd.DataFrame) -> None:
    print_section("Early Takeaways")
    top_month = monthly.sort_values(
        "share_of_total_tv_viewing", ascending=False
    ).iloc[0]
    strongest_sub_quarter = quarterly.sort_values(
        "net_adds_millions", ascending=False, na_position="last"
    ).iloc[0]

    print(
        f"1. The highest observed Peacock viewing month is "
        f"{top_month['period_month']:%Y-%m} at "
        f"{top_month['share_of_total_tv_viewing']:.1f}% TV share."
    )
    print(
        "2. Sports tentpoles dominate the largest TV-share observations, "
        "while Love Island adds repeatable summer entertainment lift."
    )
    print(
        f"3. The largest reported quarterly paid-subscriber gain in this panel is "
        f"{strongest_sub_quarter['fiscal_quarter']} with "
        f"{strongest_sub_quarter['net_adds_millions']:g}M net adds."
    )
    print(
        "4. Treat this as directional public-source analysis: Nielsen months and "
        "Comcast quarters are different grains, and missing public values are not estimated."
    )


def main() -> None:
    monthly, quarterly = load_panels()
    summarize_top_viewing_months(monthly)
    summarize_tentpole_patterns(monthly)
    summarize_subscribers(quarterly)
    summarize_takeaways(monthly, quarterly)


if __name__ == "__main__":
    main()

