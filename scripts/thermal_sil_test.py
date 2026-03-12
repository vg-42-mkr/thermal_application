#!/usr/bin/env python3
"""
thermal_sil_test_v14.py

Publishes CSV rows (payload = raw CSV line bytes) to IN_TOPIC (default: some/topic),
subscribes to OUT_TOPIC (default: other/topic), and writes received payload bytes
to OUT_FILE (default: thermal_example_module_out.csv).

Key point: zenoh Config uses json.dumps with an explicit connect endpoint, like:
  conf.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.1.10:1234"]))
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Optional

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

def main() -> None:
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
        default=Path(
            "thermal_application/s32k388_test_bench_module/simple_thermal_sil_ctrl/example_data.csv"
        ),
        help="Path to input example_data.csv",
    )
    ap.add_argument("--out-file", type=Path, default=Path("thermal_example_module_out.csv"),
                    help="Output CSV file to write captured bytes into")
    ap.add_argument("--hz", type=float, default=1.0,
                    help="Publish rate in Hz")
    ap.add_argument("--grace-sec", type=float, default=3.0,
                    help="How long to keep listening after last publish")
    ap.add_argument("--log", default="info",
                    help="Default zenoh log level if env not set (debug/info/warn/error)")
    args = ap.parse_args()

    rows = read_csv_rows(args.csv)
    if not rows:
        raise SystemExit(f"No data rows found in {args.csv} (did you only have a header?)")

    conf = build_conf(args.endpoint, mode=args.mode, log_level=args.log)

    print(f"Opening session to {args.endpoint} (mode={args.mode}) ...")
    print(
        f"Publishing {len(rows)} rows to {args.in_topic}, capturing {args.out_topic} "
        f"-> {args.out_file}"
    )
    capture = CsvCapture(args.out_file)
    capture.open()

    published = 0
    try:
        with zenoh.open(conf) as session:
            session.declare_subscriber(args.out_topic, capture.listener)
            pub = session.declare_publisher(args.in_topic, express=True)

            period = 0.1 / args.hz if args.hz > 0 else 0.0

            print(f"[INFO] Publishing {len(rows)} rows at {args.hz} Hz...")
            for i, row in enumerate(rows, start=1):
                pub.put(row)
                published += 1
                print(
                    f"[IN  {i:>3}/{len(rows)}] {len(row)} bytes. Line: "
                    f"{row.decode('utf-8', errors='replace').rstrip()!r}"
                )
                if period > 0:
                    time.sleep(period)
                time.sleep(1)

            print("[INFO] Done publishing; waiting for outputs...")
            t_end = time.time() + args.grace_sec
            while time.time() < t_end:
                time.sleep(0.1)

    finally:
        capture.close()

    print(
        f"[INFO] Summary: published={published}, captured_msgs={capture.captured_msgs}, "
        f"captured_bytes={capture.captured_bytes}"
    )
    if capture.captured_msgs == 0 or capture.captured_bytes == 0:
        print("[WARN] No outputs captured. Common causes:")
        print("  (1) Module not publishing to OUT_TOPIC, or")
        print("  (2) Python not connected to same router/peer as module.")
        print(f"  You used endpoint: {args.endpoint}")
        print("  Ensure firmware/base is connected to the same endpoint.")

    else:
        print(f"[OK] Wrote: {args.out_file.resolve()}")

if __name__ == "__main__":
    main()
