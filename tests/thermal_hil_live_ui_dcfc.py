#!/usr/bin/env python3
"""
HIL DCFC Live UI: subscribe to Zenoh topic, buffer CSV lines, and display
received data using headers from hil_dcfc_output.csv.

Based on thermal_hil_live_ui_multi.py; headers are read from tests/csv_data/hil_dcfc_output.csv
by default. Same multi-row layout (max 6 columns per row, data under each header, 2-line spacing).

Usage:
  python tests/thermal_hil_live_ui_dcfc.py
  python tests/thermal_hil_live_ui_dcfc.py --out-topic other/topic --endpoint tcp/192.168.1.10:1234
  python tests/thermal_hil_live_ui_dcfc.py --terminal
  python tests/thermal_hil_live_ui_dcfc.py --web
"""

from __future__ import annotations

import argparse
import json
import queue
import threading
import time
from pathlib import Path
from typing import List, Tuple

import zenoh


# Path to CSV that defines headers (first line = column names)
DCFC_CSV_PATH = Path(__file__).resolve().parent / "csv_data" / "hil_dcfc_output.csv"

# Default headers from hil_dcfc_output.csv (fallback if file missing)
DEFAULT_HEADERS = [
    "time_s", "driver_speed_mps", "vehicle_speed_mps", "battery_soc", "battery_soh",
    "battery_temp_K", "battery_current_A", "battery_voltage_V", "battery_heat_gen_W",
    "battery_heat_rej_W", "emotor_torque_Nm", "emotor_speed_radps", "ctrl_em_trq_cmd_Nm",
    "ctrl_brk_frc_cmd_N", "env_temp_degC", "cabin_temp_setpoint_degC", "hvac_blower_enum",
    "defrost_bool", "ac_bool", "photo_wpm2", "xtemp_batt_trgt_temp_degC",
    "xtemp_power_comp_cabin_limit_w", "xtem_power_ptc_cabin_limit_w", "xtem_temp_inv_in_trgt_degC",
    "pe_heat_W", "battery_heat_W", "power_est_pe_heat_W", "power_est_pe_aux_power_nom_W",
    "power_est_battery_heat_W", "power_est_batt_thermal_epower_W", "power_est_total_thermal_power_W",
    "power_est_heat_losses_pe_perc", "power_est_heat_loss_batt_perc", "power_est_cop_scaler",
    "power_est_cop_effective", "coolant_rad_out_temp_degC", "coolant_batt_in_temp_degC",
    "battery_temp_max_degC", "battery_temp_min_degC", "inverter_temp_degC", "motor_temp_degC",
    "cmd_fan_perc", "cmd_motor_pump_perc", "cmd_batt_ewp_perc", "cmd_batt_ptc_bool",
    "cmd_multi_valve_enum", "thermal_mode_enum", "radiator_heat_W", "total_power_W",
    "voltage_limiting_current_A", "plating_limiting_current_A", "temp_limiting_current_A",
    "infrastructure_limiting_current_A",
]

# All columns from DCFC CSV; layout: max 6 per row
DISPLAY_COLUMNS = list(DEFAULT_HEADERS)
COLS_PER_ROW = 6

# HTML for --web mode (browser UI)
_WEB_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HIL DCFC Live Data</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 16px; background: #1a1a2e; color: #eee; }
    h1 { font-size: 1.25rem; margin-bottom: 8px; }
    .config { font-size: 0.85rem; color: #888; margin-bottom: 12px; }
    .config span { margin-right: 16px; }
    .status { margin-bottom: 12px; font-weight: 600; color: #7fdbff; }
    .status.error { color: #ff6b6b; }
    .hint { font-size: 0.8rem; color: #888; margin-top: 8px; max-width: 560px; }
    .wrap { overflow-x: auto; }
    table { border-collapse: collapse; width: 100%; min-width: 640px; }
    th, td { border: 1px solid #333; padding: 8px 12px; text-align: left; }
    th { background: #16213e; color: #7fdbff; position: sticky; top: 0; }
    tr.data td { background: #0f3460; }
    tr.data:hover td { background: #163a5e; }
    tr.header-row td { background: #16213e; color: #7fdbff; font-weight: bold; }
    tr.spacer td { height: 2em; border: none; background: transparent; }
  </style>
</head>
<body>
  <h1>HIL DCFC Live Data</h1>
  <div class="config" id="config">Loading…</div>
  <div class="status" id="status">Connecting…</div>
  <div class="hint" id="hint"></div>
  <div class="wrap">
    <table>
      <tbody id="tbody"></tbody>
    </table>
  </div>
  <script>
    function update(data) {
      var configEl = document.getElementById('config');
      if (data.out_topic != null)
        configEl.innerHTML = '<span><b>Subscribed to (out-topic):</b> ' + (data.out_topic || '—') + '</span> <span><b>Endpoint:</b> ' + (data.endpoint || '—') + '</span>';
      document.getElementById('status').textContent = data.error
        ? 'Error: ' + data.error
        : 'Messages: ' + data.count + (data.row ? ' — Receiving' : ' — Waiting for data…');
      var statusEl = document.getElementById('status');
      if (data.error) {
        statusEl.className = 'status error';
        var hint = document.getElementById('hint');
        if (data.error === 'Failed to fetch') {
          hint.textContent = 'Tip: Open this page at the URL printed by the script (e.g. http://127.0.0.1:5000). Keep the script running. If the script runs on another machine, use that machine\\'s IP and port (e.g. http://192.168.1.10:5000).';
        } else hint.textContent = '';
      } else {
        statusEl.className = 'status';
        document.getElementById('hint').textContent = 'Headers from hil_dcfc_output.csv. Data is published to the out-topic by the DUT.';
      }

      var COLS_PER_ROW = 6;
      var SPACER_ROWS = 2;
      var tbody = document.getElementById('tbody');
      tbody.innerHTML = '';
      if (data.headers && data.headers.length) {
        var numChunks = Math.ceil(data.headers.length / COLS_PER_ROW);
        for (var chunk = 0; chunk < numChunks; chunk++) {
          var trH = document.createElement('tr');
          trH.className = 'header-row';
          for (var c = 0; c < COLS_PER_ROW; c++) {
            var i = chunk * COLS_PER_ROW + c;
            var td = document.createElement('td');
            td.textContent = i < data.headers.length ? data.headers[i] : '';
            trH.appendChild(td);
          }
          tbody.appendChild(trH);
          var trD = document.createElement('tr');
          trD.className = 'data';
          for (var c = 0; c < COLS_PER_ROW; c++) {
            var i = chunk * COLS_PER_ROW + c;
            var td = document.createElement('td');
            if (data.row && i < data.row.length) {
              var v = data.row[i];
              td.textContent = typeof v === 'number' ? (Number.isInteger(v) ? v : v.toFixed(4)) : v;
            }
            trD.appendChild(td);
          }
          tbody.appendChild(trD);
          for (var s = 0; s < SPACER_ROWS; s++) {
            var trSp = document.createElement('tr');
            trSp.className = 'spacer';
            var tdSp = document.createElement('td');
            tdSp.colSpan = COLS_PER_ROW;
            trSp.appendChild(tdSp);
            tbody.appendChild(trSp);
          }
        }
      }
    }
    function poll() {
      var url = (window.location.origin || 'http://127.0.0.1:' + (window.location.port || 5000)) + '/api/latest';
      fetch(url).then(function(r) { return r.json(); }).then(update).catch(function(e) {
        update({ error: e.message, headers: [], row: null, count: 0, out_topic: null, endpoint: null });
      });
    }
    poll();
    setInterval(poll, 200);
  </script>
</body>
</html>
"""


def build_conf(endpoint: str, mode: str = "peer", log_level: str = "info") -> zenoh.Config:
    """Create a zenoh.Config with logging and a single connect endpoint."""
    zenoh.init_log_from_env_or(log_level)
    conf = zenoh.Config()
    conf.insert_json5("mode", json.dumps(mode))
    conf.insert_json5("connect/endpoints", json.dumps([endpoint]))
    return conf


def read_headers_from_csv(csv_path: Path) -> List[str]:
    """Read first line of CSV as column headers. Fallback to DEFAULT_HEADERS."""
    if not csv_path.exists():
        return list(DEFAULT_HEADERS)
    try:
        line = csv_path.read_text(encoding="utf-8").strip().splitlines()[0]
        return [c.strip() for c in line.split(",") if c.strip()]
    except Exception:
        return list(DEFAULT_HEADERS)


def filter_row_for_display(headers: List[str], row: List[float]) -> Tuple[List[str], List[float]]:
    """Return (display_headers, display_row) for DISPLAY_COLUMNS only; by index if header names differ."""
    display_headers = [h for h in DISPLAY_COLUMNS if h in headers]
    if not display_headers and headers and row:
        display_headers = headers[:]
    try:
        display_row = [row[headers.index(h)] for h in display_headers]
    except (ValueError, IndexError):
        if len(row) <= len(display_headers):
            display_row = list(row) + [0.0] * (len(display_headers) - len(row))
        else:
            display_row = row[: len(display_headers)]
    return display_headers, display_row


def main() -> int:
    ap = argparse.ArgumentParser(description="HIL DCFC Live UI – subscribe and display CSV data (headers from hil_dcfc_output.csv)")
    ap.add_argument("--endpoint", default="tcp/192.168.1.10:1234", help="Zenoh connect endpoint")
    ap.add_argument("--mode", default="peer", choices=["peer", "client"], help="Zenoh mode")
    ap.add_argument("--out-topic", default="other/topic", help="Topic to subscribe to (DUT output)")
    ap.add_argument(
        "--csv",
        type=Path,
        default=DCFC_CSV_PATH,
        help="CSV file to read column headers from (default: csv_data/hil_dcfc_output.csv)",
    )
    ap.add_argument("--log", default="warn", help="Zenoh log level (info/debug/warn/error)")
    ap.add_argument(
        "--terminal",
        action="store_true",
        help="Run in terminal mode (no GUI); print latest row to stdout.",
    )
    ap.add_argument(
        "--web",
        action="store_true",
        help="Run browser-based UI (Flask). Open http://127.0.0.1:PORT in browser.",
    )
    ap.add_argument("--port", type=int, default=5000, help="Port for web UI (default: 5000)")
    args = ap.parse_args()

    headers = read_headers_from_csv(args.csv)
    if not headers:
        headers = list(DEFAULT_HEADERS)
    display_headers, _ = filter_row_for_display(headers, [0.0] * max(len(headers), 1))
    if not display_headers:
        display_headers = list(DEFAULT_HEADERS)

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
                    pass  # skip header or non-numeric lines

        try:
            with zenoh.open(conf) as session:
                session.declare_subscriber(args.out_topic, listener)
                while True:
                    time.sleep(1)
        except Exception as e:
            data_queue.put(("error", str(e)))

    thread = threading.Thread(target=run_subscriber_loop, daemon=True)
    thread.start()

    # Terminal mode: print header then data under it per block, 2 blank lines between blocks
    if args.terminal:
        print("Subscribed. Waiting for data (Ctrl+C to exit)...")
        try:
            while True:
                try:
                    item = data_queue.get(timeout=0.2)
                    if item[0] == "error":
                        print("Error:", item[1])
                        return 1
                    if item[0] == "row":
                        _, display_row = filter_row_for_display(headers, item[1])
                        for r in range(0, max(len(display_headers), len(display_row)), COLS_PER_ROW):
                            h_chunk = display_headers[r : r + COLS_PER_ROW]
                            v_chunk = display_row[r : r + COLS_PER_ROW] if r < len(display_row) else []
                            print(" | ".join(h_chunk))
                            print(" | ".join(f"{v:.4g}" for v in v_chunk))
                            print()
                            print()
                except queue.Empty:
                    pass
        except KeyboardInterrupt:
            print("\nExiting.")
        return 0

    # Web (browser) UI
    if args.web:
        try:
            from flask import Flask, jsonify
        except ImportError:
            print("Flask is required for --web. Install with: pip install flask")
            return 1

        state_lock = threading.Lock()
        shared_state: dict = {
            "headers": display_headers,
            "row": None,
            "count": 0,
            "error": None,
            "out_topic": args.out_topic,
            "endpoint": args.endpoint,
        }

        def state_updater() -> None:
            while True:
                try:
                    item = data_queue.get(timeout=0.5)
                    if item[0] == "error":
                        with state_lock:
                            shared_state["error"] = item[1]
                    elif item[0] == "row":
                        _, display_row = filter_row_for_display(headers, item[1])
                        with state_lock:
                            shared_state["row"] = display_row
                            shared_state["count"] = shared_state.get("count", 0) + 1
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
                }
            return jsonify(copy)

        @app.route("/")
        def index() -> str:
            return _WEB_HTML

        port = args.port
        url = f"http://127.0.0.1:{port}"

        def open_browser() -> None:
            time.sleep(1.2)
            import webbrowser
            webbrowser.open(url)

        threading.Thread(target=open_browser, daemon=True).start()
        print(f"HIL DCFC Live UI (web): {url}")
        print("Close with Ctrl+C.")
        app.run(host="0.0.0.0", port=port, debug=False, threaded=True, use_reloader=False)
        return 0

    # Tkinter UI
    try:
        import tkinter as tk
        from tkinter import ttk
        from tkinter import font as tkfont
    except ImportError:
        print("tkinter is required. On Ubuntu: sudo apt install python3-tk")
        print("Or run with --terminal or --web.")
        return 1

    root = tk.Tk()
    root.title("HIL DCFC Live Data")
    root.geometry("1200x500")
    root.minsize(800, 400)

    # Top: status and message count
    status_frame = ttk.Frame(root, padding=4)
    status_frame.pack(fill=tk.X)
    status_var = tk.StringVar(value="Connecting...")
    ttk.Label(status_frame, textvariable=status_var, font=("", 10, "bold")).pack(side=tk.LEFT)
    count_var = tk.StringVar(value="Messages: 0")
    ttk.Label(status_frame, textvariable=count_var, font=("", 10)).pack(side=tk.LEFT, padx=20)

    # Scrollable area for table
    table_container = ttk.Frame(root, padding=4)
    table_container.pack(fill=tk.BOTH, expand=True)
    canvas = tk.Canvas(table_container)
    scrollbar_y = ttk.Scrollbar(table_container)
    scrollbar_x = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_y.config(command=canvas.yview)
    scrollbar_x.config(command=canvas.xview)
    canvas.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    table_frame = ttk.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=table_frame, anchor=tk.NW)

    def on_frame_configure(_event) -> None:
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event: tk.Event) -> None:
        canvas.itemconfig(canvas_window, width=event.width)

    table_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    # Build grid: for each block of 6 — header row, data row under it, then 2 spacer rows
    SPACER_ROWS = 2
    ROWS_PER_BLOCK = 2 + SPACER_ROWS
    header_labels: List[ttk.Label] = []
    value_labels: List[ttk.Label] = []
    header_font = tkfont.Font(weight="bold")
    num_blocks = (len(display_headers) + COLS_PER_ROW - 1) // COLS_PER_ROW
    for i, h in enumerate(display_headers):
        block = i // COLS_PER_ROW
        header_row = block * ROWS_PER_BLOCK + 0
        data_row = block * ROWS_PER_BLOCK + 1
        c = i % COLS_PER_ROW
        lbl = ttk.Label(table_frame, text=h, font=header_font, padding=2)
        lbl.grid(row=header_row, column=c, sticky=tk.EW, padx=2, pady=2)
        header_labels.append(lbl)
        val_lbl = ttk.Label(table_frame, text="—", padding=2)
        val_lbl.grid(row=data_row, column=c, sticky=tk.EW, padx=2, pady=2)
        value_labels.append(val_lbl)
    for block in range(num_blocks):
        for s in range(SPACER_ROWS):
            r = block * ROWS_PER_BLOCK + 2 + s
            table_frame.rowconfigure(r, minsize=20)
    for c in range(COLS_PER_ROW):
        table_frame.columnconfigure(c, weight=1)

    message_count = [0]

    def process_queue() -> None:
        try:
            while True:
                item = data_queue.get_nowait()
                if item[0] == "error":
                    status_var.set(f"Error: {item[1]}")
                    break
                if item[0] == "row":
                    _, display_row = filter_row_for_display(headers, item[1])
                    message_count[0] += 1
                    count_var.set(f"Messages: {message_count[0]}")
                    status_var.set("Receiving")
                    for i, lbl in enumerate(value_labels):
                        if i < len(display_row):
                            val = display_row[i]
                            lbl.config(text=f"{val}" if isinstance(val, str) else f"{val:.4g}")
        except queue.Empty:
            pass
        root.after(100, process_queue)

    status_var.set("Subscribed – waiting for data...")
    root.after(100, process_queue)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
