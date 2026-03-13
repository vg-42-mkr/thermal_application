#!/usr/bin/env python3
"""
EV Live Navigation: Sunnyvale → Death Valley National Park.
Run: python tests/ev_navigation_sunnyvale_deathvalley_ui.py --web
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure project root is on path when run as script
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tests.ev_navigation_app import create_app
from tests.ev_navigation_shared import load_route, make_round_trip

ROUTE_JSON = Path(__file__).resolve().parent / "csv_data" / "sunnyvale_deathvalley_route.json"
DEFAULT_PORT = 5004


def main() -> int:
    parser = argparse.ArgumentParser(description="EV Live Navigation: Sunnyvale → Death Valley")
    parser.add_argument("--web", action="store_true", help="Run browser UI")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port for web UI")
    args = parser.parse_args()

    if not args.web:
        print("Use --web to run. Example: python tests/ev_navigation_sunnyvale_deathvalley_ui.py --web")
        return 0

    try:
        from flask import Flask
    except ImportError:
        print("Flask is required: pip install flask")
        return 1

    route_data = load_route(ROUTE_JSON)
    route_data["one_way_km"] = route_data["total_km"]
    route_data = make_round_trip(route_data)

    config = {
        "title": "EV Live — Sunnyvale → Death Valley",
        "route_label": "Sunnyvale → Death Valley → Sunnyvale (round trip)",
        "api_base_url": f"http://127.0.0.1:{args.port}",
        "footer_default": "Sunnyvale",
        "no_route_msg": "Run: python tests/ev_navigation_sunnyvale_deathvalley_ui.py --web",
        "auto_play": True,
    }

    app = create_app(route_data, config)
    url = config["api_base_url"]

    def open_browser() -> None:
        time.sleep(1.0)
        import webbrowser
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    print(f"EV Sunnyvale → Death Valley UI: {url}")
    print("Close with Ctrl+C.")
    app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
