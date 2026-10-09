# Peacock Marketing Analytics Dataset, 2024-2026

Created: 2026-10-06

This dataset is a first-pass reproducible public-source panel for Peacock marketing analytics. It intentionally keeps monthly Nielsen viewing metrics separate from Comcast quarterly paid-subscriber observations. Monthly subscriber values are not interpolated.

## Files

- `peacock_marketing_analytics_2024_2026_monthly_viewing.csv`: Nielsen-reported Peacock monthly viewing, usage, and title-minute observations.
- `peacock_marketing_analytics_2024_2026_quarterly_subscribers.csv`: Comcast-reported quarterly Peacock paid-subscriber observations and net adds where reported.
- `peacock_marketing_analytics_2024_2026_tentpole_events.csv`: Major content, sports, and distribution tentpoles linked to viewing or subscriber rows through `tentpole_id`.

## Join Keys

- `related_tentpole_id` may contain one or more semicolon-delimited IDs from `peacock_marketing_analytics_2024_2026_tentpole_events.csv`.
- Use `period_month` for monthly time series work and `fiscal_quarter` / `quarter_end_date` for Comcast subscriber observations.
- Do not join quarterly subscribers to months as if they were monthly subscriber values.

## Missing Values

Blank numeric fields mean the source did not report that value in the cited observation.

Important examples:

- `net_adds_millions` is blank when Comcast reported an ending subscriber count but did not report quarterly net adds in the same source.
- `month_over_month_change_value` is blank when Nielsen did not report a month-over-month change for that metric.
- Subscriber values are rounded public company disclosures. Small quarter-to-quarter changes may be hidden by rounding.

## Core Fields

- `period_month`: Calendar month represented by the observation.
- `period_start`, `period_end`: Reported or inferred source measurement window. Nielsen Gauge months sometimes use measurement weeks rather than calendar months.
- `source_grain`: Source reporting grain, such as monthly, Nielsen measurement month, or quarter.
- `metric_name`: Normalized metric label, such as `share_of_total_tv_viewing`, `usage_change_mom`, or `title_viewing_minutes`.
- `metric_value`: Numeric value for the metric.
- `metric_unit`: Unit for `metric_value`, such as `percent`, `percentage_points`, or `billion_minutes`.
- `paid_subscribers_millions`: Comcast-reported Peacock paid subscribers in millions.
- `net_adds_millions`: Comcast-reported net additions in millions when reported; otherwise blank unless clearly derived from rounded sequential counts and noted.
- `event_category`: Broad marketing category: `Sports`, `Entertainment`, or `Mixed`.
- `source_quote_or_paraphrase`: Short source-grounded provenance note for auditability.
- `verification_status`: `verified_public_source` means the row is backed by the cited public source.

## Source Method

Sources were limited to authoritative public releases, filings, or official source pages from Nielsen, Comcast, NBCUniversal, and SEC-hosted Comcast filings. Third-party articles were not used as primary evidence in the delivered rows.

