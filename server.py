"""
SkyGuard AI - local live-analysis server.

A dependency-free HTTP backend (Python standard library only) that gives the
browser dashboard a genuine backend feed instead of only reading a static CSV:

  * serves the ``web/`` dashboard as static files,
  * ``GET  /api/data``    -> the current analysis results as JSON,
  * ``POST /api/refresh``  -> re-run the REAL SkyGuard pipeline on the source
                              dataset, rewrite the export, return fresh JSON.

The refresh cycle runs the actual ensemble pipeline
(``SkyGuardEngine.process`` -> ``run_pipeline``): the four detectors
(Isolation Forest, ECOD, COPOD, HBOS), QC rules, root cause, SHAP and sensor
health. No results are fabricated. This is an on-demand live-analysis feed
against a local dataset, not a real-time network stream.

This is the canonical-schema adaptation of the ``dashboard_server.py`` pattern
from the sibling SkyGuard project (which used the legacy ``src/`` layout and
legacy column names). Here it targets this repo's ``src/skyguard/`` package and
canonical columns (``station_id``, ``timestamp``, ``temperature`` ...).

Run::

    python server.py                 # http://127.0.0.1:8137
    python server.py --port 9000
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
WEB_ROOT = PROJECT_ROOT / "web"
EXPORT_FILE = PROJECT_ROOT / "outputs" / "exports" / "anomaly_detection_results.csv"
SOURCE_FILE = PROJECT_ROOT / "data" / "processed" / "SkyGuard_clean_3hourly.csv"

# View-model projection for the JSON API. The full export (~90 columns, 20 MB)
# stays on disk; the feed returns only the columns the web/ dashboard reads, so
# the live payload is lighter than the static CSV while producing identical UI
# behaviour. Keep this in sync with the fields accessed in web/app.js.
VIEW_COLUMNS = [
    "station_id", "timestamp", "temperature", "humidity", "pressure",
    "Final_Anomaly", "Final_Score", "Ensemble_Anomaly", "Ensemble_Score",
    "Model_Agreement", "severity", "Anomaly_Severity", "confidence",
    "IF_Anomaly", "ECOD_Anomaly", "COPOD_Anomaly", "HBOS_Anomaly",
    "qc_failed", "qc_flags", "health_status", "health_score",
    "maintenance_recommendation", "root_cause", "explanation",
    "SHAP_Available", "SHAP_Top_Feature", "SHAP_Top_Contribution", "SHAP_Note",
]


def _json_safe(value):
    """Coerce a single value into something ``json.dumps`` accepts."""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _rows_from_csv(path: Path) -> list[dict]:
    """Read a results CSV into JSON-safe row dictionaries (empty if missing).

    Only the ``VIEW_COLUMNS`` the dashboard consumes are returned, intersected
    with the columns actually present in the file.
    """
    if not path.exists():
        return []
    frame = pd.read_csv(path)
    keep = [column for column in VIEW_COLUMNS if column in frame.columns]
    if keep:
        frame = frame[keep]
    frame = frame.where(pd.notnull(frame), None)
    return [
        {key: _json_safe(value) for key, value in record.items()}
        for record in frame.to_dict(orient="records")
    ]


def data_payload(source: str = "stored") -> dict:
    """Build the ``/api/data`` payload from the current export on disk."""
    rows = _rows_from_csv(EXPORT_FILE)
    updated = None
    if EXPORT_FILE.exists():
        updated = datetime.fromtimestamp(
            EXPORT_FILE.stat().st_mtime, timezone.utc
        ).isoformat()
    return {
        "updated": updated,
        "count": len(rows),
        "source": source,
        "export": str(EXPORT_FILE.relative_to(PROJECT_ROOT)),
        "rows": rows,
    }


def run_refresh() -> dict:
    """Re-run the real pipeline on the source dataset and rewrite the export."""
    # Imported lazily so that merely serving static files / /api/data does not
    # pay the heavy ML import cost, and so an import failure surfaces as a clean
    # 500 on /api/refresh rather than crashing server startup.
    from src.skyguard.engine import SkyGuardEngine

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Source dataset not found: {SOURCE_FILE}")

    frame = pd.read_csv(SOURCE_FILE)
    result = SkyGuardEngine().process(frame)
    EXPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.observations.to_csv(EXPORT_FILE, index=False)
    return data_payload(source="refreshed")


class SkyGuardHandler(SimpleHTTPRequestHandler):
    """Serve the ``web/`` dashboard plus the JSON data/refresh endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802 (http.server naming)
        if urlparse(self.path).path == "/api/data":
            try:
                self._send_json(data_payload())
            except Exception as error:  # pragma: no cover - defensive
                self._send_json(
                    {"error": f"{type(error).__name__}: {error}"}, status=500
                )
            return
        super().do_GET()

    def do_POST(self):  # noqa: N802 (http.server naming)
        if urlparse(self.path).path != "/api/refresh":
            self._send_json({"error": "Not found"}, status=404)
            return
        print("Running live analysis cycle (SkyGuardEngine)...")
        try:
            payload = run_refresh()
            print(f"Live cycle complete: {payload['count']} observations analysed.")
            self._send_json(payload)
        except Exception as error:
            print(f"Live pipeline failed: {type(error).__name__}: {error}")
            self._send_json(
                {"error": f"Live pipeline failed: {type(error).__name__}: {error}"},
                status=500,
            )


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="SkyGuard AI local live-analysis server"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8137)
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), SkyGuardHandler)
    base = f"http://{args.host}:{args.port}"
    print("=" * 60)
    print("SkyGuard AI - live analysis server")
    print("=" * 60)
    print(f"Dashboard : {base}/")
    print(f"Data API  : GET  {base}/api/data")
    print(f"Refresh   : POST {base}/api/refresh")
    print(f"Web root  : {WEB_ROOT}")
    print(f"Export    : {EXPORT_FILE}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
