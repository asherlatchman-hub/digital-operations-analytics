"""Data preparation and summary functions for the dashboard."""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent / "data"


def load_data():
    """Read our two CSV files and convert numbers/dates to useful types."""
    daily = pd.read_csv(DATA / "service_daily.csv", parse_dates=["date"])
    incidents = pd.read_csv(DATA / "incidents.csv", parse_dates=["opened_at"])

    # Cleaning: remove exact duplicate rows and discard incomplete essential records.
    daily = daily.drop_duplicates().dropna(subset=["date", "service", "requests"])
    incidents = incidents.drop_duplicates(subset=["incident_id"]).dropna(
        subset=["incident_id", "service", "opened_at"]
    )
    for column in ("requests", "users"):
        daily[column] = pd.to_numeric(daily[column], errors="coerce")
    for column in ("avg_latency_ms", "error_rate_pct", "error_slo_pct"):
        daily[column] = pd.to_numeric(daily[column], errors="coerce")
    incidents["affected_users"] = pd.to_numeric(
        incidents["affected_users"], errors="coerce"
    )
    incidents["priority_score"] = pd.to_numeric(
        incidents["priority_score"], errors="coerce"
    )
    return daily, incidents


def filter_dates(daily, incidents, start_date, end_date):
    """Filter both datasets to the same inclusive date range."""
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    d = daily.loc[daily["date"].between(start, end)].copy()
    i = incidents.loc[incidents["opened_at"].dt.normalize().between(start, end)].copy()
    return d, i


def weighted_error_rate(daily):
    """Total estimated failed requests / total requests, as a percent."""
    if daily.empty or daily["requests"].sum() == 0:
        return 0.0
    failed = (daily["error_rate_pct"] / 100 * daily["requests"]).sum()
    return float(100 * failed / daily["requests"].sum())


def service_summary(daily):
    """One easy-to-read row per service for the overview."""
    rows = []
    for service, group in daily.groupby("service"):
        latest = group.sort_values("date").iloc[-1]
        rows.append({
            "Service": service,
            "Requests": int(group["requests"].sum()),
            "Weighted error rate (%)": round(weighted_error_rate(group), 2),
            "Latest error rate (%)": float(latest["error_rate_pct"]),
            "SLO limit (%)": float(latest["error_slo_pct"]),
            "Latest status": "Review" if latest["error_rate_pct"] > latest["error_slo_pct"] else "Within limit",
        })
    return pd.DataFrame(rows).sort_values("Weighted error rate (%)", ascending=False)


def filter_incidents(incidents, service="All services", priorities=None):
    """Filter rows by one service and any selected incident priorities."""
    visible = incidents.copy()
    if service != "All services":
        visible = visible.loc[visible["service"] == service]
    if priorities is not None:
        visible = visible.loc[visible["priority"].isin(priorities)]
    return visible
