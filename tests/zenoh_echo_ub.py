#!/usr/bin/env python3
"""
Zenoh echo: subscribe to one topic and republish each message to another topic.

Useful when no DUT is available: test_thermal_hil_1.py publishes to --in-topic,
this script echoes to --out-topic, and the Live UI (and the test script) receive
on --out-topic.

Requires a Zenoh router listening at --endpoint, e.g.:
  zenohd --listen tcp/0.0.0.0:1234

Usage:
  python tests/zenoh_echo.py
  python tests/zenoh_echo.py --endpoint tcp/192.168.1.10:1234 --in-topic some/topic --out-topic other/topic
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Optional

import zenoh


def build_conf(endpoint: str, mode: str = "peer", log_level: str = "warn") -> zenoh.Config:
    zenoh.init_log_from_env_or(log_level)
    conf = zenoh.Config()
    conf.insert_json5("mode", json.dumps(mode))
    conf.insert_json5("connect/endpoints", json.dumps([endpoint]))
    return conf


def main() -> int:
    ap = argparse.ArgumentParser(description="Echo Zenoh: subscribe in-topic → publish out-topic")
    ap.add_argument("--endpoint", default="tcp/192.168.1.10:1234", help="Zenoh connect endpoint")
    ap.add_argument("--mode", default="peer", choices=["peer", "client"], help="Zenoh mode")
    ap.add_argument("--in-topic", default="some/topic", help="Topic to subscribe to (input)")
    ap.add_argument("--out-topic", default="other/topic", help="Topic to publish to (echo output)")
    ap.add_argument("--log", default="warn", help="Zenoh log level")
    args = ap.parse_args()

    conf = build_conf(args.endpoint, mode=args.mode, log_level=args.log)
    session: Optional[zenoh.Session] = None

    def on_sample(sample: zenoh.Sample) -> None:
        payload = sample.payload
        if session and pub:
            pub.put(payload)
            print(".", end="", flush=True)

    try:
        session = zenoh.open(conf)
        pub = session.declare_publisher(args.out_topic, express=True)
        session.declare_subscriber(args.in_topic, on_sample)
        print(
            f"Echo: {args.in_topic} → {args.out_topic} @ {args.endpoint} (Ctrl+C to stop)",
            flush=True,
        )
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if session:
            session.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
