# EV Navigation, Energy Utilization & Range Estimation (2026.1)

## Overview

This package implements a **live UI** to test and demonstrate the ecosystem for EV navigation, energy utilization, and range estimation using the required 2026.1 APIs.

## 1. Core Framework APIs

- **Car.createCar(context)** – Top-level entry; initialize before any car services.
- **CarPropertyManager** – Get/set and subscribe to vehicle sensors (EV data).
- **CarInfoManager** – Static metadata (e.g. battery capacity); often via CarPropertyManager in 2026.
- **CarAppService** – Required for template-based Car App Library apps (driver safety).

## 2. VHAL Property IDs (CarPropertyManager)

Use `CarPropertyManager.registerCallback()` / `getProperty()` with:

| Feature           | Property ID                         | Type    |
|------------------|--------------------------------------|--------|
| Current charge   | EV_BATTERY_LEVEL                     | Float   |
| Max capacity     | INFO_EV_BATTERY_CAPACITY            | Float   |
| Energy flow      | EV_BATTERY_INSTANTANEOUS_CHARGE_RATE | Float (mW) |
| Charging state   | EV_CHARGE_STATE                      | Enum    |
| Plug status      | EV_CHARGE_PORT_CONNECTED             | Boolean |
| Battery temp     | EV_BATTERY_AVERAGE_TEMPERATURE       | Float (°C) |
| Regen braking    | EV_REGENERATIVE_BRAKING_STATE        | Enum    |
| Speed            | PERF_VEHICLE_SPEED                   | Float (m/s) |
| Climate load     | HVAC_POWER_ON                        | Boolean |

See `EvVehiclePropertyIds.kt` and `EvDataModel.kt`.

## 3. Manifest Permissions

Declared in `AndroidManifest.xml`:

- `android.car.permission.CAR_ENERGY`
- `android.car.permission.CAR_ENERGY_PORTS`
- `android.car.permission.CAR_SPEED`
- `android.car.permission.READ_CAR_STEERING`
- `android.car.permission.CAR_EXTERIOR_ENVIRONMENT`
- `android.permission.ACCESS_FINE_LOCATION`
- `android.car.permission.CAR_NAVIGATION_MANAGER`

## 4. Implementation Logic

1. **Initialize:** `Car.createCar(context)` → `getCarManager(Car.PROPERTY_SERVICE)` → `CarPropertyManager`.
2. **Request energy profile:** `getProperty(INFO_EV_BATTERY_CAPACITY)`.
3. **Subscribe to SoC:** `registerCallback(..., EV_BATTERY_LEVEL, ...)`.
4. **Range-aware routing:** Send `current_soc` to routing engine; get route with `charging_stations` as waypoints (e.g. ComputeRoutes, travelMode: DRIVE, routingPreference: FUEL_EFFICIENT).
5. **Thermal / preconditioning:** If next waypoint is a charger and distance < 20 km, call vendor property to start battery preconditioning.

## 5. Navigation & Routing APIs

- **Google Maps Routes API (v2):** ComputeRoutes with waypoints (chargers), travelMode DRIVE, routingPreference FUEL_EFFICIENT.
- **androidx.car.app.navigation:** NavigationManager (turn-by-turn to cluster), PlaceListMapTemplate (charging stations).
- **EVCoDriver API:** Time-to-charge at waypoints from charging curve.

## 6. Current Implementation

- **EvNavigationActivity** – Entry point; uses **MockEvDataProvider** for testing without DUT.
- **EvLiveUiScreen** – Compose UI showing all EV parameters, range estimate, and placeholders for range-aware routing and preconditioning.
- **CarEvDataProvider** – Stub for VHAL-backed data when running on Android Automotive with Car API.

To use real VHAL, implement `CarEvDataProvider` with `Car.createCar(context)` and `CarPropertyManager` callbacks using `EvVehiclePropertyIds`.
