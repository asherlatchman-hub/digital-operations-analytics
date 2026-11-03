"""Generate fictional daily service measurements for the operations analytics dashboard.

Run with: python generate_sample_data.py
Note: These measurements are deliberately fabricated for learning, not historical logs.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).parent / "data" / "service_daily.csv"
SERVICES = [
    ("Engineering PLM", "Engineering", 3200, 540, 1.5),
    ("Payroll & HR Portal", "HR", 8500, 280, 1.0),
    ("Identity Gateway (SSO)", "Identity & Access", 9000, 85, 1.0),
    ("Secure File Transfer", "IT Platform Services", 1800, 150, 1.0),
    ("Supply Chain ERP", "ERP Platform", 2500, 310, 1.5),
    ("Customer Support CRM", "Business Applications", 1200, 250, 1.5),
    ("Test Data Lake", "Data Platform", 400, 570, 2.0),
    ("IT Service Desk", "Service Management", 9000, 180, 1.5),
]


def generate():
    rng = random.Random(20261103)
    start = date(2026, 10, 20)
    rows = []
    for offset in range(15):
        day = start + timedelta(days=offset)
        for idx, (service, team, users, baseline_latency, error_slo) in enumerate(SERVICES):
            requests = int(2500 + users * 4 + rng.randint(-1000, 2400))
            latency = round(max(30, baseline_latency + rng.gauss(0, 22)), 1)
            error_rate = round(max(0.03, rng.gauss(0.24, 0.09)), 2)
            # Match the general incident timing, but NOT the exact peak telemetry.
            if service == "Payroll & HR Portal" and str(day) in {"2026-10-26", "2026-11-03"}:
                error_rate = 1.82 if str(day) == "2026-10-26" else 2.45
                requests = int(requests * 0.78)
                latency = round(latency * 0.88, 1)
            if service == "Engineering PLM" and str(day) == "2026-11-03":
                error_rate = 1.74
            rows.append({
                "date": day.isoformat(),
                "service": service,
                "team": team,
                "users": users,
                "requests": requests,
                "avg_latency_ms": latency,
                "error_rate_pct": error_rate,
                "error_slo_pct": error_slo,
            })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = generate()
    print(f"Wrote {len(rows)} entirely simulated measurements to {OUT}")
