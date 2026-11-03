# Case study: Analysing digital service performance

**Scope:** Synthetic data analysis across eight fictional business applications (20 October–3 November 2026).

## Question

Which services should be investigated first based on their error rates and incident records?

## Data and approach

- 120 daily performance records across eight services, with request volume, latency and error rates.
- 15 synthetic incident records, including three Payroll incidents adapted from a separate synthetic dataset.
- Pandas for loading, cleaning, filtering and service summaries; SQLite for querying incidents; Streamlit for charts and tables.

## Results

| Metric | Value |
|---|---:|
| Daily service records | 120 |
| Applications | 8 |
| Simulated requests | 2,509,454 |
| Request-weighted error rate | 0.275% |
| Incident records | 15 |
| Payroll P2 incidents | 3 |
| Payroll summed affected-user estimates | 12,801 |
| Payroll error rate, 3 Nov | 2.45% |
| Payroll threshold | 1.00% |
| Engineering PLM error rate, 3 Nov | 1.74% |
| Engineering threshold | 1.50% |

Payroll exceeded its defined threshold by **1.45 percentage points** and Engineering PLM by **0.24 percentage points** on 3 November. The Payroll incident records describe three P2 events; the sum of user-impact estimates does not represent unique people.

## Interpretation

Payroll and Engineering PLM are candidates for closer review because their final-day error rates exceeded the sample thresholds. However, incident records and daily measurements were generated separately. They should not be treated as evidence of a shared root cause or as real operational incidents.

## Recommended next steps

In a live environment, confirm the observation period, inspect logs, check dependencies, assess the number of distinct users affected and verify recovery before drawing a root-cause conclusion.

## Tools and limitations

**Tools:** Python, Pandas, SQLite/SQL, Streamlit, Plotly.

This project demonstrates CSV preparation, SQL filtering and aggregation, KPI reporting and interpretation of sample operational data. It is an exploratory dashboard, not a production monitoring system. All data is synthetic.
