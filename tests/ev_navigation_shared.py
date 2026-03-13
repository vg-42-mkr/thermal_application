"""
Shared utilities and constants for EV navigation UIs (Death Valley, Tahoe, etc.).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

WEATHER_LABELS: dict[int, str] = {
    0: "Clear",
    1: "Cloudy",
    2: "Rain",
    3: "Snow",
    4: "Fog",
}

WEATHER_ICONS: dict[int, str] = {
    0: "☀️",
    1: "⛅",
    2: "🌧️",
    3: "❄️",
    4: "🌫️",
}

# Simulation
STEP_SEC = 1.0
CHARGE_STEP_PCT = 1
DESTINATION_COUNTDOWN_SEC = 10
EMPTY_RECOVERY_DELAY_SEC = 10
DEFAULT_MAX_RANGE_KM = 360
AVG_SPEED_KMH = 80.0

# -----------------------------------------------------------------------------
# Route helpers
# -----------------------------------------------------------------------------


def load_route(route_json_path: Path) -> dict[str, Any]:
    """Load route data from a JSON file."""
    with open(route_json_path, encoding="utf-8") as f:
        return json.load(f)


def make_round_trip(route_data: dict[str, Any]) -> dict[str, Any]:
    """
    Append return leg (reverse of waypoints) so route goes back to origin.
    Mutates and returns route_data.
    """
    waypoints = route_data["waypoints"]
    n = len(waypoints)
    if n < 2:
        return route_data
    one_way_km = route_data["total_km"]
    total_km_so_far = one_way_km
    return_waypoints = []
    for j in range(n - 2, -1, -1):
        wp = dict(waypoints[j])
        km_back = waypoints[j + 1]["cumulative_km"] - waypoints[j]["cumulative_km"]
        total_km_so_far += km_back
        wp["cumulative_km"] = round(total_km_so_far, 2)
        return_waypoints.append(wp)
    route_data["waypoints"] = waypoints + return_waypoints
    route_data["total_km"] = round(total_km_so_far, 0)
    return route_data


def build_route_payload(route_data: dict[str, Any]) -> dict[str, Any]:
    """Build the payload for the frontend route-data JSON (escape for </script>)."""
    return {
        "waypoints": route_data["waypoints"],
        "chargers": route_data["chargers"],
        "weatherLabels": WEATHER_LABELS,
        "weatherIcons": WEATHER_ICONS,
        "total_km": route_data["total_km"],
        "max_range_km": route_data.get("max_range_km", DEFAULT_MAX_RANGE_KM),
        "origin": route_data["origin"],
        "destination": route_data["destination"],
    }
