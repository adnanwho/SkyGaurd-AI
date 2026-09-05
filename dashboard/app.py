from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.skyguard.evaluation.runner import run_evaluation
from src.skyguard.engine import SkyGuardEngine
from src.skyguard.replay.engine import replay
from src.skyguard.context.temporal import temporal_model_status
from src.skyguard.config import DEFAULT_CONFIG
from src.skyguard.utils.paths import resolve_project_path

st.set_page_config(page_title="SkyGuard AI", page_icon="⦿", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --ink:#17212b; --muted:#64727d; --line:#dfe5e8; --paper:#f4f7f6; --blue:#2563eb; --green:#16805b; --amber:#b45309; --red:#b42318; --purple:#7657a8; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
h1, h2, h3 { font-family:'Space Grotesk',sans-serif; letter-spacing:0; }
.stApp { background:var(--paper); }
.block-container { max-width:1500px; padding-top:1.5rem; }
.hero { display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid var(--line); padding:0 0 1.15rem; margin-bottom:1.25rem; }
.eyebrow, .section-label, .metric-label { color:var(--muted); font-size:.7rem; font-weight:700; letter-spacing:.11em; text-transform:uppercase; }
.hero h1 { font-size:2.35rem; margin:.2rem 0 0; }
.hero-note { color:var(--muted); text-align:right; font-size:.85rem; }
.panel { background:#fff; border:1px solid var(--line); border-radius:8px; padding:1rem 1.1rem; height:100%; }
.panel h3 { margin:.1rem 0 .7rem; }
.metric { background:#fff; border:1px solid var(--line); border-top:3px solid var(--blue); border-radius:7px; padding:.85rem 1rem; min-height:108px; }
.metric-value { font:700 1.8rem 'Space Grotesk',sans-serif; margin:.35rem 0 .15rem; }
.metric-note { color:var(--muted); font-size:.8rem; }
.badge { display:inline-block; padding:.2rem .48rem; border-radius:999px; font-size:.68rem; font-weight:700; letter-spacing:.05em; }
.healthy { color:#116149; background:#e5f5ee; } .warning { color:#8a4b09; background:#fff1d6; } .critical { color:#a31d16; background:#fee7e5; } .info { color:#1d4ed8; background:#e7efff; }
.issue { border-left:4px solid var(--amber); background:#fff; border-top:1px solid var(--line); border-right:1px solid var(--line); border-bottom:1px solid var(--line); border-radius:6px; padding:.8rem 1rem; margin:.45rem 0; }
.issue.critical { border-left-color:var(--red); } .issue.high { border-left-color:var(--amber); }
.muted { color:var(--muted); }
.stButton > button { border-radius:5px; }
</style>
""",
    unsafe_allow_html=True,
)

ROOT_CAUSE_LABELS = {"SPIKE": "Sudden spike", "FROZEN_STUCK": "Frozen sensor", "DRIFT_BIAS": "Sensor drift", "COMMUNICATION_MISSING": "Missing communication", "UNKNOWN": "Needs review", "NONE": "No fault assigned"}
EVENT_LABELS = {"SENSOR_FAULT": "Likely sensor fault", "WEATHER_EVENT": "Likely weather event", "UNCERTAIN": "Needs review", "NORMAL": "Normal"}
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}


@st.cache_data(show_spinner=False)
def analyze(data: pd.DataFrame) -> pd.DataFrame:
    return SkyGuardEngine().process(data).observations.copy()


@st.cache_data(show_spinner=False)
def load_bundled_results() -> pd.DataFrame:
    results = pd.read_csv(resolve_project_path(DEFAULT_CONFIG.paths.bundled_results))
    results["timestamp"] = pd.to_datetime(results["timestamp"])
    return results


def numeric(row: pd.Series, key: str, digits: int = 1, suffix: str = "") -> str:
    value = pd.to_numeric(row.get(key), errors="coerce")
    return f"{value:.{digits}f}{suffix}" if pd.notna(value) else "Unavailable"


def metric_card(label: str, value: str, note: str, color: str = "#2563eb") -> None:
    st.markdown(f'<div class="metric" style="border-top-color:{color}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)


def status_badge(status: str) -> str:
    value = str(status or "UNKNOWN").upper()
    tone = "healthy" if value in {"HEALTHY", "NORMAL", "OPERATIONAL"} else "critical" if value in {"CRITICAL", "HIGH"} else "warning" if value in {"WARNING", "DEGRADING", "MEDIUM"} else "info"
    return f'<span class="badge {tone}">{value.replace("_", " ")}</span>'


def issue_card(row: pd.Series) -> None:
    severity = str(row.get("severity", row.get("Anomaly_Severity", "UNKNOWN"))).upper()
    cause = ROOT_CAUSE_LABELS.get(str(row.get("root_cause", "UNKNOWN")), str(row.get("root_cause", "UNKNOWN")))
    event = EVENT_LABELS.get(str(row.get("event_type", "UNCERTAIN")), str(row.get("event_type", "UNCERTAIN")))
    timestamp = pd.Timestamp(row["timestamp"]).strftime("%d %b %H:%M")
    st.markdown(f'<div class="issue {severity.lower()}"><b>{severity}</b> &nbsp; {cause}<br><strong>{row["station_id"]}</strong> · {timestamp}<br><span class="muted">{event} · confidence {float(row.get("confidence", 0)):.0%} · {row.get("explanation", "No explanation available.")}</span></div>', unsafe_allow_html=True)


def evidence_chart(row: pd.Series) -> None:
    values = {
        "QC rules": int(bool(row.get("qc_failed", False))) * 100,
        "Isolation Forest": float(row.get("IF_Score", 0) or 0) * 100,
        "ECOD": float(row.get("ECOD_Score", 0) or 0) * 100,
        "COPOD": float(row.get("COPOD_Score", 0) or 0) * 100,
        "HBOS": float(row.get("HBOS_Score", 0) or 0) * 100,
    }
    frame = pd.DataFrame({"Evidence": list(values), "Strength": list(values.values())})
    fig = px.bar(frame, x="Strength", y="Evidence", orientation="h", height=220, color="Strength", color_continuous_scale=["#cfe2ff", "#2563eb"])
    fig.update_layout(margin=dict(l=0, r=0, t=5, b=5), coloraxis_showscale=False, xaxis_title=None, yaxis_title=None, xaxis_range=[0, max(100, frame.Strength.max() + 5)])
    st.plotly_chart(fig, use_container_width=True)


def dashboard_page(filtered: pd.DataFrame) -> None:
    anomaly_column = "Final_Anomaly" if "Final_Anomaly" in filtered else "Ensemble_Anomaly"
    anomalies = filtered[filtered[anomaly_column].fillna(0).astype(int).eq(1)].copy()
    anomalies["_order"] = anomalies["severity"].map(SEVERITY_ORDER).fillna(4)
    anomalies = anomalies.sort_values(["_order", "confidence", "timestamp"], ascending=[True, False, False])
    latest = filtered.sort_values("timestamp").groupby("station_id", as_index=False).tail(1) if not filtered.empty else filtered
    health = float(latest["health_score"].mean()) if not latest.empty else 0
    confidence = float(anomalies["confidence"].mean()) if not anomalies.empty else float(filtered.get("confidence", pd.Series([0])).mean())
    metric_cols = st.columns(5)
    with metric_cols[0]: metric_card("Stations", f"{filtered['station_id'].nunique()}", "Connected in selection", "#16805b")
    with metric_cols[1]: metric_card("Observations", f"{len(filtered):,}", "Processed readings", "#2563eb")
    with metric_cols[2]: metric_card("Anomalies", f"{len(anomalies):,}", f"{len(anomalies) / max(len(filtered), 1):.2%} of data", "#b45309")
    with metric_cols[3]: metric_card("Station health", f"{health:.0f}%", "Latest average", "#16805b")
    with metric_cols[4]: metric_card("Model confidence", f"{confidence:.0%}", "Average active evidence", "#7657a8")
    st.markdown("### What needs attention?")
    left, right = st.columns([1.25, 1])
    with left:
        if anomalies.empty: st.success("Everything looks normal. No active anomalies were detected in this selection.")
        else:
            for _, row in anomalies.head(5).iterrows(): issue_card(row)
            if len(anomalies) > 5: st.caption(f"Showing 5 of {len(anomalies):,} active anomalies. Use Anomalies for the full queue.")
    with right:
        st.markdown('<div class="panel"><h3>System pulse</h3>', unsafe_allow_html=True)
        health_frame = filtered.sort_values("timestamp")[["timestamp", "station_id", "health_score"]]
        fig = px.line(health_frame, x="timestamp", y="health_score", color="station_id", height=260)
        fig.update_layout(margin=dict(l=0, r=0, t=5, b=0), yaxis_range=[0, 100], xaxis_title=None, yaxis_title="Health")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("### Station overview")
    station_rows = []
    for _, row in latest.iterrows():
        count = int(anomalies["station_id"].eq(row["station_id"]).sum())
        station_rows.append({"Station": row["station_id"], "Status": str(row.get("health_status", "UNKNOWN")), "Health": f"{float(row.get('health_score', 0)):.0f}%", "Temperature": numeric(row, "temperature", 1, "°C"), "Humidity": numeric(row, "humidity", 0, "%"), "Pressure": numeric(row, "pressure", 0, " hPa"), "Active anomalies": count, "Last update": pd.Timestamp(row["timestamp"]).strftime("%d %b %H:%M")})
    st.dataframe(pd.DataFrame(station_rows), use_container_width=True, hide_index=True)


def station_page(filtered: pd.DataFrame, station: str) -> None:
    station_data = filtered[filtered["station_id"].eq(station)].sort_values("timestamp")
    if station_data.empty: st.info("No observations are available for this station."); return
    latest = station_data.iloc[-1]
    st.title(f"{station} station")
    st.markdown(f"{status_badge(latest.get('health_status', 'UNKNOWN'))} &nbsp; Health {numeric(latest, 'health_score', 0, '%')} &nbsp; Last update {pd.Timestamp(latest['timestamp']).strftime('%d %b %Y, %H:%M')}", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a: metric_card("Temperature", numeric(latest, "temperature", 1, "°C"), "Latest reading")
    with b: metric_card("Humidity", numeric(latest, "humidity", 0, "%"), "Latest reading", "#16805b")
    with c: metric_card("Pressure", numeric(latest, "pressure", 0, " hPa"), "Latest reading", "#7657a8")
    window = st.select_slider("Trend window", options=["1 hour", "6 hours", "24 hours", "7 days"], value="24 hours")
    hours = {"1 hour": 1, "6 hours": 6, "24 hours": 24, "7 days": 168}[window]
    trend = station_data[station_data["timestamp"] >= station_data["timestamp"].max() - pd.Timedelta(hours=hours)]
    for variable, label, color in [("temperature", "Temperature (°C)", "#b45309"), ("humidity", "Humidity (%)", "#16805b"), ("pressure", "Pressure (hPa)", "#2563eb")]:
        fig = px.line(trend, x="timestamp", y=variable, height=230, color_discrete_sequence=[color], title=label)
        marked = trend[trend.get("Final_Anomaly", pd.Series(0, index=trend.index)).fillna(0).astype(int).eq(1)]
        if not marked.empty: fig.add_scatter(x=marked["timestamp"], y=marked[variable], mode="markers", name="Anomaly", marker=dict(color="#b42318", size=9))
        fig.update_layout(margin=dict(l=0, r=0, t=35, b=0), showlegend=False, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)


def anomalies_page(filtered: pd.DataFrame) -> None:
    st.title("Anomaly investigation")
    source = filtered[filtered["Final_Anomaly"].fillna(0).astype(int).eq(1)].copy()
    if source.empty: st.success("Everything looks normal in the selected range."); return
    a, b, c, d = st.columns(4)
    with a: station = st.selectbox("Station", ["All stations", *sorted(source.station_id.unique())])
    with b: severity = st.multiselect("Severity", sorted(source.severity.dropna().unique()), default=[])
    with c: cause = st.multiselect("Root cause", sorted(source.root_cause.dropna().unique()), default=[])
    with d: event = st.multiselect("Diagnosis", sorted(source.event_type.dropna().unique()), default=[])
    if station != "All stations": source = source[source.station_id.eq(station)]
    if severity: source = source[source.severity.isin(severity)]
    if cause: source = source[source.root_cause.isin(cause)]
    if event: source = source[source.event_type.isin(event)]
    source = source.sort_values("timestamp", ascending=False)
    view = source[["timestamp", "station_id", "temperature", "severity", "confidence", "root_cause", "event_type", "explanation"]].copy()
    view.columns = ["Time", "Station", "Temperature", "Severity", "Confidence", "Cause", "Diagnosis", "Explanation"]
    view["Time"] = view["Time"].dt.strftime("%d %b %H:%M"); view["Confidence"] = view["Confidence"].map(lambda value: f"{value:.0%}")
    st.dataframe(view, use_container_width=True, hide_index=True)
    selected = st.selectbox("Open anomaly", source.index, format_func=lambda index: f"{source.loc[index, 'station_id']} · {pd.Timestamp(source.loc[index, 'timestamp']).strftime('%d %b %H:%M')} · {source.loc[index, 'root_cause']}")
    investigation_view(source.loc[selected])


def investigation_view(row: pd.Series) -> None:
    st.markdown("### What happened?")
    st.info(str(row.get("explanation", "No explanation is available for this observation.")))
    a, b, c, d = st.columns(4)
    with a: metric_card("Observed temperature", numeric(row, "temperature", 1, "°C"), "Recorded value", "#b45309")
    with b: metric_card("Recent baseline", numeric(row, "regional_temperature", 1, "°C"), "Regional reference", "#2563eb")
    with c: metric_card("Model agreement", f"{int(row.get('Model_Agreement', 0))}/4", "Detectors agreeing", "#7657a8")
    with d: metric_card("Confidence", f"{float(row.get('confidence', 0)):.0%}", "Evidence strength", "#16805b")
    left, right = st.columns(2)
    with left:
        st.markdown("### Event classification")
        st.markdown(f"{status_badge(row.get('event_type', 'UNCERTAIN'))} &nbsp; {EVENT_LABELS.get(str(row.get('event_type')), 'Needs review')}", unsafe_allow_html=True)
        st.write(str(row.get("spatial_evidence", "Spatial evidence unavailable.")))
        st.markdown("### QC evidence")
        st.code(str(row.get("qc_flags", "No failed QC rules recorded.")), language="text")
    with right:
        st.markdown("### Why was this flagged?")
        evidence_chart(row)
        st.markdown("### AI explanation")
        st.write(f"Top contributing feature: **{row.get('SHAP_Top_Feature', 'Unavailable')}**")
        st.caption(str(row.get("SHAP_Note", "Feature contribution is not causal proof.")))
    st.markdown("### Recommended action")
    st.warning(str(row.get("maintenance_recommendation", "No recommendation available.")))
    st.markdown(f"### Recovery status: {str(row.get('recovery_status', 'NOT_AVAILABLE')).replace('_', ' ').title()}")
    st.caption(str(row.get("recovery_reason", "No recovery action is required.")))


def health_page(filtered: pd.DataFrame) -> None:
    st.title("Sensor health")
    latest = filtered.sort_values("timestamp").groupby("station_id", as_index=False).tail(1)
    for _, row in latest.iterrows():
        st.markdown(f"### {row['station_id']} &nbsp; {status_badge(row.get('health_status', 'UNKNOWN'))}", unsafe_allow_html=True)
        cols = st.columns(5)
        values = [("Overall", row.get("health_score", 0)), ("Temperature sensor", row.get("health_score", 0)), ("Humidity sensor", row.get("health_score", 0)), ("Pressure sensor", row.get("health_score", 0)), ("Communication", 100 if not bool(row.get("missing_fail", False)) else 0)]
        for col, (label, value) in zip(cols, values):
            with col: st.progress(max(0, min(100, int(float(value)))), text=f"{label}: {float(value):.0f}%")
        st.caption(str(row.get("maintenance_recommendation", "No action required.")))


def evaluation_page() -> None:
    st.title("Evaluation")
    report_path = resolve_project_path(DEFAULT_CONFIG.paths.evaluation_dir / "latest.csv")
    if st.button("Run evaluation", type="primary"):
        with st.spinner("Running reproducible evaluation scenarios..."): st.session_state["evaluation"] = run_evaluation()
    summary = st.session_state.get("evaluation")
    if summary is None and report_path.exists():
        try:
            report = pd.read_csv(report_path)
            summary = evaluation_metrics(report)
        except (OSError, ValueError): summary = None
    if not summary: st.info("Run the evaluation to generate measured model metrics."); return
    cols = st.columns(5)
    for col, label, key in zip(cols, ["Precision", "Recall", "F1", "False positive rate", "Weather event recall"], ["precision", "recall", "f1", "false_positive_rate", "weather_event_recall"]):
        with col: metric_card(label, f"{float(summary.get(key, 0)):.1%}", "Measured evaluation result", "#7657a8")
    st.markdown("### What does this mean?")
    st.info("Precision is how often flagged anomalies were confirmed by the injected evaluation scenarios. Recall is how many injected anomalies were found.")


def evaluation_metrics(report: pd.DataFrame) -> dict:
    truth = report.get("ground_truth", pd.Series("NORMAL", index=report.index)).ne("NORMAL")
    predicted = report.get("Final_Anomaly", report.get("Ensemble_Anomaly", pd.Series(0, index=report.index))).astype(bool)
    tp, fp, fn, tn = int((predicted & truth).sum()), int((predicted & ~truth).sum()), int((~predicted & truth).sum()), int((~predicted & ~truth).sum())
    precision = tp / max(tp + fp, 1); recall = tp / max(tp + fn, 1)
    weather = report.get("ground_truth", pd.Series(index=report.index)).eq("WEATHER_EVENT")
    return {"precision": precision, "recall": recall, "f1": 2 * precision * recall / max(precision + recall, 1e-9), "false_positive_rate": fp / max(fp + tn, 1), "weather_event_recall": int((predicted & weather).sum()) / max(int(weather.sum()), 1)}


def replay_page(filtered: pd.DataFrame) -> None:
    st.title("Replay a historical scenario")
    station = st.selectbox("Station", ["All stations", *sorted(filtered.station_id.unique())])
    count = st.select_slider("Observations", options=[10, 20, 40, 80], value=40)
    subset = filtered if station == "All stations" else filtered[filtered.station_id.eq(station)]
    if st.button("Start replay", type="primary"):
        rows = list(replay(subset[["station_id", "timestamp", "temperature", "pressure", "humidity"]].head(count)))
        frame = pd.DataFrame([{"Position": item.position, "Replay time": item.timestamp, "Latency (ms)": item.processing_ms, "Status": item.result.get("event_type", "WARMUP")} for item in rows])
        st.dataframe(frame, use_container_width=True, hide_index=True)
        if rows: st.success(f"Replay complete. Average latency: {frame['Latency (ms)'].mean():.2f} ms per observation.")


def main() -> None:
    with st.sidebar:
        st.markdown("## ⦿ SkyGuard AI")
        st.caption("Automated weather station intelligence")
        page = st.radio("Navigate", ["Dashboard", "Stations", "Anomalies", "Sensor Health", "Evaluation", "Replay", "Data source", "Settings / About"], label_visibility="collapsed")
        st.divider(); st.markdown(f"**System status**  {status_badge('Operational')}", unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload observation CSV", type="csv")
        use_existing = st.checkbox("Use bundled results", value=uploaded is None)
    if uploaded is not None:
        try:
            with st.spinner("Running quality checks and anomaly models..."): results = analyze(pd.read_csv(uploaded))
        except (ValueError, KeyError, OSError) as error:
            st.error("Unable to process dataset. Check that it contains station_id, timestamp, temperature, pressure, and humidity.")
            with st.expander("Technical details"): st.code(str(error))
            return
    elif use_existing: results = load_bundled_results()
    else: st.info("Choose a CSV from Data source to begin."); return
    results["timestamp"] = pd.to_datetime(results["timestamp"])
    stations = sorted(results["station_id"].dropna().unique())
    with st.sidebar: selected_station = st.selectbox("Station scope", ["All stations", *stations])
    filtered = results if selected_station == "All stations" else results[results["station_id"].eq(selected_station)]
    st.markdown('<div class="hero"><div><div class="eyebrow">Automated weather station intelligence</div><h1>SkyGuard AI</h1></div><div class="hero-note">System operational<br>Last updated: ' + pd.Timestamp(results["timestamp"].max()).strftime("%d %b %Y, %H:%M") + '</div></div>', unsafe_allow_html=True)
    if page == "Dashboard": dashboard_page(filtered)
    elif page == "Stations": station_page(results, st.selectbox("Open station", stations))
    elif page == "Anomalies": anomalies_page(filtered)
    elif page == "Sensor Health": health_page(filtered)
    elif page == "Evaluation": evaluation_page()
    elif page == "Replay": replay_page(filtered)
    elif page == "Data source":
        st.title("Data source"); st.write(f"{len(results):,} observations across {results.station_id.nunique()} stations.")
        st.dataframe(results[["station_id", "timestamp", "temperature", "pressure", "humidity"]].head(20), use_container_width=True, hide_index=True)
    else:
        st.title("Settings / About"); st.info("SkyGuard combines deterministic QC, ensemble anomaly detection, temporal and spatial evidence, diagnosis, explanations, station health, maintenance recommendations, and recovery review.")
        st.write(f"Temporal model: {temporal_model_status().message}")


if __name__ == "__main__":
    main()
