# Thermal HIL Viewer (Android)

Android app that displays **Thermal HIL 1** response data from CSV (same format as `thermal_example_module_out.csv`).

## Gradle 9.0.0 compatibility

This project is configured for **Gradle 9.0.0**:

- **Gradle**: 9.0.0 (see `gradle/wrapper/gradle-wrapper.properties`).
- **Android Gradle Plugin (AGP)**: 8.7.2 (Gradle 9.0.0 requires AGP ≥ 8.4.0).
- **Kotlin**: 2.0.21 (Gradle 9.0.0 requires Kotlin Gradle Plugin ≥ 2.0.0).
- **Compose**: uses `org.jetbrains.kotlin.plugin.compose` (Compose compiler built into Kotlin 2.x).

**JDK**: Gradle 9.0.0 requires **JVM 17 or higher** to run the Gradle daemon.

## Features

- **Live metrics** – Latest sample: Battery SOC %, vehicle speed (kph), battery temp (°C), coolant outlet temp (°C).
- **Time series** – Scrollable list of all rows with time, SOC, speed, and temperatures per sample.
- Loads CSV from **assets**: `app/src/main/assets/thermal_hil_response.csv`.

## Data format

CSV must have header and columns (same as `tests/csv_data/thermal_data_base.csv`):

`dt_s`, `driver_speed_mps`, `vehicle_speed_mps`, `battery_soc`, `battery_soh`, `battery_temp_K`, `battery_current_A`, `battery_voltage_V`, `battery_heat_gen_W`, `battery_heat_rej_W`, `emotor_torque_Nm`, `emotor_speed_radps`, `env_temp_degC`, `vehicle_spd_kph`, `coolant_rad_out_temp_degC`, `coolant_batt_in_temp_degC`, `inverter_temp_degC`

## Build and run

1. Open **Android Studio** and open the `android_app` folder (or the repo root and select `android_app` as the project).
2. Sync Gradle, then Run on a device or emulator (API 26+).

Or from the command line (no need to install Gradle globally; the project includes the wrapper):

```bash
cd android_app
./gradlew assembleDebug
# Install: adb install -r app/build/outputs/apk/debug/app-debug.apk
```

**Note:** You do **not** need to install `gradle` on your machine. Use `./gradlew` (Gradle Wrapper) from the `android_app` directory; it uses the bundled `gradle-wrapper.jar` and will download Gradle 9.0.0 on first run if needed. Requires **JDK 17+**.

If `gradle-wrapper.jar` is missing (e.g. not committed), generate it once:

```bash
# Install Gradle (one-time), then generate wrapper
brew install gradle   # macOS
# or: sdk install gradle 9.0.0
gradle wrapper --gradle-version 9.0.0
```

## Replacing data

- Replace `app/src/main/assets/thermal_hil_response.csv` with your HIL output (e.g. copy from `thermal_example_module_out.csv` after running the test), then rebuild and run.
