"""Create first-pass charts for the Peacock marketing dataset."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from load_data import PROJECT_ROOT, load_all


OUTPUT_DIR = PROJECT_ROOT / "outputs"


def main() -> None:
    monthly, subscribers, _events = load_all()
    OUTPUT_DIR.mkdir(exist_ok=True)

    share = (
        monthly[monthly["metric_name"] == "share_of_total_tv_viewing"]
        .sort_values("period_month")
        .copy()
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(share["period_month"], share["metric_value"], marker="o", linewidth=2)
    ax.set_title("Peacock Share of Total TV Viewing")
    ax.set_xlabel("Month")
    ax.set_ylabel("Share of total TV viewing (%)")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "peacock_tv_share.png", dpi=160)
    plt.close(fig)

    subs = subscribers.sort_values("quarter_end_date").copy()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        subs["quarter_end_date"],
        subs["paid_subscribers_millions"],
        marker="o",
        linewidth=2,
        color="#1261A0",
    )
    ax.set_title("Peacock Paid Subscribers")
    ax.set_xlabel("Quarter end")
    ax.set_ylabel("Paid subscribers (millions)")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "peacock_paid_subscribers.png", dpi=160)
    plt.close(fig)

    print(f"Saved charts to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

