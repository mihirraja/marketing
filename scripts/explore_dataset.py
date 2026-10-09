"""Print first-pass EDA summaries for the Peacock marketing dataset."""

from __future__ import annotations

from load_data import load_all


def print_section(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> None:
    monthly, subscribers, events = load_all()

    print_section("Dataset Coverage")
    print(f"Monthly viewing observations: {len(monthly)}")
    print(f"Quarterly subscriber observations: {len(subscribers)}")
    print(f"Tentpole events: {len(events)}")
    print(
        "Monthly viewing period: "
        f"{monthly['period_month'].min().date()} to {monthly['period_month'].max().date()}"
    )
    print(
        "Subscriber period: "
        f"{subscribers['quarter_end_date'].min().date()} to "
        f"{subscribers['quarter_end_date'].max().date()}"
    )

    print_section("Peacock TV Share Observations")
    share = (
        monthly[monthly["metric_name"] == "share_of_total_tv_viewing"]
        .sort_values("metric_value", ascending=False)
        .loc[:, ["period_month", "metric_value", "related_tentpole_id", "reported_context"]]
    )
    for _, row in share.iterrows():
        print(
            f"{row['period_month']:%Y-%m}: {row['metric_value']:.1f}% "
            f"({row['related_tentpole_id']})"
        )

    print_section("Quarterly Subscribers")
    sub_cols = [
        "fiscal_quarter",
        "paid_subscribers_millions",
        "net_adds_millions",
        "related_tentpole_id",
    ]
    for _, row in subscribers.loc[:, sub_cols].iterrows():
        net_adds = row["net_adds_millions"]
        net_text = "not reported" if str(net_adds) == "nan" else f"{net_adds:g}M net adds"
        print(
            f"{row['fiscal_quarter']}: {row['paid_subscribers_millions']:g}M paid subs, "
            f"{net_text} ({row['related_tentpole_id']})"
        )

    print_section("Tentpole Mix")
    category_counts = events["event_category"].value_counts().sort_index()
    for category, count in category_counts.items():
        print(f"{category}: {count}")

    print_section("Source Publishers")
    publishers = sorted(
        set(monthly["source_publisher"])
        | set(subscribers["source_publisher"])
        | set(events["source_publisher"])
    )
    for publisher in publishers:
        print(publisher)


if __name__ == "__main__":
    main()

