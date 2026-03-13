"""
EV Navigation Flask app factory and simulation loop.
Used by route-specific UIs (e.g. Death Valley, Tahoe).

APIs:
  GET  /             - Index page (HTML)
  GET  /api/state    - Current state (JSON): current_index, playing, soc_pct, charging,
                       charge_progress, recovery_charging, empty_recovery_seconds_left,
                       destination_reached, destination_countdown_sec, range_km,
                       trip_remaining_km, eta_min, total_km, max_range_km, len_waypoints
  GET  /api/play     - Start simulation
  GET  /api/pause    - Pause simulation
  GET  /api/reset    - Reset to start (index 0, SOC 100%)
  GET  /api/speed?x= - Set speed 1–8 (e.g. ?x=8)
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

from tests.ev_navigation_shared import (
    AVG_SPEED_KMH,
    CHARGE_STEP_PCT,
    DEFAULT_MAX_RANGE_KM,
    DESTINATION_COUNTDOWN_SEC,
    EMPTY_RECOVERY_DELAY_SEC,
    STEP_SEC,
    build_route_payload,
)

# -----------------------------------------------------------------------------
# Default config
# -----------------------------------------------------------------------------

DEFAULT_CONFIG: dict[str, Any] = {
    "title": "EV Live Navigation",
    "route_label": "Round trip",
    "api_base_url": "http://127.0.0.1:5004",
    "footer_default": "—",
    "no_route_msg": "Run with --web to load route.",
    "auto_play": True,
}


def _initial_state(*, auto_play: bool = True) -> dict[str, Any]:
    return {
        "current_index": 0,
        "playing": auto_play,
        "speed_index": 8,
        "soc_pct": 100.0,
        "charging_at_end": False,
        "charge_progress": 0,
        "empty_recovery_at": None,
        "recovery_charging": False,
        "destination_reached_at": None,
    }


def _run_simulation(
    state: dict[str, Any],
    state_lock: threading.Lock,
    waypoints: list[dict],
    route_data: dict[str, Any],
) -> None:
    n = len(waypoints)
    max_range_km = route_data.get("max_range_km", DEFAULT_MAX_RANGE_KM)
    while True:
        with state_lock:
            speed = max(1, state["speed_index"])
        time.sleep(STEP_SEC / speed)
        with state_lock:
            if not state["playing"]:
                ear = state.get("empty_recovery_at")
                if ear is not None and time.time() >= ear:
                    state["recovery_charging"] = True
                    state["charge_progress"] = 0
                    state["empty_recovery_at"] = None
                    state["playing"] = True
                continue
            idx = state["current_index"]
            if state["charging_at_end"]:
                state["charge_progress"] = min(100, state["charge_progress"] + CHARGE_STEP_PCT)
                state["soc_pct"] = state["charge_progress"]
                if state["charge_progress"] >= 100:
                    state["charging_at_end"] = False
                    state["charge_progress"] = 0
                    state["current_index"] = 0
                    state["soc_pct"] = 100.0
                continue
            if state.get("recovery_charging"):
                state["charge_progress"] = min(100, state["charge_progress"] + CHARGE_STEP_PCT)
                state["soc_pct"] = state["charge_progress"]
                if state["charge_progress"] >= 100:
                    state["recovery_charging"] = False
                    state["charge_progress"] = 0
                    state["soc_pct"] = 100.0
                continue
            first_leg_end = n // 2 - 1
            if idx == first_leg_end and first_leg_end < n - 1:
                dra = state.get("destination_reached_at")
                if dra is None:
                    state["destination_reached_at"] = time.time()
                    continue
                if time.time() - dra >= DESTINATION_COUNTDOWN_SEC:
                    state["destination_reached_at"] = None
                    state["current_index"] = n // 2
                continue
            if idx >= n - 1:
                dra = state.get("destination_reached_at")
                if dra is None:
                    state["destination_reached_at"] = time.time()
                    continue
                if time.time() - dra >= DESTINATION_COUNTDOWN_SEC:
                    state["charging_at_end"] = True
                    state["charge_progress"] = state["soc_pct"]
                    state["destination_reached_at"] = None
                continue
            next_idx = idx + 1
            state["current_index"] = next_idx
            w = waypoints[next_idx]
            prev = waypoints[next_idx - 1]
            delta_km = w["cumulative_km"] - prev["cumulative_km"]
            state["soc_pct"] = max(0, state["soc_pct"] - (delta_km / max_range_km) * 100)
            if state["soc_pct"] <= 0:
                state["playing"] = False
                state["empty_recovery_at"] = time.time() + EMPTY_RECOVERY_DELAY_SEC


def _load_template() -> str:
    """Load HTML template from templates/ev_navigation_index.html."""
    path = Path(__file__).resolve().parent / "templates" / "ev_navigation_index.html"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "<!DOCTYPE html><html><body><p>Template not found.</p></body></html>"


def create_app(route_data: dict[str, Any], config: dict[str, Any] | None = None):
    """
    Create and return a Flask app for EV navigation.
    config overrides: title, route_label, api_base_url, footer_default, no_route_msg, auto_play.
    """
    from flask import Flask, jsonify, request

    cfg = {**DEFAULT_CONFIG, **(config or {})}
    template_html = _load_template()
    auto_play = cfg.get("auto_play", True)
    waypoints = route_data["waypoints"]
    n = len(waypoints)
    max_range_km = route_data.get("max_range_km", DEFAULT_MAX_RANGE_KM)
    state_lock = threading.Lock()
    state = _initial_state(auto_play=auto_play)

    def render_index(template_html: str) -> str:
        payload = build_route_payload(route_data)
        route_data_js = json.dumps(payload).replace("</", "<\\/")
        total_km = route_data["total_km"]
        len_waypoints = len(waypoints)
        return (
            template_html.replace("__TITLE__", cfg["title"])
            .replace("__ROUTE_LABEL__", cfg["route_label"])
            .replace("__TOTAL_KM__", str(total_km))
            .replace("__LEN_WAYPOINTS__", str(len_waypoints))
            .replace("__ROUTE_DATA_JS__", route_data_js)
            .replace("__API_BASE_URL__", cfg["api_base_url"])
            .replace("__FOOTER_DEFAULT__", cfg["footer_default"])
            .replace("__NO_ROUTE_MSG__", cfg["no_route_msg"])
        )

    threading.Thread(
        target=_run_simulation,
        args=(state, state_lock, waypoints, route_data),
        daemon=True,
    ).start()

    app = Flask(__name__)
    app.config["EV_NAV_TEMPLATE"] = template_html

    @app.route("/")
    def index() -> str:
        return render_index(app.config["EV_NAV_TEMPLATE"])

    @app.route("/api/state")
    def api_state() -> str:
        with state_lock:
            idx = state["current_index"]
            w = waypoints[idx] if 0 <= idx < n else None
            cum_km = w["cumulative_km"] if w else 0
            one_way_km = route_data.get("one_way_km", route_data["total_km"] // 2)
            if idx < n // 2:
                trip_remaining_km = max(0, one_way_km - cum_km)
                leg_total_km = one_way_km
            else:
                trip_remaining_km = max(0, route_data["total_km"] - cum_km)
                leg_total_km = one_way_km
            range_km = (state["soc_pct"] / 100.0) * max_range_km
            eta_min = (trip_remaining_km / AVG_SPEED_KMH * 60) if trip_remaining_km > 0 else 0
            recovery = state.get("recovery_charging", False)
            charging = state.get("charging_at_end", False) or recovery
            charge_progress = state.get("charge_progress", 0)
            ear = state.get("empty_recovery_at")
            empty_recovery_seconds_left = max(0, int(ear - time.time())) if ear is not None else None
            dra = state.get("destination_reached_at")
            destination_reached = (
                dra is not None
                and not state.get("charging_at_end", False)
                and (idx == n - 1 or idx == n // 2 - 1)
            )
            destination_countdown_sec = None
            if destination_reached and dra is not None:
                elapsed = int(time.time() - dra)
                destination_countdown_sec = max(0, min(10, 10 - elapsed))
        return jsonify({
            "current_index": idx,
            "playing": state["playing"],
            "speed_index": state["speed_index"],
            "soc_pct": state["soc_pct"],
            "charging": charging,
            "charge_progress": charge_progress,
            "recovery_charging": recovery,
            "empty_recovery_seconds_left": empty_recovery_seconds_left,
            "destination_reached": destination_reached,
            "destination_countdown_sec": destination_countdown_sec,
            "range_km": range_km,
            "trip_remaining_km": trip_remaining_km,
            "eta_min": eta_min,
            "total_km": leg_total_km,
            "max_range_km": max_range_km,
            "len_waypoints": n,
        })

    @app.route("/api/play", methods=["GET", "POST"])
    def api_play() -> str:
        with state_lock:
            state["playing"] = True
        return jsonify({"ok": True})

    @app.route("/api/pause", methods=["GET", "POST"])
    def api_pause() -> str:
        with state_lock:
            state["playing"] = False
        return jsonify({"ok": True})

    @app.route("/api/reset", methods=["GET", "POST"])
    def api_reset() -> str:
        with state_lock:
            state["current_index"] = 0
            state["soc_pct"] = 100.0
            state["playing"] = False
            state["charging_at_end"] = False
            state["charge_progress"] = 0
            state["empty_recovery_at"] = None
            state["recovery_charging"] = False
            state["destination_reached_at"] = None
        return jsonify({"ok": True})

    @app.route("/api/speed")
    def api_speed() -> str:
        x = request.args.get("x", "1")
        try:
            xi = max(1, min(8, int(x)))
            with state_lock:
                state["speed_index"] = xi
            return jsonify({"ok": True, "speed": xi})
        except ValueError:
            return jsonify({"ok": False}), 400

    return app
