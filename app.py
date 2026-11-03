"""Streamlit dashboard for simulated IT service analysis."""
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from analysis import filter_dates, filter_incidents, load_data, service_summary, weighted_error_rate

st.set_page_config(
    page_title="Digital Operations | Analytics",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
  .block-container { padding-top: 2rem; max-width: 1320px; }
  h1, h2, h3 { letter-spacing: -0.025em; }
  div[data-testid="stMetric"] { background: #152033; border: 1px solid #2c3d52;
     border-radius: 12px; padding: 17px 18px; }
  div[data-testid="stMetricLabel"] { color: #a6bacf; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_data()

DAILY, INCIDENTS = get_data()

st.sidebar.title("DIGITAL OPS")
st.sidebar.caption("Service performance and incidents")
page = st.sidebar.radio(
    "Navigate", ["Overview", "Service health", "Analytics", "SQL explorer"]
)
st.sidebar.divider()
first_day = DAILY["date"].min().date()
last_day = DAILY["date"].max().date()
range_value = st.sidebar.date_input(
    "Reporting dates", value=(first_day, last_day), min_value=first_day, max_value=last_day
)
if not isinstance(range_value, tuple) or len(range_value) != 2:
    st.info("Choose a start date and an end date to continue.")
    st.stop()
start_date, end_date = range_value
D, I = filter_dates(DAILY, INCIDENTS, start_date, end_date)

st.title("Digital Operations Analytics")
st.caption("Analyse service performance and incident trends using synthetic sample data.")

if D.empty:
    st.warning("There are no measurements in the selected period.")
    st.stop()

if page == "Overview":
    st.subheader("Operations at a glance")
    cols = st.columns(4)
    cols[0].metric("Total requests", f"{int(D['requests'].sum()):,}")
    cols[1].metric("Weighted error rate", f"{weighted_error_rate(D):.2f}%")
    cols[2].metric("Incidents recorded", f"{len(I):,}")
    cols[3].metric("Summed affected-user estimates", f"{int(I['affected_users'].sum()):,}")
    st.caption("Affected-user estimates may count the same person more than once. Daily error rates are sample averages, not peak incident error rates.")

    st.subheader("Service health summary")
    st.dataframe(service_summary(D), use_container_width=True, hide_index=True)
    left, right = st.columns([1.4, 1])
    with left:
        totals = D.groupby("date", as_index=False)["requests"].sum()
        fig = px.line(totals, x="date", y="requests", markers=True,
                      title="Daily request volume", labels={"date": "Day", "requests": "Requests"})
        st.plotly_chart(fig, use_container_width=True)
    with right:
        counts = I.groupby("priority").size().reset_index(name="incidents")
        if counts.empty:
            st.info("No incidents in this reporting range.")
        else:
            fig = px.bar(counts, x="priority", y="incidents", title="Incidents by priority",
                         labels={"priority": "Priority", "incidents": "Incidents"})
            st.plotly_chart(fig, use_container_width=True)
    st.subheader("Recent incidents")
    view = I.sort_values("opened_at", ascending=False).head(8)
    st.dataframe(view[["incident_id", "service", "opened_at", "priority", "status", "issue_type"]],
                 use_container_width=True, hide_index=True)

elif page == "Service health":
    st.subheader("Explore a service")
    service = st.selectbox("Application", sorted(D["service"].unique()))
    one = D[D["service"] == service].sort_values("date")
    latest = one.iloc[-1]
    a, b, c = st.columns(3)
    a.metric("Requests (selected dates)", f"{one['requests'].sum():,}")
    b.metric("Latest daily error rate", f"{latest['error_rate_pct']:.2f}%")
    c.metric("Latest daily latency", f"{latest['avg_latency_ms']:.0f} ms")
    fig = px.line(one, x="date", y="error_rate_pct", markers=True, title="Daily average error rate (%)")
    fig.add_hline(y=float(latest["error_slo_pct"]), line_dash="dash",
                  annotation_text="Configured error-rate SLO limit")
    st.plotly_chart(fig, use_container_width=True)
    left, right = st.columns(2)
    with left:
        fig = px.line(one, x="date", y="avg_latency_ms", markers=True, title="Daily average latency (ms)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.line(one, x="date", y="requests", markers=True, title="Daily request count")
        st.plotly_chart(fig, use_container_width=True)
    st.info("These are daily synthetic measurements. You can observe associations, but these charts do not prove a technical root cause.")
    st.subheader("Related incidents")
    related = I[I["service"] == service]
    if related.empty:
        st.write("No incident records for this service in the selected range.")
    else:
        st.dataframe(related[["incident_id", "opened_at", "priority", "status", "affected_users", "summary"]],
                     use_container_width=True, hide_index=True)

elif page == "Analytics":
    st.subheader("Compare services and incidents")
    # Filter incident records by the selected application.
    services = ["All services"] + sorted(I["service"].unique().tolist())
    chosen_service = st.selectbox("Filter application", services)
    selected_incidents = filter_incidents(I, service=chosen_service)
    totals = selected_incidents.groupby("service", as_index=False).agg(
        incident_count=("incident_id", "count"),
        summed_user_estimate=("affected_users", "sum")
    ).sort_values("incident_count", ascending=False)
    left, right = st.columns(2)
    if totals.empty:
        st.info("No incident records for this period.")
    else:
        with left:
            fig = px.bar(totals, x="incident_count", y="service", orientation="h",
                         title="Recorded incidents by service")
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.bar(totals, x="summed_user_estimate", y="service", orientation="h",
                         title="Summed estimated affected-user counts")
            st.plotly_chart(fig, use_container_width=True)
    st.subheader("Incident records")
    priority = st.multiselect("Filter priority", ["P1", "P2", "P3", "P4"], default=["P1", "P2", "P3", "P4"])
    visible = filter_incidents(selected_incidents, priorities=priority)
    st.caption(f"Showing {len(visible)} incident(s) for selected filters.")
    st.dataframe(visible.sort_values("opened_at", ascending=False), use_container_width=True, hide_index=True)
    st.download_button("Download filtered incidents as CSV", data=visible.to_csv(index=False),
                       file_name="incident_analysis.csv", mime="text/csv")
    with st.expander("What do these numbers mean?"):
        st.markdown("""
        - **Error rate:** the share of requests that returned an error, expressed as a percentage.
        - **Latency:** how long a response took, averaged across the simulated day.
        - **SLO:** service-level objective, the target used to evaluate service performance.
        - **Affected-user estimates:** estimates by incident, which can overlap across incidents.
        - **Weighted error rate:** total estimated errors divided by total requests, rather than a simple average of percentages.
        """)

else:  # SQL explorer — basic SQL, real SQLite database, read-only queries
    st.subheader("SQL explorer")
    st.write("Run simple SQL queries against the same two tables used by this dashboard.")
    examples = {
        "1 · View a few incidents": "SELECT incident_id, service, priority, status\nFROM incidents\nLIMIT 10;",
        "2 · Filter urgent incidents": "SELECT incident_id, service, priority, affected_users\nFROM incidents\nWHERE priority IN ('P1', 'P2')\nORDER BY affected_users DESC;",
        "3 · Count incidents per service": "SELECT service, COUNT(*) AS incident_count\nFROM incidents\nGROUP BY service\nORDER BY incident_count DESC;",
        "4 · Payroll investigation": "SELECT incident_id, opened_at, priority, status, affected_users\nFROM incidents\nWHERE service = 'Payroll & HR Portal'\nORDER BY opened_at;",
        "5 · Join incidents with daily data": "SELECT i.incident_id, i.service, d.date, d.error_rate_pct\nFROM incidents AS i\nJOIN service_daily AS d\n  ON i.service = d.service\n AND substr(i.opened_at, 1, 10) = d.date\nORDER BY i.opened_at DESC;",
    }
    chosen = st.selectbox("Start with an example", list(examples))
    sql = st.text_area("SQL query — you can edit this", examples[chosen], height=180, key=f"sql_{chosen}")
    if st.button("Run query", type="primary"):
        try:
            statement = sql.strip()
            # Restrict the query interface to a single SELECT statement.
            if not statement.lower().startswith("select"):
                st.error("Only SELECT queries are supported.")
            elif ";" in statement.rstrip(";"):
                st.error("Run one SELECT query at a time.")
            else:
                with sqlite3.connect(":memory:") as conn:
                    # SQLite cannot store a pandas datetime directly as needed for joins,
                    # so convert it to simple ISO strings before loading it.
                    sql_daily = D.copy()
                    sql_daily["date"] = sql_daily["date"].dt.strftime("%Y-%m-%d")
                    sql_incidents = I.copy()
                    sql_incidents["opened_at"] = sql_incidents["opened_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
                    sql_daily.to_sql("service_daily", conn, index=False, if_exists="replace")
                    sql_incidents.to_sql("incidents", conn, index=False, if_exists="replace")
                    conn.execute("PRAGMA query_only = ON")
                    result = pd.read_sql_query(statement, conn)
                st.success(f"Query returned {len(result)} row(s).")
                st.dataframe(result, use_container_width=True, hide_index=True)
        except (sqlite3.Error, pd.errors.DatabaseError, ValueError) as exc:
            st.error(f"Query error: {exc}")
    with st.expander("Tables and columns"):
        st.code("service_daily: date, service, team, users, requests, avg_latency_ms, error_rate_pct, error_slo_pct\nincidents: incident_id, service, opened_at, priority, status, affected_users, priority_score, issue_type, summary, record_origin")
    st.caption("Queries use only the currently selected dates. This practice database is rebuilt in memory whenever you run a query; your files are not changed.")

st.divider()
st.caption("Exploratory dashboard · Synthetic data · No live system connection")
