#!/usr/bin/env python3
"""
EV Navigation Live UI – receive DUT data via Zenoh and/or cloud-style data (weather, elevation).
Supports CSV replay for testing without DUT. Fixed X-axis 0–1800 s; reset when time_s <= 0.5.

Charts: SOC (red/yellow/green), Range, Speed + Battery temp, Elevation profile, Charge rate, Weather strip.
"""

from __future__ import annotations

import argparse
import csv
import json
import queue
import threading
import time
from collections import deque
from pathlib import Path
from typing import List, Optional, Tuple

import zenoh


# Columns expected from DUT or CSV (same order as ev_navigation_mock.csv)
EV_DISPLAY_COLUMNS = [
    "time_s",
    "battery_soc",
    "battery_capacity_wh",
    "vehicle_speed_mps",
    "battery_temp_c",
    "charge_rate_mw",
    "charge_port_connected",
    "range_km",
    "elevation_m",
    "ambient_temp_c",
    "weather_code",
]

MAX_CHART_POINTS = 20000
FIXED_CHART_TIME_S = 1800

# Weather code labels for UI
WEATHER_LABELS = {0: "Clear", 1: "Cloudy", 2: "Rain", 3: "Snow", 4: "Fog"}


def _web_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EV Navigation Live</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    body { font-family: system-ui, sans-serif; margin: 16px; background: #0d1117; color: #e6edf3; }
    h1 { font-size: 1.35rem; margin-bottom: 4px; color: #58a6ff; }
    .sub { font-size: 0.85rem; color: #8b949e; margin-bottom: 12px; }
    .weather-strip { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: #161b22; border: 1px solid #30363d; border-radius: 8px; margin-bottom: 12px; flex-wrap: wrap; }
    .weather-strip span { font-size: 0.9rem; }
    .weather-strip .temp { color: #79c0ff; font-weight: 600; }
    .weather-strip .elev { color: #a371f7; }
    .weather-strip .range { color: #3fb950; font-weight: 600; }
    .progress-block { margin: 12px 0; max-width: 420px; }
    .progress-block label { display: block; font-size: 0.9rem; color: #8b949e; margin-bottom: 4px; }
    .progress-track { height: 26px; background: #21262d; border-radius: 13px; overflow: hidden; border: 1px solid #30363d; }
    .progress-fill { height: 100%; border-radius: 12px; transition: width 0.2s ease, background-color 0.2s ease; }
    .progress-fill.soc-low { background: #f85149; }
    .progress-fill.soc-mid { background: #d29922; }
    .progress-fill.soc-high { background: #3fb950; }
    .progress-text { font-size: 0.85rem; color: #8b949e; margin-top: 4px; }
    .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 16px; margin: 16px 0; }
    .chart-wrap { min-height: 260px; }
    .wrap { overflow-x: auto; margin-top: 12px; }
    table { border-collapse: collapse; width: 100%; min-width: 720px; font-size: 0.85rem; }
    th, td { border: 1px solid #30363d; padding: 6px 10px; text-align: left; }
    th { background: #161b22; color: #58a6ff; }
    tr.data td { background: #21262d; }
    .footer-info { margin-top: 16px; padding-top: 10px; border-top: 1px solid #30363d; font-size: 0.85rem; color: #8b949e; }
  </style>
</head>
<body>
  <h1>EV Navigation Live</h1>
  <div class="sub">DUT + cloud (weather, elevation)</div>
  <div class="weather-strip" id="weatherStrip">
    <span class="temp">Ambient: — °C</span>
    <span class="elev">Elevation: — m</span>
    <span class="range">Range: — km</span>
    <span>Weather: —</span>
  </div>
  <div class="progress-block">
    <label>Battery SOC</label>
    <div class="progress-track">
      <div class="progress-fill soc-low" id="progressFill" style="width: 0%;"></div>
    </div>
    <div class="progress-text" id="progressText">— %</div>
  </div>
  <div class="charts-grid">
    <div class="chart-wrap"><canvas id="chartSoc"></canvas></div>
    <div class="chart-wrap"><canvas id="chartRange"></canvas></div>
    <div class="chart-wrap"><canvas id="chartSpeedTemp"></canvas></div>
    <div class="chart-wrap"><canvas id="chartElevation"></canvas></div>
    <div class="chart-wrap"><canvas id="chartCharge"></canvas></div>
  </div>
  <div class="wrap">
    <table>
      <thead id="thead"></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
  <div class="footer-info">
    <div id="config">Loading…</div>
    <div class="status" id="status" style="margin-top:4px;color:#79c0ff;">Connecting…</div>
  </div>
  <script>
    var charts = {};
    var weatherLabels = """ + json.dumps(WEATHER_LABELS) + """;
    function ensureCharts() {
      if (charts.soc) return;
      var opts = { animation: { duration: 0 }, transitions: { active: { animation: { duration: 0 } }, resize: { animation: { duration: 0 } } }, responsive: true, maintainAspectRatio: false, interaction: { mode: 'nearest', intersect: false }, scales: { x: { type: 'linear', min: 0, max: 1800, title: { display: true, text: 'Time (s)', color: '#8b949e' }, ticks: { color: '#8b949e' }, grid: { color: '#21262d' } }, y: { grid: { color: '#21262d' }, ticks: { color: '#8b949e' } } }, plugins: { legend: { labels: { color: '#e6edf3' } } } };
      var ctxSoc = document.getElementById('chartSoc').getContext('2d');
      charts.soc = new Chart(ctxSoc, {
        type: 'line',
        data: { datasets: [{ label: 'SOC (%)', data: [], fill: true, tension: 0, borderWidth: 2.5, pointRadius: 1.5, segment: { borderColor: function(ctx) { var y = (ctx.p1 && ctx.p1.parsed && ctx.p1.parsed.y !== undefined) ? ctx.p1.parsed.y : 0; if (y <= 20) return '#f85149'; if (y <= 50) return '#d29922'; return '#3fb950'; }, backgroundColor: function(ctx) { var y = (ctx.p1 && ctx.p1.parsed && ctx.p1.parsed.y !== undefined) ? ctx.p1.parsed.y : 0; if (y <= 20) return 'rgba(248,81,73,0.12)'; if (y <= 50) return 'rgba(210,153,34,0.12)'; return 'rgba(63,185,80,0.12)'; } }, pointBackgroundColor: function(ctx) { var y = (ctx.raw && ctx.raw.y !== undefined) ? ctx.raw.y : 0; if (y <= 20) return '#f85149'; if (y <= 50) return '#d29922'; return '#3fb950'; } }] },
        options: Object.assign({}, opts, { scales: { x: { type: 'linear', min: 0, max: 1800, title: { display: true, text: 'Time (s)', color: '#8b949e' }, ticks: { color: '#8b949e' }, grid: { color: '#21262d' } }, y: { min: 0, max: 100, title: { display: true, text: 'SOC (%)', color: '#58a6ff' }, ticks: { color: '#58a6ff', callback: function(v) { return v + '%'; } }, grid: { color: '#21262d' } } } })
      });
      var ctxRange = document.getElementById('chartRange').getContext('2d');
      charts.range = new Chart(ctxRange, {
        type: 'line',
        data: { datasets: [{ label: 'Range (km)', data: [], borderColor: '#3fb950', backgroundColor: 'rgba(63,185,80,0.1)', fill: true, tension: 0 }] },
        options: Object.assign({}, opts, { scales: { x: { type: 'linear', min: 0, max: 1800, grid: { color: '#21262d' } }, y: { title: { display: true, text: 'Range (km)', color: '#3fb950' }, ticks: { color: '#3fb950' }, grid: { color: '#21262d' } } } })
      });
      var ctxSpeedTemp = document.getElementById('chartSpeedTemp').getContext('2d');
      charts.speedTemp = new Chart(ctxSpeedTemp, {
        type: 'line',
        data: { datasets: [{ label: 'Speed (km/h)', data: [], borderColor: '#79c0ff', yAxisID: 'y_speed', tension: 0 }, { label: 'Battery temp (°C)', data: [], borderColor: '#a371f7', yAxisID: 'y_temp', tension: 0 }] },
        options: Object.assign({}, opts, { scales: { x: { type: 'linear', min: 0, max: 1800, grid: { color: '#21262d' } }, y_speed: { type: 'linear', position: 'left', title: { display: true, text: 'Speed (km/h)', color: '#79c0ff' }, ticks: { color: '#79c0ff' }, grid: { color: '#21262d' } }, y_temp: { type: 'linear', position: 'right', min: 0, max: 60, title: { display: true, text: 'Temp (°C)', color: '#a371f7' }, ticks: { color: '#a371f7' }, grid: { drawOnChartArea: false } } } })
      });
      var ctxElev = document.getElementById('chartElevation').getContext('2d');
      charts.elevation = new Chart(ctxElev, {
        type: 'line',
        data: { datasets: [{ label: 'Elevation (m)', data: [], borderColor: '#d2a8ff', backgroundColor: 'rgba(210,168,255,0.15)', fill: true, tension: 0.3 }] },
        options: Object.assign({}, opts, { scales: { x: { type: 'linear', min: 0, max: 1800, grid: { color: '#21262d' } }, y: { title: { display: true, text: 'Elevation (m)', color: '#d2a8ff' }, ticks: { color: '#d2a8ff' }, grid: { color: '#21262d' } } } })
      });
      var ctxCharge = document.getElementById('chartCharge').getContext('2d');
      charts.charge = new Chart(ctxCharge, {
        type: 'line',
        data: { datasets: [{ label: 'Charge rate (kW)', data: [], borderColor: '#f0883e', backgroundColor: 'transparent', tension: 0 }] },
        options: Object.assign({}, opts, { scales: { x: { type: 'linear', min: 0, max: 1800, grid: { color: '#21262d' } }, y: { title: { display: true, text: 'Power (kW)', color: '#f0883e' }, ticks: { color: '#f0883e' }, grid: { color: '#21262d' } } } })
      });
    }
    function update(data) {
      document.getElementById('config').innerHTML = (data.out_topic != null) ? '<b>Subscribed to:</b> ' + (data.out_topic || '—') + ' &nbsp; <b>Endpoint:</b> ' + (data.endpoint || '—') + (data.csv_file ? ' &nbsp; <b>CSV:</b> ' + data.csv_file : '') : 'CSV replay: ' + (data.csv_file || '—');
      document.getElementById('status').textContent = data.error ? ('Error: ' + data.error) : ('Messages: ' + data.count + (data.row ? ' — Receiving' : ' — Waiting…'));
      document.getElementById('status').style.color = data.error ? '#f85149' : '#79c0ff';

      var pct = null;
      if (data.chart_data && data.chart_data.length) { var last = data.chart_data[data.chart_data.length - 1]; pct = last.soc <= 1 ? last.soc * 100 : last.soc; }
      else if (data.row && data.headers) { var i = data.headers.indexOf('battery_soc'); if (i >= 0 && typeof data.row[i] === 'number') pct = data.row[i] <= 1 ? data.row[i] * 100 : data.row[i]; }
      var fillEl = document.getElementById('progressFill'); var textEl = document.getElementById('progressText');
      if (pct != null && fillEl && textEl) { pct = Math.max(0, Math.min(100, pct)); fillEl.style.width = pct.toFixed(2) + '%'; fillEl.className = 'progress-fill ' + (pct <= 20 ? 'soc-low' : pct <= 50 ? 'soc-mid' : 'soc-high'); textEl.textContent = pct.toFixed(1) + '%'; }
      else if (textEl) textEl.textContent = '— %';

      if (data.chart_data && data.chart_data.length) {
        var last = data.chart_data[data.chart_data.length - 1];
        document.querySelector('.weather-strip .temp').textContent = 'Ambient: ' + (last.ambient_temp_c != null ? last.ambient_temp_c.toFixed(1) : '—') + ' °C';
        document.querySelector('.weather-strip .elev').textContent = 'Elevation: ' + (last.elevation_m != null ? Math.round(last.elevation_m) : '—') + ' m';
        document.querySelector('.weather-strip .range').textContent = 'Range: ' + (last.range_km != null ? last.range_km.toFixed(1) : '—') + ' km';
        document.querySelector('.weather-strip span:last-child').textContent = 'Weather: ' + (weatherLabels[last.weather_code] != null ? weatherLabels[last.weather_code] : last.weather_code);
      }

      if (data.headers && data.headers.length) {
        var thead = document.getElementById('thead');
        if (!thead.querySelector('tr')) { var tr = document.createElement('tr'); data.headers.forEach(function(h) { var th = document.createElement('th'); th.textContent = h; tr.appendChild(th); }); thead.appendChild(tr); }
      }
      var tbody = document.getElementById('tbody'); tbody.innerHTML = '';
      if (data.row && data.row.length) {
        var tr = document.createElement('tr'); tr.className = 'data';
        var headers = data.headers || [];
        data.row.forEach(function(v, i) {
          var td = document.createElement('td');
          var h = headers[i] || '';
          if ((h === 'battery_soc') && typeof v === 'number' && v >= 0 && v <= 1) td.textContent = (v * 100).toFixed(2) + '%';
          else if (h === 'battery_soc' && typeof v === 'number') td.textContent = v.toFixed(2) + '%';
          else td.textContent = typeof v === 'number' ? (Number.isInteger(v) ? v : v.toFixed(4)) : v;
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      }

      if (data.chart_data && data.chart_data.length) {
        ensureCharts();
        var pts = data.chart_data.slice().sort(function(a, b) { return a.t - b.t; });
        charts.soc.data.datasets[0].data = pts.map(function(d) { return { x: d.t, y: (d.soc <= 1 ? d.soc * 100 : d.soc) }; });
        charts.range.data.datasets[0].data = pts.map(function(d) { return { x: d.t, y: d.range_km }; });
        charts.speedTemp.data.datasets[0].data = pts.map(function(d) { return { x: d.t, y: d.speed_kmh }; });
        charts.speedTemp.data.datasets[1].data = pts.map(function(d) { return { x: d.t, y: d.battery_temp_c }; });
        charts.elevation.data.datasets[0].data = pts.map(function(d) { return { x: d.t, y: d.elevation_m }; });
        charts.charge.data.datasets[0].data = pts.map(function(d) { return { x: d.t, y: d.charge_rate_kw }; });
        charts.soc.update('none'); charts.range.update('none'); charts.speedTemp.update('none'); charts.elevation.update('none'); charts.charge.update('none');
      }
    }
    function poll() {
      var url = (window.location.origin || 'http://127.0.0.1:5002') + '/api/latest';
      fetch(url).then(function(r) { return r.json(); }).then(update).catch(function(e) { update({ error: e.message, headers: [], row: null, count: 0, chart_data: [], out_topic: null, endpoint: null }); });
    }
    poll(); setInterval(poll, 200);
  </script>
</body>
</html>
"""


def build_conf(endpoint: str, mode: str = "peer", log_level: str = "info") -> zenoh.Config:
    zenoh.init_log_from_env_or(log_level)
    conf = zenoh.Config()
    conf.insert_json5("mode", json.dumps(mode))
    conf.insert_json5("connect/endpoints", json.dumps([endpoint]))
    return conf


def filter_row_for_display(headers: List[str], row: List[float]) -> Tuple[List[str], List[float]]:
    display_headers = [h for h in EV_DISPLAY_COLUMNS if h in headers]
    if not display_headers and len(row) >= len(EV_DISPLAY_COLUMNS):
        display_headers = list(EV_DISPLAY_COLUMNS)
    if not display_headers:
        return list(EV_DISPLAY_COLUMNS), []
    try:
        display_row = [row[headers.index(h)] for h in display_headers]
    except (ValueError, IndexError):
        display_row = row[: len(display_headers)] if len(row) >= len(display_headers) else list(row) + [0.0] * (len(display_headers) - len(row))
    return display_headers, display_row


def extract_chart_point(headers: List[str], row: List[float]) -> Optional[dict]:
    """Extract chart point: t, soc, range_km, speed_kmh, battery_temp_c, elevation_m, charge_rate_kw, ambient_temp_c, weather_code."""
    required = ["time_s", "battery_soc", "range_km", "vehicle_speed_mps", "battery_temp_c", "elevation_m", "charge_rate_mw", "ambient_temp_c", "weather_code"]
    try:
        idx = {h: headers.index(h) for h in required}
    except ValueError:
        return None
    if max(idx.values()) >= len(row):
        return None
    return {
        "t": round(row[idx["time_s"]], 2),
        "soc": row[idx["battery_soc"]],
        "range_km": row[idx["range_km"]],
        "speed_kmh": row[idx["vehicle_speed_mps"]] * 3.6,
        "battery_temp_c": row[idx["battery_temp_c"]],
        "elevation_m": row[idx["elevation_m"]],
        "charge_rate_kw": row[idx["charge_rate_mw"]] * 1000.0,
        "ambient_temp_c": row[idx["ambient_temp_c"]],
        "weather_code": int(row[idx["weather_code"]]) if row[idx["weather_code"]] == row[idx["weather_code"]] else 0,
    }


def run_csv_replay(csv_path: Path, data_queue: queue.Queue, delay_s: float = 0.05) -> None:
    """Replay CSV rows into data_queue. First line = headers, then numeric rows."""
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header_row = next(reader, None)
            if not header_row:
                return
            data_queue.put(("headers", header_row))
            for row in reader:
                if not row:
                    continue
                try:
                    values = [float(x.strip()) for x in row if x.strip()]
                    if values:
                        data_queue.put(("row", values))
                except ValueError:
                    continue
                time.sleep(delay_s)
        # Loop replay
        while True:
            time.sleep(1.0)
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if not row:
                        continue
                    try:
                        values = [float(x.strip()) for x in row if x.strip()]
                        if values:
                            data_queue.put(("row", values))
                    except ValueError:
                        continue
                    time.sleep(delay_s)
    except Exception as e:
        data_queue.put(("error", str(e)))


def main() -> int:
    ap = argparse.ArgumentParser(description="EV Navigation Live UI: Zenoh + optional CSV replay")
    ap.add_argument("--endpoint", default="tcp/192.168.1.10:1234", help="Zenoh connect endpoint")
    ap.add_argument("--mode", default="peer", choices=["peer", "client"], help="Zenoh mode")
    ap.add_argument("--out-topic", default="thermal/ev/navigation", help="Topic to subscribe to")
    ap.add_argument("--csv", type=Path, default=None, help="Replay from CSV (e.g. tests/csv_data/ev_navigation_mock.csv)")
    ap.add_argument("--csv-delay", type=float, default=0.05, help="Delay between CSV rows (s)")
    ap.add_argument("--log", default="warn", help="Zenoh log level")
    ap.add_argument("--web", action="store_true", help="Run browser UI")
    ap.add_argument("--port", type=int, default=5002, help="Port for web UI")
    args = ap.parse_args()

    display_headers = list(EV_DISPLAY_COLUMNS)
    data_queue: queue.Queue = queue.Queue()

    if args.csv and args.csv.exists():
        threading.Thread(target=run_csv_replay, args=(args.csv, data_queue, args.csv_delay), daemon=True).start()

    def run_subscriber_loop() -> None:
        if args.csv and args.csv.exists():
            return
        conf = build_conf(args.endpoint, mode=args.mode, log_level=args.log)
        buffer = bytearray()

        def listener(sample: zenoh.Sample) -> None:
            payload_bytes = sample.payload.to_bytes()
            if not payload_bytes:
                return
            buffer.extend(payload_bytes)
            while True:
                nl = buffer.find(b"\n")
                if nl == -1:
                    break
                line_bytes = bytes(buffer[: nl + 1])
                del buffer[: nl + 1]
                line_s = line_bytes.decode("utf-8", errors="replace").strip()
                if not line_s:
                    continue
                parts = [p.strip() for p in line_s.split(",")]
                try:
                    values = [float(p) for p in parts]
                    if values:
                        data_queue.put(("row", values))
                except ValueError:
                    if len(parts) > 1:
                        data_queue.put(("headers", parts))

        try:
            with zenoh.open(conf) as session:
                session.declare_subscriber(args.out_topic, listener)
                while True:
                    time.sleep(1)
        except Exception as e:
            data_queue.put(("error", str(e)))

    threading.Thread(target=run_subscriber_loop, daemon=True).start()

    if not args.web:
        print("Use --web to run the UI. Example: python tests/ev_navigation_live_ui.py --web --csv tests/csv_data/ev_navigation_mock.csv")
        return 0

    try:
        from flask import Flask, jsonify
    except ImportError:
        print("Flask is required. pip install flask")
        return 1

    state_lock = threading.Lock()
    shared_state: dict = {
        "headers": display_headers,
        "row": None,
        "count": 0,
        "error": None,
        "out_topic": args.out_topic,
        "endpoint": args.endpoint,
        "csv_file": str(args.csv) if args.csv else None,
        "chart_data": [],
        "stream_headers": None,
    }
    chart_deque: deque = deque(maxlen=MAX_CHART_POINTS)

    def state_updater() -> None:
        nonlocal chart_deque
        while True:
            try:
                item = data_queue.get(timeout=0.5)
                if item[0] == "error":
                    with state_lock:
                        shared_state["error"] = item[1]
                elif item[0] == "headers":
                    with state_lock:
                        shared_state["stream_headers"] = item[1]
                elif item[0] == "row":
                    row = item[1]
                    with state_lock:
                        headers = shared_state.get("stream_headers") or display_headers
                        display_headers_out, display_row = filter_row_for_display(headers, row)
                        shared_state["headers"] = display_headers_out
                        shared_state["row"] = display_row
                        shared_state["count"] = shared_state.get("count", 0) + 1
                        pt = extract_chart_point(headers, row)
                        if pt is not None:
                            if pt["t"] <= 0.5:
                                chart_deque.clear()
                            chart_deque.append(pt)
                            shared_state["chart_data"] = list(chart_deque)
            except queue.Empty:
                pass

    threading.Thread(target=state_updater, daemon=True).start()

    app = Flask(__name__)

    @app.route("/api/latest")
    def api_latest() -> str:
        with state_lock:
            copy = {
                "headers": shared_state["headers"],
                "row": shared_state["row"],
                "count": shared_state["count"],
                "error": shared_state["error"],
                "out_topic": shared_state["out_topic"],
                "endpoint": shared_state["endpoint"],
                "csv_file": shared_state.get("csv_file"),
                "chart_data": shared_state.get("chart_data", []),
            }
        return jsonify(copy)

    @app.route("/")
    def index() -> str:
        return _web_html()

    port = args.port
    url = f"http://127.0.0.1:{port}"
    def open_browser() -> None:
        time.sleep(1.2)
        import webbrowser
        webbrowser.open(url)
    threading.Thread(target=open_browser, daemon=True).start()
    print(f"EV Navigation Live UI: {url}")
    if args.csv:
        print(f"  CSV replay: {args.csv}")
    else:
        print(f"  Zenoh: {args.out_topic} @ {args.endpoint}")
    print("Close with Ctrl+C.")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
