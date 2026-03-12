#!/usr/bin/env python3
"""
Thermal HIL test: publish CSV rows and capture DUT responses.

Publishes CSV rows (payload = raw CSV line bytes) to IN_TOPIC (default: some/topic),
subscribes to OUT_TOPIC (default: other/topic), and writes received payload bytes
to OUT_FILE (default: thermal_example_module_out.csv).

Runs continuously for a configurable duration (default: 120 seconds), cycling through
CSV rows and counting published vs received responses. Generates HTML report with
pass/fail status based on response ratio.

Key point: zenoh Config uses json.dumps with an explicit connect endpoint, like:
  conf.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.1.10:1234"]))
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import zenoh


def build_conf(endpoint: str, mode: str = "peer", log_level: str = "info") -> zenoh.Config:
    """Create a zenoh.Config with logging and a single connect endpoint."""
    # Initiate logging (env can override); set a default to keep noise manageable.
    zenoh.init_log_from_env_or(log_level)

    conf = zenoh.Config()
    conf.insert_json5("mode", json.dumps(mode))
    conf.insert_json5("connect/endpoints", json.dumps([endpoint]))
    return conf

class CsvCapture:
    """Capture raw payload bytes to a file and print line-aware previews."""
    def __init__(
        self,
        out_file: Path,
        preview_max_lines_per_msg: int = 1,
        partial_preview_len: int = 120,
    ):
        self.out_file = out_file
        self.fp = None
        self.captured_msgs = 0
        self.captured_bytes = 0

        # Buffer for assembling full CSV lines across multiple samples
        self._buf = bytearray()

        # Preview behavior
        self.preview_max_lines_per_msg = preview_max_lines_per_msg
        self.partial_preview_len = partial_preview_len

    def open(self) -> None:
        self.out_file.parent.mkdir(parents=True, exist_ok=True)
        # Write binary so we never lose data on decoding issues.
        self.fp = self.out_file.open("wb")

    def close(self) -> None:
        if self.fp:
            self.fp.flush()
            self.fp.close()
            self.fp = None

        # Optional: show if there are leftover bytes that never ended with '\n'
        if self._buf:
            leftover = bytes(self._buf[: self.partial_preview_len]).decode(
                "utf-8",
                errors="replace",
            )
            print(f"[OUT] leftover bytes without newline ({len(self._buf)}): {leftover!r}")

    def listener(self, sample: zenoh.Sample) -> None:
        """
        Receives payload and appends as-is to output file.
        This matches the "byte stream" style where the firmware may publish 1 byte at a time.

        Console preview prints *complete CSV lines* when possible (split by '\\n').
        """
        payload_bytes = sample.payload.to_bytes()
        if not payload_bytes:
            return
        if self.fp is None:
            # Shouldn't happen, but guard anyway.
            return

        # Always persist raw bytes (lossless)
        self.fp.write(payload_bytes)
        self.fp.flush()

        self.captured_msgs += 1
        self.captured_bytes += len(payload_bytes)

        # Buffer for line-aware previewing
        self._buf.extend(payload_bytes)

        lines_printed = 0
        while lines_printed < self.preview_max_lines_per_msg:
            nl = self._buf.find(b"\n")
            if nl == -1:
                break  # no complete line yet

            line_bytes = bytes(self._buf[: nl + 1])
            del self._buf[: nl + 1]

            line_s = line_bytes.decode("utf-8", errors="replace").rstrip("\n")
            print(
                f"[OUT] +{len(payload_bytes)} bytes (total {self.captured_bytes}). "
                f"Line: {line_s!r}"
            )
            lines_printed += 1

        # If no newline found, show a partial preview of the buffered content
        if lines_printed == 0:
            partial = bytes(self._buf[: self.partial_preview_len])
            partial_s = partial.decode("utf-8", errors="replace")
            print(
                f"[OUT] +{len(payload_bytes)} bytes (total {self.captured_bytes}). "
                f"Partial: {partial_s!r}"
            )


def generate_html_report(
    stats: Dict[str, Any],
    args: argparse.Namespace,
    csv_rows: int,
    out_file: Path,
    passed: bool,
    response_ratio: float,
    min_response_ratio: float,
    elapsed_total: float,
) -> str:
    """Generate HTML report with test results and statistics."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_color = "#28a745" if passed else "#dc3545"
    status_text = "PASS" if passed else "FAIL"
    status_icon = "✅" if passed else "❌"
    
    response_ratio_color = "#28a745" if response_ratio >= min_response_ratio else "#dc3545"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thermal HIL Test Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid {status_color};
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 18px;
            color: white;
            background-color: {status_color};
            margin-bottom: 20px;
        }}
        .section {{
            margin: 30px 0;
        }}
        .section h2 {{
            color: #555;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #333;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .metric-value {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .metric-good {{
            color: #28a745;
        }}
        .metric-warning {{
            color: #ffc107;
        }}
        .metric-bad {{
            color: #dc3545;
        }}
        .info-box {{
            background-color: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .warning-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .error-box {{
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Thermal HIL Test Report</h1>
        <div class="status-badge">{status_icon} {status_text}</div>
        
        <div class="section">
            <h2>Test Summary</h2>
            <table>
                <tr>
                    <th>Test Status</th>
                    <td><span class="metric-value" style="color: {status_color}">{status_text}</span></td>
                </tr>
                <tr>
                    <th>Timestamp</th>
                    <td>{timestamp}</td>
                </tr>
                <tr>
                    <th>Duration</th>
                    <td class="metric-value">{elapsed_total:.2f} seconds</td>
                </tr>
                <tr>
                    <th>Response Ratio</th>
                    <td class="metric-value" style="color: {response_ratio_color}">{response_ratio:.1f}%</td>
                </tr>
                <tr>
                    <th>Minimum Required</th>
                    <td>{min_response_ratio:.1f}%</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Test Configuration</h2>
            <table>
                <tr>
                    <th>Endpoint</th>
                    <td>{args.endpoint}</td>
                </tr>
                <tr>
                    <th>Mode</th>
                    <td>{args.mode}</td>
                </tr>
                <tr>
                    <th>Input Topic</th>
                    <td>{args.in_topic}</td>
                </tr>
                <tr>
                    <th>Output Topic</th>
                    <td>{args.out_topic}</td>
                </tr>
                <tr>
                    <th>CSV File</th>
                    <td>{args.csv}</td>
                </tr>
                <tr>
                    <th>CSV Rows</th>
                    <td>{csv_rows}</td>
                </tr>
                <tr>
                    <th>Publish Rate</th>
                    <td>{args.hz} Hz</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Statistics</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Published Messages</td>
                    <td class="metric-value">{stats['published']}</td>
                </tr>
                <tr>
                    <td>Received Messages</td>
                    <td class="metric-value">{stats['received']}</td>
                </tr>
                <tr>
                    <td>Received Bytes</td>
                    <td class="metric-value">{stats['received_bytes']:,}</td>
                </tr>
                <tr>
                    <td>Publish Rate</td>
                    <td class="metric-value">{stats['publish_rate']:.2f} messages/second</td>
                </tr>
                <tr>
                    <td>Receive Rate</td>
                    <td class="metric-value">{stats['receive_rate']:.2f} messages/second</td>
                </tr>
                <tr>
                    <td>Response Ratio</td>
                    <td class="metric-value" style="color: {response_ratio_color}">{response_ratio:.1f}%</td>
                </tr>
            </table>
        </div>
"""
    
    if not passed:
        html += f"""
        <div class="section">
            <div class="error-box">
                <strong>Test Failed</strong><br>
                Response ratio ({response_ratio:.1f}%) is below the minimum required ({min_response_ratio:.1f}%).
                <br><br>
                <strong>Common causes:</strong>
                <ul>
                    <li>Module not publishing to OUT_TOPIC</li>
                    <li>Python not connected to same router/peer as module</li>
                    <li>Check endpoint: {args.endpoint}</li>
                    <li>Network connectivity issues</li>
                </ul>
            </div>
        </div>
"""
    else:
        html += f"""
        <div class="section">
            <div class="info-box">
                <strong>Test Passed</strong><br>
                Response ratio ({response_ratio:.1f}%) meets or exceeds the minimum required ({min_response_ratio:.1f}%).
            </div>
        </div>
"""
    
    html += f"""
        <div class="section">
            <h2>Output Files</h2>
            <table>
                <tr>
                    <th>File Type</th>
                    <th>Path</th>
                </tr>
                <tr>
                    <td>Output CSV</td>
                    <td><code>{out_file}</code></td>
                </tr>
                <tr>
                    <td>HTML Report</td>
                    <td><code>This file</code></td>
                </tr>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Thermal HIL Test Framework</p>
            <p>Report generated at: {timestamp}</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def read_csv_rows(csv_path: Path) -> list[bytes]:
    """
    Read CSV data rows as UTF-8 bytes, one line per row.

    Returns a list of bytes, each representing one CSV data row line.
    - Skips empty lines
    - Skips header row if it looks like it contains letters (simple heuristic)
    """
    lines = csv_path.read_text(encoding="utf-8", errors="replace").splitlines()
    rows: list[bytes] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # If it's a header (contains letters), skip it.
        if any(c.isalpha() for c in line):
            continue
        # Ensure newline at end so downstream can treat as "line"
        rows.append((line + "\n").encode("utf-8"))
    return rows


def main() -> int:
    """Parse args, publish CSV rows to zenoh, and capture output payloads."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="tcp/192.168.1.10:1234",
                    help="Zenoh connect endpoint, e.g. tcp/192.168.1.10:1234")
    ap.add_argument("--mode", default="peer", choices=["peer", "client"],
                    help="Zenoh mode")
    ap.add_argument("--in-topic", default="some/topic",
                    help="Topic to publish CSV rows to")
    ap.add_argument("--out-topic", default="other/topic",
                    help="Topic to subscribe to and capture outputs from")
    ap.add_argument(
        "--csv",
        type=Path,
        default=Path(__file__).parent.parent / "tests" / "csv_data" / "hil_dcfc_output_2.csv",
        help="Path to input CSV file (default: tests/csv_data/csv_data/hil_dcfc_output_2.csv)",
     )
    ap.add_argument("--out-file", type=Path, default=Path("thermal_example_module_out.csv"),
                    help="Output CSV file to write captured bytes into")
    ap.add_argument("--hz", type=float, default=1.0,
                    help="Publish rate in Hz")
    ap.add_argument("--duration", type=float, default=120.0,
                    help="Test duration in seconds (default: 120.0)")
    ap.add_argument("--grace-sec", type=float, default=3.0,
                    help="How long to keep listening after last publish (legacy, not used with --duration)")
    ap.add_argument("--min-response-ratio", type=float, default=100.0,
                    help="Minimum response ratio percentage for PASS (default: 100.0%%)")
    ap.add_argument("--report-dir", type=Path, default=Path.home() / "reports",
                    help="Directory for HTML report (default: ~/reports/)")
    ap.add_argument("--log", default="info",
                    help="Default zenoh log level if env not set (debug/info/warn/error)")
    args = ap.parse_args()

    rows = read_csv_rows(args.csv)
    if not rows:
        raise SystemExit(f"No data rows found in {args.csv} (did you only have a header?)")

    conf = build_conf(args.endpoint, mode=args.mode, log_level=args.log)

    print(f"Opening session to {args.endpoint} (mode={args.mode}) ...")
    print(
        f"Publishing CSV rows to {args.in_topic}, capturing {args.out_topic} "
        f"-> {args.out_file}"
    )
    print(f"Duration: {args.duration} seconds, Rate: {args.hz} Hz")
    capture = CsvCapture(args.out_file)
    capture.open()

    published = 0
    start_time = time.time()
    end_time = start_time + args.duration
    row_index = 0
    
    try:
        with zenoh.open(conf) as session:
            session.declare_subscriber(args.out_topic, capture.listener)
            pub = session.declare_publisher(args.in_topic, express=True)

            period = 1.0 / args.hz if args.hz > 0 else 0.0

            print(f"[INFO] Starting continuous publish loop for {args.duration} seconds at {args.hz} Hz...")
            print(f"[INFO] Cycling through {len(rows)} CSV rows...")
            
            while time.time() < end_time:
                # Select next CSV row (cycle through)
                row = rows[row_index % len(rows)]
                row_index += 1
                
                pub.put(row)
                published += 1
                
                # Print progress every 10 publishes or on first publish
                if published == 1 or published % 10 == 0:
                    elapsed = time.time() - start_time
                    remaining = max(0, end_time - time.time())
                    print(
                        f"[IN  {published:>4}] {len(row)} bytes. "
                        f"Elapsed: {elapsed:.1f}s, Remaining: {remaining:.1f}s. "
                        f"Line: {row.decode('utf-8', errors='replace').rstrip()[:60]!r}"
                    )
                
                # Sleep for rate control
                if period > 0:
                    time.sleep(period)
                else:
                    time.sleep(0.001)  # Minimal sleep to avoid busy-wait

            print(f"[INFO] Duration reached ({args.duration}s). Done publishing.")

    except KeyboardInterrupt:
        print("\n[WARN] Interrupted by user")
    finally:
        capture.close()

    elapsed_total = time.time() - start_time
    response_ratio = (capture.captured_msgs / published * 100) if published > 0 else 0.0
    
    # Determine pass/fail status
    passed = response_ratio >= args.min_response_ratio
    
    # Calculate statistics
    stats = {
        'published': published,
        'received': capture.captured_msgs,
        'received_bytes': capture.captured_bytes,
        'publish_rate': published / elapsed_total if elapsed_total > 0 else 0.0,
        'receive_rate': capture.captured_msgs / elapsed_total if elapsed_total > 0 else 0.0,
    }
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Duration: {elapsed_total:.1f} seconds")
    print(f"Published: {published} messages")
    print(f"Received: {capture.captured_msgs} messages")
    print(f"Received bytes: {capture.captured_bytes} bytes")
    print(f"Publish rate: {stats['publish_rate']:.2f} messages/second")
    print(f"Receive rate: {stats['receive_rate']:.2f} messages/second")
    print(f"Response ratio: {response_ratio:.1f}%")
    print(f"Minimum required: {args.min_response_ratio:.1f}%")
    print(f"Status: {'✅ PASS' if passed else '❌ FAIL'}")
    print(f"Output file: {args.out_file.resolve()}")
    print("=" * 70)
    
    # Generate HTML report
    args.report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report_file = args.report_dir / f"thermal_hil_test_{timestamp}.html"
    
    html_content = generate_html_report(
        stats=stats,
        args=args,
        csv_rows=len(rows),
        out_file=args.out_file,
        passed=passed,
        response_ratio=response_ratio,
        min_response_ratio=args.min_response_ratio,
        elapsed_total=elapsed_total,
    )
    html_report_file.write_text(html_content, encoding='utf-8')
    print(f"📄 HTML Report: {html_report_file}")
    
    if not passed:
        print()
        print("⚠️  TEST FAILED: Response ratio below minimum required.")
        print("   Common causes:")
        print("   1. Module not publishing to OUT_TOPIC")
        print("   2. Python not connected to same router/peer as module")
        print(f"   3. Check endpoint: {args.endpoint}")
        print("   4. Ensure firmware/base is connected to the same endpoint.")
        return 1
    
    if capture.captured_msgs == 0 or capture.captured_bytes == 0:
        print()
        print("[WARN] No outputs captured. Common causes:")
        print("  (1) Module not publishing to OUT_TOPIC, or")
        print("  (2) Python not connected to same router/peer as module.")
        print(f"  You used endpoint: {args.endpoint}")
        print("  Ensure firmware/base is connected to the same endpoint.")
    else:
        print()
        print(f"[OK] Wrote: {args.out_file.resolve()}")
    
    print()
    print("✅ TEST PASSED")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
