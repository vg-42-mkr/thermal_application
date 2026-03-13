#!/usr/bin/env python3
"""
EV Live Navigation: Sunnyvale → South Lake Tahoe (real-world route).
Route from sunnyvale_tahoe_route.json: 20 waypoints, 5 chargers, weather, wind, elevation.
Leaflet map (teal polyline, car marker, purple charger markers), Play/Pause/Reset, 1×–8× speed.
Sidebar: SOC, range, trip remaining, ETA, weather icon, wind arrow & direction, elevation profile (You point), chargers list.
Run: python tests/ev_navigation_sunnyvale_tahoe_ui.py --web
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from pathlib import Path

# Route data path (expanduser so ~ works if present)
ROUTE_JSON = Path(__file__).resolve().parent.joinpath("csv_data", "sunnyvale_tahoe_route.json").expanduser().resolve()

WEATHER_LABELS = {
    0: "Clear",
    1: "Cloudy",
    2: "Rain",
    3: "Snow",
    4: "Fog",
}
WEATHER_ICONS = {0: "☀️", 1: "⛅", 2: "🌧️", 3: "❄️", 4: "🌫️"}


def _load_route() -> dict:
    with open(ROUTE_JSON, encoding="utf-8") as f:
        return json.load(f)


def _web_html(route_data: dict) -> str:
    waypoints = route_data["waypoints"]
    chargers = route_data["chargers"]
    origin = route_data["origin"]
    destination = route_data["destination"]
    total_km = route_data["total_km"]
    max_range_km = route_data.get("max_range_km", 360)
    len_waypoints = len(waypoints)
    route_data_js = json.dumps({
        "waypoints": waypoints,
        "chargers": chargers,
        "weatherLabels": WEATHER_LABELS,
        "weatherIcons": WEATHER_ICONS,
        "total_km": total_km,
        "max_range_km": max_range_km,
        "origin": origin,
        "destination": destination,
    }).replace("</", "<\\/")
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EV Live — Sunnyvale → South Lake Tahoe</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {
      --bg: #0c0f14;
      --card: #151a22;
      --border: #2a3342;
      --accent: #22c3a6;
      --accent2: #7c3aed;
      --text: #e2e8f0;
      --muted: #94a3b8;
      --danger: #f43f5e;
      --elev: #a78bfa;
      --wind: #38bdf8;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: 'DM Sans', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
    .app { display: grid; grid-template-columns: 1fr 380px; grid-template-rows: auto 1fr auto; gap: 0; min-height: 100vh; }
    @media (max-width: 1024px) { .app { grid-template-columns: 1fr; } }
    .header { grid-column: 1 / -1; padding: 14px 20px; background: linear-gradient(135deg, var(--card) 0%, #1a2230 100%); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
    .header h1 { margin: 0; font-size: 1.35rem; font-weight: 700; background: linear-gradient(90deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .header .route-label { font-size: 0.9rem; color: var(--muted); }
    #map { height: 100%; min-height: 400px; }
    .sidebar { background: var(--card); border-left: 1px solid var(--border); padding: 16px; overflow-y: auto; }
    .controls { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
    .btn { padding: 8px 14px; border-radius: 8px; border: 1px solid var(--border); background: var(--card); color: var(--text); cursor: pointer; font-size: 0.9rem; }
    .btn:hover { background: #1e2530; }
    .btn.primary { background: var(--accent); color: var(--bg); border-color: var(--accent); }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .progress-block { margin: 12px 0; }
    .progress-block label { display: block; font-size: 0.85rem; color: var(--muted); margin-bottom: 4px; }
    .progress-track { height: 22px; background: #1e2530; border-radius: 11px; overflow: hidden; border: 1px solid var(--border); }
    .progress-fill { height: 100%; border-radius: 10px; transition: width 0.2s ease; }
    .progress-fill.soc-low { background: var(--danger); }
    .progress-fill.soc-mid { background: #eab308; }
    .progress-fill.soc-high { background: var(--accent); }
    .progress-text { font-size: 0.8rem; color: var(--muted); margin-top: 2px; }
    .stat { font-size: 0.9rem; color: var(--muted); margin: 6px 0; }
    .stat span { color: var(--text); }
    .chart-wrap { height: 180px; margin-top: 12px; }
    .car-waypoint-label { font-size: 0.85rem; color: var(--accent); font-weight: 600; padding: 2px 6px; background: rgba(12,15,20,0.9); border-radius: 4px; }
    .card-title { font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin: 14px 0 6px; }
    .card-title:first-of-type { margin-top: 0; }
    .weather-row { display: flex; align-items: center; gap: 8px; margin: 6px 0; }
    .weather-icon { font-size: 1.5rem; }
    .weather-label { color: var(--text); }
    .ambient-val { color: var(--accent2); font-weight: 600; }
    .wind-row { display: flex; align-items: center; gap: 6px; margin: 6px 0; }
    .wind-arrow { display: inline-block; font-size: 1.2rem; color: var(--wind); transition: transform 0.2s; }
    .live-card { background: rgba(30, 37, 48, 0.6); border: 1px solid var(--border); border-radius: 10px; padding: 12px; margin: 10px 0; }
    .live-card h3 { margin: 0 0 10px; font-size: 0.8rem; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 8px; }
    .live-badge { font-size: 0.65rem; background: var(--accent); color: var(--bg); padding: 2px 6px; border-radius: 4px; font-weight: 700; }
    .live-weather-grid { display: grid; gap: 8px; }
    .live-weather-row { display: flex; align-items: center; justify-content: space-between; font-size: 0.9rem; }
    .live-weather-row .val { color: var(--text); font-weight: 500; }
    .live-elev-now { font-size: 0.85rem; color: var(--elev); margin-bottom: 8px; }
    .live-elev-now strong { color: var(--text); }
    .live-card .chart-wrap { min-height: 180px; height: 180px; }
    .nav-plan-row { font-size: 0.9rem; margin: 4px 0; }
    .nav-plan-row .muted { color: var(--muted); margin-right: 8px; }
    .charger-list { font-size: 0.85rem; }
    .charger-item { padding: 6px 0; border-bottom: 1px solid var(--border); color: var(--text); }
    .charger-item.passed { color: var(--muted); opacity: 0.8; }
    .charger-item .power { color: var(--accent2); margin-left: 6px; }
    .footer { grid-column: 1 / -1; padding: 10px 20px; background: var(--card); border-top: 1px solid var(--border); font-size: 0.9rem; color: var(--muted); }
    .footer span { color: var(--accent); font-weight: 600; }
  </style>
</head>
<body>
  <div class="app">
    <header class="header">
      <h1>EV Live — Sunnyvale → South Lake Tahoe</h1>
      <div class="route-label">Sunnyvale → South Lake Tahoe · __TOTAL_KM__ km · Max range __MAX_RANGE_KM__ km</div>
      <div class="controls">
        <button class="btn primary" id="btnPlay">Play</button>
        <button class="btn" id="btnPause">Pause</button>
        <button class="btn" id="btnReset">Reset</button>
        <span class="btn" id="tripProgress">0 / __LEN_WAYPOINTS__</span>
        <select id="speedSelect">
          <option value="1">1×</option>
          <option value="2">2×</option>
          <option value="4">4×</option>
          <option value="8" selected>8×</option>
        </select>
      </div>
    </header>
    <div id="map"></div>
    <aside class="sidebar">
      <div class="live-card" id="navPlanCard">
        <h3><span class="live-badge">Route</span> Navigation plan</h3>
        <div class="nav-plan-row"><span class="muted">From</span> <strong id="navOrigin">—</strong></div>
        <div class="nav-plan-row"><span class="muted">To</span> <strong id="navDestination">—</strong></div>
        <div class="nav-plan-row"><span class="muted">Distance</span> <strong id="navTotalKm">—</strong> km · <strong id="navWaypoints">—</strong> waypoints</div>
      </div>
      <div class="card-title">Battery &amp; range</div>
      <div class="progress-block">
        <label>Battery SOC</label>
        <div class="progress-track">
          <div class="progress-fill soc-high" id="socFill" style="width: 100%;"></div>
        </div>
        <div class="progress-text" id="socText">100%</div>
      </div>
      <div class="progress-block" id="chargingBlock" style="display: none;">
        <label>Charging at destination</label>
        <div class="progress-track">
          <div class="progress-fill soc-mid" id="chargingFill" style="width: 0%;"></div>
        </div>
        <div class="progress-text" id="chargingText">0%</div>
      </div>
      <div class="stat">Est. range: <span id="rangeKm">—</span> km</div>
      <div class="stat">Trip remaining: <span id="tripRemainingKm">—</span> km</div>
      <div class="stat">ETA: <span id="etaMin">—</span> min</div>
      <div class="live-card">
        <h3><span class="live-badge">Live</span> Weather &amp; Wind</h3>
        <div class="live-weather-grid">
          <div class="live-weather-row">
            <span><span id="weatherIcon" class="weather-icon">☀️</span> <span id="weatherVal" class="weather-label">—</span></span>
            <span id="ambientVal" class="val ambient-val">— °C</span>
          </div>
          <div class="wind-row live-weather-row">
            <span><span id="windArrow" class="wind-arrow" title="Wind from">↑</span> <span id="windVal">—</span> km/h</span>
            <span id="windDir" class="val">—</span>
          </div>
        </div>
      </div>
      <div class="live-card">
        <h3><span class="live-badge">Live</span> Elevation Chart</h3>
        <div class="live-elev-now">Now: <strong id="elevVal">—</strong> m</div>
        <div class="chart-wrap"><canvas id="elevChart"></canvas></div>
      </div>
      <div class="card-title">Chargers along route</div>
      <div id="chargerList" class="charger-list"></div>
    </aside>
  </div>
  <footer class="footer">
    <span id="footerLocation">Sunnyvale</span>
  </footer>
  <script type="application/json" id="route-data">__ROUTE_DATA_JS__</script>
  <script>
    var routeData = (function() {
      var el = document.getElementById('route-data');
      if (!el || !el.textContent) return {};
      try { return JSON.parse(el.textContent); } catch (e) { return {}; }
    })();
    var waypoints = Array.isArray(routeData.waypoints) ? routeData.waypoints : [];
    var chargers = Array.isArray(routeData.chargers) ? routeData.chargers : [];
    var weatherLabels = routeData.weatherLabels && typeof routeData.weatherLabels === 'object' ? routeData.weatherLabels : { 0: 'Clear', 1: 'Cloudy', 2: 'Rain', 3: 'Snow', 4: 'Fog' };
    var weatherIcons = routeData.weatherIcons && typeof routeData.weatherIcons === 'object' ? routeData.weatherIcons : { 0: '☀️', 1: '⛅', 2: '🌧️', 3: '❄️', 4: '🌫️' };
    var totalKm = typeof routeData.total_km === 'number' ? routeData.total_km : 354;
    var maxRangeKm = typeof routeData.max_range_km === 'number' ? routeData.max_range_km : 360;
    var map, routeLine, carMarker, carTooltip;
    var currentIndex = 0;
    var elevChart = null;

    function setText(id, text) { var el = document.getElementById(id); if (el) el.textContent = text; }

    function windDirFromDeg(deg) {
      if (deg == null) return '—';
      var d = ['N','NE','E','SE','S','SW','W','NW'];
      var i = Math.round(((deg % 360) + 360) % 360 / 45) % 8;
      return d[i];
    }

    function initMap() {
      var start = [waypoints[0].lat, waypoints[0].lon];
      map = L.map('map').setView(start, 8);
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap, © CARTO' }).addTo(map);
      var latlngs = waypoints.map(function(w) { return [w.lat, w.lon]; });
      routeLine = L.polyline(latlngs, { color: '#14b8a6', weight: 4, opacity: 0.8 }).addTo(map);
      map.fitBounds(routeLine.getBounds(), { padding: [20, 20] });
      var carIcon = L.divIcon({ className: 'car-marker', html: '<div style="width:16px;height:16px;border-radius:50%;background:#14b8a6;border:2px solid #0c0f14;box-shadow:0 0 6px rgba(20,184,166,0.8);"></div>', iconSize: [16, 16], iconAnchor: [8, 8] });
      carMarker = L.marker([waypoints[0].lat, waypoints[0].lon], { icon: carIcon }).addTo(map);
      carTooltip = L.tooltip({ permanent: true, direction: 'top', className: 'car-waypoint-label' }).setContent(waypoints[0].label && waypoints[0].label.trim() ? waypoints[0].label.trim() : '');
      carMarker.bindTooltip(carTooltip);
      chargers.forEach(function(c) {
        var popup = (c.label || 'Charger') + (c.power_kw ? ' · ' + c.power_kw + ' kW' : '');
        L.marker([c.lat, c.lon], { icon: L.divIcon({ className: 'charger-marker', html: '<div style="width:20px;height:20px;border-radius:4px;background:#7c3aed;color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;">⚡</div>', iconSize: [20, 20], iconAnchor: [10, 10] }) }).addTo(map).bindPopup(popup);
      });
    }

    function ensureElevChart() {
      if (elevChart) return;
      var canvas = document.getElementById('elevChart');
      if (!canvas || waypoints.length === 0) return;
      var ctx = canvas.getContext('2d');
      var elevData = waypoints.map(function(w) { return { x: w.cumulative_km, y: w.elevation_m }; });
      elevChart = new Chart(ctx, {
        type: 'line',
        data: {
          datasets: [
            { label: 'Elevation (m)', data: elevData, borderColor: '#a78bfa', backgroundColor: 'rgba(167,139,250,0.2)', fill: true, tension: 0.3, pointRadius: 0 },
            { label: 'You', data: [], borderColor: '#22c3a6', backgroundColor: 'transparent', pointRadius: 6, pointBackgroundColor: '#22c3a6', pointBorderColor: '#0c0f14', pointBorderWidth: 2 }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false, animation: { duration: 0 }, scales: { x: { type: 'linear', ticks: { color: '#94a3b8', maxTicksLimit: 8 }, grid: { color: '#2a3342' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: '#2a3342' } } }, plugins: { legend: { labels: { color: '#e2e8f0' } } } }
      });
    }

    function buildInitialState() {
      if (waypoints.length === 0) return null;
      var w0 = waypoints[0];
      var tripRem = totalKm - (w0.cumulative_km || 0);
      return { current_index: 0, playing: false, speed_index: 8, soc_pct: 100, range_km: maxRangeKm, trip_remaining_km: tripRem, eta_min: tripRem / 80 * 60 };
    }

    function updateUI(data) {
      if (!data || waypoints.length === 0) return;
      currentIndex = data.current_index;
      var w = waypoints[currentIndex];
      if (!w) return;
      carMarker.setLatLng([w.lat, w.lon]);
      var labelText = (w.label && w.label.trim()) ? w.label.trim() : '';
      carTooltip.setContent(labelText);
      if (labelText) carMarker.openTooltip(); else carMarker.closeTooltip();
      setText('tripProgress', currentIndex + ' / ' + waypoints.length);
      setText('footerLocation', labelText || '—');
      var soc = Math.max(0, Math.min(100, data.soc_pct));
      var fillEl = document.getElementById('socFill');
      var textEl = document.getElementById('socText');
      if (fillEl) fillEl.style.width = soc.toFixed(1) + '%';
      if (fillEl) fillEl.className = 'progress-fill ' + (soc <= 20 ? 'soc-low' : soc <= 50 ? 'soc-mid' : 'soc-high');
      if (textEl) textEl.textContent = soc.toFixed(1) + '%';
      setText('rangeKm', data.range_km != null ? Math.round(data.range_km) : '—');
      setText('tripRemainingKm', data.trip_remaining_km != null ? Math.round(data.trip_remaining_km) : '—');
      setText('etaMin', data.eta_min != null ? Math.round(data.eta_min) : '—');
      var chargingBlock = document.getElementById('chargingBlock');
      var chargingFill = document.getElementById('chargingFill');
      var chargingText = document.getElementById('chargingText');
      if (data.charging && chargingBlock && chargingFill && chargingText) {
        chargingBlock.style.display = 'block';
        var pct = Math.max(0, Math.min(100, data.charge_progress != null ? data.charge_progress : 0));
        chargingFill.style.width = pct.toFixed(0) + '%';
        chargingText.textContent = pct.toFixed(0) + '%';
      } else if (chargingBlock) {
        chargingBlock.style.display = 'none';
      }
      var weatherCode = w.weather_code != null ? w.weather_code : 0;
      setText('weatherIcon', (weatherIcons[weatherCode] != null ? weatherIcons[weatherCode] : weatherIcons[0]) || '☀️');
      setText('weatherVal', (weatherLabels[weatherCode] != null ? weatherLabels[weatherCode] : weatherLabels[0]) || 'Clear');
      setText('ambientVal', (w.ambient_c != null ? w.ambient_c : '—') + ' °C');
      setText('windVal', w.wind_speed_kmh != null ? w.wind_speed_kmh : '—');
      setText('windDir', windDirFromDeg(w.wind_deg));
      var windArrow = document.getElementById('windArrow');
      if (windArrow) { windArrow.style.transform = 'rotate(' + (w.wind_deg != null ? w.wind_deg : 0) + 'deg)'; windArrow.title = 'Wind from ' + windDirFromDeg(w.wind_deg); }
      setText('elevVal', w.elevation_m != null ? Math.round(w.elevation_m) : '—');
      ensureElevChart();
      if (elevChart && elevChart.data.datasets[1]) {
        elevChart.data.datasets[1].data = [{ x: w.cumulative_km, y: w.elevation_m }];
        elevChart.update('none');
      }
      var listEl = document.getElementById('chargerList');
      var curKm = w.cumulative_km;
      listEl.innerHTML = chargers.map(function(c) {
        var km = c.cumulative_km != null ? c.cumulative_km : 0;
        var ahead = km - curKm;
        var passed = ahead <= 0;
        var power = c.power_kw ? ' <span class="power">' + c.power_kw + ' kW</span>' : '';
        return '<div class="charger-item ' + (passed ? 'passed' : '') + '">' + (c.label || 'Charger') + power + ' · ' + (passed ? 'Passed' : ahead.toFixed(0) + ' km ahead') + '</div>';
      }).join('');
    }

    function poll() {
      var url = (window.location.origin || 'http://127.0.0.1:5003') + '/api/state';
      fetch(url).then(function(r) { return r.json(); }).then(updateUI).catch(function() {});
    }

    document.getElementById('btnPlay').onclick = function() { fetch((window.location.origin || 'http://127.0.0.1:5003') + '/api/play').then(poll); };
    document.getElementById('btnPause').onclick = function() { fetch((window.location.origin || 'http://127.0.0.1:5003') + '/api/pause').then(poll); };
    document.getElementById('btnReset').onclick = function() { fetch((window.location.origin || 'http://127.0.0.1:5003') + '/api/reset').then(poll); };
    document.getElementById('speedSelect').onchange = function() {
      var v = this.value;
      fetch((window.location.origin || 'http://127.0.0.1:5003') + '/api/speed?x=' + v).then(poll);
    };

    setText('navOrigin', routeData.origin || '—');
    setText('navDestination', routeData.destination || '—');
    setText('navTotalKm', totalKm);
    setText('navWaypoints', waypoints.length);
    initMap();
    var initialState = buildInitialState();
    if (initialState) {
      updateUI(initialState);
      setTimeout(function() {
        ensureElevChart();
        if (elevChart && waypoints[currentIndex]) {
          var w0 = waypoints[currentIndex];
          elevChart.data.datasets[1].data = [{ x: w0.cumulative_km, y: w0.elevation_m }];
          elevChart.update('none');
        }
      }, 150);
    } else if (waypoints.length === 0) {
      setText('navOrigin', 'No route loaded');
      setText('navDestination', 'Run: python tests/ev_navigation_sunnyvale_tahoe_ui.py --web');
    }
    poll();
    setInterval(poll, 200);
  </script>
</body>
</html>
"""
    return (
        html.replace("__TOTAL_KM__", str(total_km))
        .replace("__MAX_RANGE_KM__", str(max_range_km))
        .replace("__LEN_WAYPOINTS__", str(len_waypoints))
        .replace("__ROUTE_DATA_JS__", route_data_js)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="EV Live Navigation: Sunnyvale → South Lake Tahoe")
    parser.add_argument("--web", action="store_true", help="Run browser UI")
    parser.add_argument("--port", type=int, default=5003, help="Port for web UI")
    args = parser.parse_args()

    if not args.web:
        print("Use --web to run. Example: python tests/ev_navigation_sunnyvale_tahoe_ui.py --web")
        return 0

    try:
        from flask import Flask, jsonify, request
    except ImportError:
        print("Flask is required: pip install flask")
        return 1

    route_data = _load_route()
    waypoints = route_data["waypoints"]
    n = len(waypoints)
    max_range_km = route_data.get("max_range_km", 360)
    state_lock = threading.Lock()
    state = {
        "current_index": 0,
        "playing": False,
        "speed_index": 8,
        "soc_pct": 100.0,
        "charging_at_end": False,
        "charge_progress": 0,
    }
    step_sec = 2.0  # 1 waypoint every 2s at 1× (2/speed s at higher speeds)
    charge_step_pct = 5  # charging at destination: +5% per tick

    def simulation_loop() -> None:
        while True:
            with state_lock:
                speed = max(1, state["speed_index"])
            time.sleep(step_sec / speed)
            with state_lock:
                if not state["playing"]:
                    continue
                idx = state["current_index"]
                if state["charging_at_end"]:
                    state["charge_progress"] = min(100, state["charge_progress"] + charge_step_pct)
                    state["soc_pct"] = state["charge_progress"]
                    if state["charge_progress"] >= 100:
                        state["charging_at_end"] = False
                        state["playing"] = False
                    continue
                if idx >= n - 1:
                    state["charging_at_end"] = True
                    state["charge_progress"] = state["soc_pct"]
                    continue
                next_idx = idx + 1
                state["current_index"] = next_idx
                w = waypoints[next_idx]
                prev = waypoints[next_idx - 1]
                delta_km = w["cumulative_km"] - prev["cumulative_km"]
                state["soc_pct"] = max(0, state["soc_pct"] - (delta_km / max_range_km) * 100)

    threading.Thread(target=simulation_loop, daemon=True).start()

    app = Flask(__name__)

    @app.route("/")
    def index() -> str:
        return _web_html(route_data)

    @app.route("/api/state")
    def api_state() -> str:
        with state_lock:
            idx = state["current_index"]
            w = waypoints[idx] if 0 <= idx < n else None
            cum_km = w["cumulative_km"] if w else 0
            trip_remaining_km = max(0, route_data["total_km"] - cum_km)
            range_km = (state["soc_pct"] / 100.0) * max_range_km
            avg_speed_kmh = 80.0
            eta_min = (trip_remaining_km / avg_speed_kmh * 60) if trip_remaining_km > 0 else 0
            charging = state.get("charging_at_end", False)
            charge_progress = state.get("charge_progress", 0)
        return jsonify({
            "current_index": idx,
            "playing": state["playing"],
            "speed_index": state["speed_index"],
            "soc_pct": state["soc_pct"],
            "charging": charging,
            "charge_progress": charge_progress,
            "range_km": range_km,
            "trip_remaining_km": trip_remaining_km,
            "eta_min": eta_min,
            "total_km": route_data["total_km"],
            "max_range_km": max_range_km,
            "len_waypoints": n,
        })

    @app.route("/api/play")
    def api_play() -> str:
        with state_lock:
            state["playing"] = True
        return jsonify({"ok": True})

    @app.route("/api/pause")
    def api_pause() -> str:
        with state_lock:
            state["playing"] = False
        return jsonify({"ok": True})

    @app.route("/api/reset")
    def api_reset() -> str:
        with state_lock:
            state["current_index"] = 0
            state["soc_pct"] = 100.0
            state["playing"] = False
            state["charging_at_end"] = False
            state["charge_progress"] = 0
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

    port = args.port
    url = f"http://127.0.0.1:{port}"

    def open_browser() -> None:
        time.sleep(1.0)
        import webbrowser
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()
    print(f"EV Sunnyvale → Tahoe UI: {url}")
    print("Close with Ctrl+C.")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
