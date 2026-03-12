#!/usr/bin/env python3
"""
HIL DCFC Live UI – fixed X-axis 0–1800 s and fixed Y-axes. Data updates as it arrives; plot resets when 0 s data arrives.

Charts use fixed axes (X: 0–1800 s; SOC: 0–100%). When a sample with time_s <= 0.5 s arrives, the
buffer is cleared and a new run is drawn. Points are sorted by time before drawing to avoid backward lines.
Animation is disabled so the plot redraws in place without travelling.

Usage:
  python tests/thermal_hil_live_ui_dcfc_chart_bt_cycle.py --web
  python tests/thermal_hil_live_ui_dcfc_chart_bt_cycle.py --web --port 5001
"""

from __future__ import annotations

import argparse
import json
import queue
import threading
import time
from collections import deque
from pathlib import Path
from typing import List, Tuple

import zenoh


DISPLAY_COLUMNS = [
    "time_s",
    "driver_speed_mps",
    "vehicle_speed_mps",
    "battery_soc",
    "battery_soh",
    "battery_temp_K",
    "battery_current_A",
    "battery_voltage_V",
    "battery_heat_gen_W",
    "battery_heat_rej_W",
]

CHART_KEYS = ["time_s", "battery_soc", "battery_temp_K", "battery_current_A", "battery_voltage_V"]

# Keep enough points to cover full 0-1800 s (e.g. ~10 Hz = 18000 points)
MAX_CHART_POINTS = 20000

# Fixed X-axis max (seconds). Both charts always show 0 to this value.
FIXED_CHART_TIME_S = 1800


def _web_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HIL DCFC – Fast charging (cycle)</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 16px; background: #1a1a2e; color: #eee; }}
    h1 {{ font-size: 1.25rem; margin-bottom: 8px; }}
    .config {{ font-size: 0.85rem; color: #888; margin-bottom: 8px; }}
    .config span {{ margin-right: 16px; }}
    .status {{ margin-bottom: 8px; font-weight: 600; color: #7fdbff; }}
    .status.error {{ color: #ff6b6b; }}
    .progress-block {{ margin: 12px 0; max-width: 400px; }}
    .progress-block label {{ display: block; font-size: 0.9rem; color: #888; margin-bottom: 4px; }}
    .progress-track {{ height: 24px; background: #0f3460; border-radius: 12px; overflow: hidden; border: 1px solid #333; }}
    .progress-fill {{ height: 100%; border-radius: 11px; transition: width 0.2s ease, background-color 0.2s ease; }}
    .progress-fill.soc-low {{ background: #e74c3c; }}
    .progress-fill.soc-mid {{ background: #f1c40f; }}
    .progress-fill.soc-high {{ background: #2ecc71; }}
    .progress-text {{ font-size: 0.85rem; color: #aaa; margin-top: 4px; }}
    .charts-row {{ display: flex; gap: 16px; margin: 16px 0; flex-wrap: wrap; }}
    .chart-wrap {{ flex: 1; min-width: 320px; height: 320px; }}
    .wrap {{ overflow-x: auto; margin-top: 12px; }}
    table {{ border-collapse: collapse; width: 100%; min-width: 640px; }}
    th, td {{ border: 1px solid #333; padding: 6px 10px; text-align: left; }}
    th {{ background: #16213e; color: #7fdbff; }}
    tr.data td {{ background: #0f3460; }}
    .footer-info {{ margin-top: 16px; padding-top: 8px; border-top: 1px solid #333; }}
  </style>
</head>
<body>
  <h1>HIL DCFC – Fast charging progress (0–1800 s)</h1>
  <div class="progress-block">
    <label>Charging progress (SOC)</label>
    <div class="progress-track">
      <div class="progress-fill soc-low" id="progressFill" style="width: 0%;"></div>
    </div>
    <div class="progress-text" id="progressText">— %</div>
  </div>
  <div class="charts-row">
    <div class="chart-wrap">
      <canvas id="chart1"></canvas>
    </div>
    <div class="chart-wrap">
      <canvas id="chart2"></canvas>
    </div>
  </div>
  <div class="wrap">
    <table>
      <thead id="thead"></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
  <div class="footer-info">
    <div class="config" id="config">Loading…</div>
    <div class="status" id="status">Connecting…</div>
  </div>
  <script>
    var chart1 = null;
    var chart2 = null;
    function ensureCharts() {{
      if (chart1) return;
      var ctx1 = document.getElementById('chart1').getContext('2d');
      chart1 = new Chart(ctx1, {{
        type: 'line',
        data: {{
          datasets: [
            {{
              label: 'SOC (%)',
              data: [],
              fill: true,
              tension: 0,
              borderWidth: 2.5,
              pointRadius: 2,
              pointBorderWidth: 1,
              segment: {{
                borderColor: function(ctx) {{
                  var y = (ctx.p1 && ctx.p1.parsed && ctx.p1.parsed.y !== undefined) ? ctx.p1.parsed.y : 0;
                  if (y <= 20) return '#e74c3c';
                  if (y <= 50) return '#f1c40f';
                  return '#2ecc71';
                }},
                backgroundColor: function(ctx) {{
                  var y = (ctx.p1 && ctx.p1.parsed && ctx.p1.parsed.y !== undefined) ? ctx.p1.parsed.y : 0;
                  if (y <= 20) return 'rgba(231, 76, 60, 0.15)';
                  if (y <= 50) return 'rgba(241, 196, 15, 0.15)';
                  return 'rgba(46, 204, 113, 0.15)';
                }}
              }},
              pointBackgroundColor: function(ctx) {{
                var y = (ctx.raw && ctx.raw.y !== undefined) ? ctx.raw.y : (ctx.parsed && ctx.parsed.y !== undefined ? ctx.parsed.y : 0);
                if (y <= 20) return '#e74c3c';
                if (y <= 50) return '#f1c40f';
                return '#2ecc71';
              }},
              pointBorderColor: function(ctx) {{
                var y = (ctx.raw && ctx.raw.y !== undefined) ? ctx.raw.y : (ctx.parsed && ctx.parsed.y !== undefined ? ctx.parsed.y : 0);
                if (y <= 20) return '#e74c3c';
                if (y <= 50) return '#f1c40f';
                return '#2ecc71';
              }}
            }}
          ]
        }},
        options: {{
          animation: {{ duration: 0 }},
          transitions: {{ active: {{ animation: {{ duration: 0 }} }}, resize: {{ animation: {{ duration: 0 }} }} }},
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{ mode: 'nearest', intersect: false }},
          scales: {{
            x: {{ type: 'linear', min: 0, max: 1800, title: {{ display: true, text: 'Time (s)', color: '#888' }}, ticks: {{ color: '#aaa', stepSize: 300 }}, grid: {{ color: '#333' }} }},
            y: {{ min: 0, max: 100, title: {{ display: true, text: 'SOC (%)', color: '#7fdbff' }}, ticks: {{ color: '#7fdbff', callback: function(v) {{ return v + '%'; }} }}, grid: {{ color: '#333' }} }}
          }},
          plugins: {{ legend: {{ labels: {{ color: '#eee' }} }} }}
        }}
      }});
      var ctx2 = document.getElementById('chart2').getContext('2d');
      chart2 = new Chart(ctx2, {{
        type: 'line',
        data: {{
          datasets: [
            {{ label: 'Current (A)', data: [], borderColor: '#2ecc71', backgroundColor: 'transparent', yAxisID: 'y_current', tension: 0 }},
            {{ label: 'Voltage (V)', data: [], borderColor: '#e74c3c', backgroundColor: 'transparent', yAxisID: 'y_voltage', tension: 0 }},
            {{ label: 'Temp (°C)', data: [], borderColor: '#9b59b6', backgroundColor: 'transparent', yAxisID: 'y_temp', tension: 0 }}
          ]
        }},
        options: {{
          animation: {{ duration: 0 }},
          transitions: {{ active: {{ animation: {{ duration: 0 }} }}, resize: {{ animation: {{ duration: 0 }} }} }},
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{ mode: 'nearest', intersect: false }},
          scales: {{
            x: {{ type: 'linear', min: 0, max: 1800, title: {{ display: true, text: 'Time (s)', color: '#888' }}, ticks: {{ color: '#aaa', stepSize: 300 }}, grid: {{ color: '#333' }} }},
            y_current: {{ type: 'linear', position: 'left', title: {{ display: true, text: 'Current (A)', color: '#2ecc71' }}, ticks: {{ color: '#2ecc71' }}, grid: {{ color: '#333' }} }},
            y_voltage: {{ type: 'linear', position: 'right', min: 0, max: 500, title: {{ display: true, text: 'Voltage (V)', color: '#e74c3c' }}, ticks: {{ color: '#e74c3c' }}, grid: {{ drawOnChartArea: false }} }},
            y_temp: {{ type: 'linear', position: 'right', min: 0, max: 100, title: {{ display: true, text: 'Temp (°C)', color: '#9b59b6' }}, ticks: {{ color: '#9b59b6' }}, grid: {{ drawOnChartArea: false }} }}
          }},
          plugins: {{ legend: {{ labels: {{ color: '#eee' }} }} }}
        }}
      }});
    }}
    function update(data) {{
      var configEl = document.getElementById('config');
      if (data.out_topic != null)
        configEl.innerHTML = '<span><b>Subscribed to:</b> ' + (data.out_topic || '—') + '</span> <span><b>Endpoint:</b> ' + (data.endpoint || '—') + '</span>';
      document.getElementById('status').textContent = data.error
        ? 'Error: ' + data.error
        : 'Messages: ' + data.count + (data.row ? ' — Receiving' : ' — Waiting for data…');
      if (data.error) document.getElementById('status').className = 'status error';
      else document.getElementById('status').className = 'status';

      var pct = null;
      if (data.chart_data && data.chart_data.length) {{
        var last = data.chart_data[data.chart_data.length - 1];
        pct = last.soc <= 1 ? last.soc * 100 : last.soc;
      }} else if (data.row && data.headers) {{
        var i = data.headers.indexOf('battery_soc');
        if (i >= 0 && typeof data.row[i] === 'number') pct = data.row[i] <= 1 ? data.row[i] * 100 : data.row[i];
      }}
      var fillEl = document.getElementById('progressFill');
      var textEl = document.getElementById('progressText');
      if (pct != null && fillEl && textEl) {{
        pct = Math.max(0, Math.min(100, pct));
        fillEl.style.width = pct.toFixed(2) + '%';
        fillEl.className = 'progress-fill ' + (pct <= 20 ? 'soc-low' : pct <= 50 ? 'soc-mid' : 'soc-high');
        textEl.textContent = pct.toFixed(1) + '%';
      }} else if (textEl) textEl.textContent = '— %';

      if (data.headers && data.headers.length) {{
        var thead = document.getElementById('thead');
        if (!thead.querySelector('tr')) {{
          var tr = document.createElement('tr');
          data.headers.forEach(function(h) {{
            var th = document.createElement('th');
            th.textContent = (h === 'battery_soc' || h === 'battery_soh') ? h + ' (%)' : (h === 'battery_temp_K' ? 'battery_temp_K (°C)' : h);
            tr.appendChild(th);
          }});
          thead.appendChild(tr);
        }}
      }}
      var tbody = document.getElementById('tbody');
      tbody.innerHTML = '';
      if (data.row && data.row.length) {{
        var tr = document.createElement('tr');
        tr.className = 'data';
        var headers = data.headers || [];
        data.row.forEach(function(v, i) {{
          var td = document.createElement('td');
          var h = headers[i] || '';
          if ((h === 'battery_soc' || h === 'battery_soh') && typeof v === 'number' && v >= 0 && v <= 1)
            td.textContent = (v * 100).toFixed(2) + '%';
          else if ((h === 'battery_soc' || h === 'battery_soh') && typeof v === 'number')
            td.textContent = v.toFixed(2) + '%';
          else if (h === 'battery_temp_K' && typeof v === 'number')
            td.textContent = (v - 273.15).toFixed(2) + ' °C';
          else
            td.textContent = typeof v === 'number' ? (Number.isInteger(v) ? v : v.toFixed(4)) : v;
          tr.appendChild(td);
        }});
        tbody.appendChild(tr);
      }}

      if (data.chart_data && data.chart_data.length) {{
        ensureCharts();
        var pts = data.chart_data.slice().sort(function(a, b) {{ return a.t - b.t; }});
        chart1.data.datasets[0].data = pts.map(function(d) {{ return {{ x: d.t, y: (d.soc <= 1 ? d.soc * 100 : d.soc) }}; }});
        chart2.data.datasets[0].data = pts.map(function(d) {{ return {{ x: d.t, y: d.current }}; }});
        chart2.data.datasets[1].data = pts.map(function(d) {{ return {{ x: d.t, y: d.voltage }}; }});
        chart2.data.datasets[2].data = pts.map(function(d) {{ return {{ x: d.t, y: d.temp - 273.15 }}; }});
        chart1.update('none');
        chart2.update('none');
      }}
    }}
    function poll() {{
      var url = (window.location.origin || 'http://127.0.0.1:5000') + '/api/latest';
      fetch(url).then(function(r) {{ return r.json(); }}).then(update).catch(function(e) {{
        update({{ error: e.message, headers: [], row: null, count: 0, chart_data: [], out_topic: null, endpoint: null }});
      }});
    }}
    poll();
    setInterval(poll, 200);
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
    """Return (display_headers, display_row) for DISPLAY_COLUMNS; match by header name or by index."""
    display_headers = [h for h in DISPLAY_COLUMNS if h in headers]
    if not display_headers and len(row) >= len(DISPLAY_COLUMNS):
        display_headers = list(DISPLAY_COLUMNS)
    if not display_headers:
        return list(DISPLAY_COLUMNS), []
    try:
        display_row = [row[headers.index(h)] for h in display_headers]
    except (ValueError, IndexError):
        if len(row) >= len(DISPLAY_COLUMNS):
            display_row = row[: len(DISPLAY_COLUMNS)]
        else:
            display_row = list(row) + [0.0] * (len(display_headers) - len(row))
    return display_headers, display_row


def extract_chart_point(headers: List[str], row: List[float]) -> dict | None:
    """Extract {t, soc, current, voltage, temp} from row using header indices. Returns None if not enough data."""
    try:
        idx_t = headers.index("time_s")
        idx_soc = headers.index("battery_soc")
        idx_current = headers.index("battery_current_A")
        idx_voltage = headers.index("battery_voltage_V")
        idx_temp = headers.index("battery_temp_K")
    except ValueError:
        return None
    if max(idx_t, idx_soc, idx_current, idx_voltage, idx_temp) >= len(row):
        return None
    return {
        "t": round(row[idx_t], 2),
        "soc": row[idx_soc],
        "current": row[idx_current],
        "voltage": row[idx_voltage],
        "temp": row[idx_temp],
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="HIL DCFC Live UI (cycle): fixed X-axis 0–max s; reset when time repeats from 0"
    )
    ap.add_argument("--endpoint", default="tcp/192.168.1.10:1234", help="Zenoh connect endpoint")
    ap.add_argument("--mode", default="peer", choices=["peer", "client"], help="Zenoh mode")
    ap.add_argument("--out-topic", default="other/topic", help="Topic to subscribe to")
    ap.add_argument("--log", default="warn", help="Zenoh log level")
    ap.add_argument("--web", action="store_true", help="Run browser UI with chart")
    ap.add_argument("--port", type=int, default=5000, help="Port for web UI")
    args = ap.parse_args()
    display_headers = list(DISPLAY_COLUMNS)
    data_queue: queue.Queue = queue.Queue()

    def run_subscriber_loop() -> None:
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
                    if len(values) > 0:
                        data_queue.put(("row", values))
                except ValueError:
                    if parts and len(parts) > 1:
                        data_queue.put(("headers", parts))

        try:
            with zenoh.open(conf) as session:
                session.declare_subscriber(args.out_topic, listener)
                while True:
                    time.sleep(1)
        except Exception as e:
            data_queue.put(("error", str(e)))

    thread = threading.Thread(target=run_subscriber_loop, daemon=True)
    thread.start()

    if not args.web:
        print("Use --web to run the UI. Example: python tests/thermal_hil_live_ui_dcfc_chart_bt_cycle.py --web")
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
        "chart_data": [],
        "chart_max_time_s": FIXED_CHART_TIME_S,
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
                        _, display_row = filter_row_for_display(headers, row)
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

    updater_thread = threading.Thread(target=state_updater, daemon=True)
    updater_thread.start()

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
                "chart_data": shared_state.get("chart_data", []),
                "chart_max_time_s": FIXED_CHART_TIME_S,
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
    print(f"HIL DCFC Chart UI (0–{FIXED_CHART_TIME_S} s): {url}")
    print("Close with Ctrl+C.")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
