# Peacock Marketing Analytics Dataset

Public-source Peacock marketing analytics dataset for 2024-2026.

This project keeps monthly Nielsen viewing observations separate from Comcast quarterly paid-subscriber observations. It does not interpolate monthly subscriber values.

## Structure

- `data/peacock_marketing_analytics_2024_2026_monthly_viewing.csv`
  Monthly Nielsen-reported Peacock viewing share, usage changes, and title-minute observations.
- `data/peacock_marketing_analytics_2024_2026_quarterly_subscribers.csv`
  Comcast-reported quarterly Peacock paid subscribers and net adds where reported.
- `data/peacock_marketing_analytics_2024_2026_tentpole_events.csv`
  Major Peacock sports, entertainment, mixed, and distribution tentpoles.
- `docs/peacock_marketing_analytics_2024_2026_data_dictionary.md`
  Field definitions, missing-value rules, and source method.
- `scripts/validate_dataset.py`
  Basic schema and relationship checks.

## Quick Start

Project Python interpreter:

```text
.venv/bin/python
```

Validate the dataset:

```bash
python3 scripts/validate_dataset.py
```

Or with the project virtual environment:

```bash
.venv/bin/python scripts/validate_dataset.py
```

Run the first EDA summary:

```bash
.venv/bin/python scripts/explore_dataset.py
```

Create first-pass charts:

```bash
.venv/bin/python scripts/make_charts.py
```

Build analysis-ready tables:

```bash
.venv/bin/python scripts/build_analysis_tables.py
```

This writes:

- `analysis/monthly_peacock_panel.csv`
- `analysis/quarterly_subscriber_panel.csv`

Load in Python:

```python
import pandas as pd
from pathlib import Path

root = Path(".")

monthly = pd.read_csv(root / "data/peacock_marketing_analytics_2024_2026_monthly_viewing.csv")
subs = pd.read_csv(root / "data/peacock_marketing_analytics_2024_2026_quarterly_subscribers.csv")
events = pd.read_csv(root / "data/peacock_marketing_analytics_2024_2026_tentpole_events.csv")
```

## Notes

- Blank numeric fields mean the cited public source did not report that value.
- `related_tentpole_id` can contain multiple semicolon-delimited event IDs.
- Subscriber rows are quarterly observations. Do not treat them as monthly subscriber estimates.
