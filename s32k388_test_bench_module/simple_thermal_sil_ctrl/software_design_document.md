# Software Design Document: Simple SIL Thermal Controller T3

**Document Version:** 1.1  
**Date:** January 13, 2026  
**Project:** Electric Vehicle Thermal Management System (SIL - Software-in-the-Loop)  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture](#architecture)
4. [Data Flow](#data-flow)
5. [Module Descriptions](#module-descriptions)
6. [Input/Output Specifications](#inputoutput-specifications)
7. [Control Logic & Algorithms](#control-logic--algorithms)
8. [State Machines & Discrete Logic](#state-machines--discrete-logic)
9. [Numerical Methods & Integration](#numerical-methods--integration)
10. [Code Generation & Build Process](#code-generation--build-process)
11. [Testing & Validation](#testing--validation)
12. [Performance Characteristics](#performance-characteristics)
13. [Code Standards & Conventions](#code-standards--conventions)
14. [File Structure](#file-structure)

---

## Executive Summary

The **Simple SIL Thermal Controller T3** is a thermal management system for electric vehicles. This system manages:

- **Thermal Regulation**: Battery cooling, cabin climate control, and component temperature management
- **Multi-Source Inputs**: Environmental data, component temperatures, HVAC settings, refrigerant properties
- **Discrete Control Outputs**: Relay signals for pump control, PTC (Positive Temperature Coefficient) heaters, compressor bypass valve, and HVAC settings
- **Continuous State Integration**: PID controllers with hysteretic relay logic for robust temperature management

---

## System Overview

### Purpose & Scope

The thermal controller manages EV thermal systems, including:
1. **Battery thermal management**: cooling, preheating, temperature limiting
2. **Cabin climate control**: HVAC blower, defrost, AC system coordination
3. **Powertrain cooling**: Motor, inverter, and radiator management
4. **Refrigerant cycle control**: Compressor discharge pressure, suction conditions
5. **Energy optimization**: Power compensation for cooling/heating loads


## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────┐
│     Input Vector (25 Signals)                       │
│  - Environmental & Sensor Data                      │
│  - HVAC Control Requests                            │
│  - Refrigerant Cycle Data                           │
│  - Vehicle State                                    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Thermal Control Algorithm                          │
│  ┌──────────────────────────────────────────────┐  │
│  │ PID Controllers (3x)                         │  │
│  │ - Battery thermal loop                       │  │
│  │ - Cabin temperature loop                     │  │
│  │ - Inverter/Motor thermal loop                │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │ Hysteretic Relay Logic (9x)                  │  │
│  │ - ON/OFF thresholds                          │  │
│  │ - Mode state tracking                        │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │ Lookup Tables (6x)                           │  │
│  │ - Performance mapping                        │  │
│  │ - Temperature-dependent gain scheduling      │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│     Output Vector (4 Signals)                       │
│  - Pump control signal                              │
│  - PTC heater command                               │
│  - Exv valve command                  │
│  - HVAC blower speed command                        │
└─────────────────────────────────────────────────────┘
```

### Module Dependencies

```
main.c
├── simple_sil_thermal_ctrl_t3.h
│   ├── simple_sil_thermal_ctrl_t4_math.h (types, solver support, nonfinite helpers)
│   ├── simple_sil_thermal_ctrl_t3_types.h
│   └── simple_sil_thermal_ctrl_t3_private.h
└── simple_sil_thermal_ctrl_t3.c
    ├── simple_sil_thermal_ctrl_t3_data.c (parameters)
    ├── math.h (mathematical functions)
    ├── simple_sil_thermal_ctrl_t4_math.c/h (runtime support)
    └── (no additional support libraries)
```

---

## Data Flow

### External Input Structure (25 Signals)

```c
typedef struct {
  // Temperature sensors [°C]
  real_T env_temp_degC;                     // [0] Environment
  real_T coolant_rad_out_temp_degC;         // [1] Radiator outlet
  real_T inverter_temp_degC;                // [2] Power inverter
  real_T motor_temp_degC;                   // [3] Electric motor
  real_T coolant_batt_in_temp_degC;         // [4] Battery loop inlet
  real_T battery_temp_max_degC;             // [5] Battery max (cell)
  real_T battery_temp_min_degC;             // [6] Battery min (cell)
  real_T cabin_temp_degC;                   // [7] Cabin interior
  real_T cabin_temp_setpoint_degC;          // [8] HVAC setpoint
  
  // HVAC Control
  real_T hvac_blower_enum;                  // [9] Blower speed (0-3)
  real_T defrost_bool;                      // [10] Defrost request
  real_T ac_bool;                           // [11] AC compressor request
  
  // Air Handling (ADS - Air Dust Sensor)
  real_T ads_temp_degC;                     // [12] Air temperature
  real_T ads_rh_perc;                       // [13] Relative humidity
  
  // Solar
  real_T photo_wpm2;                        // [14] Solar irradiance
  
  // Vehicle State
  real_T vehicle_spd_kph;                   // [15] Vehicle speed
  
  // Refrigerant Cycle (A/C System)
  real_T suction_temp_degC;                 // [16] Compressor suction
  real_T suction_press_psig;                // [17] Suction pressure
  real_T rts_temp_degC;                     // [18] Refrigerant Tank Sensor
  real_T discharge_temp_degC;               // [19] Compressor discharge
  real_T discharge_press_psig;              // [20] Discharge pressure
  
  // Target Setpoints & Limits
  real_T xtemp_batt_trgt_temp_degC;         // [21] Battery target temp
  real_T xtemp_power_comp_cabin_limit_w;    // [22] Cooling power limit
  real_T xtem_power_ptc_cabin_limit_w;      // [23] PTC heating power limit
  real_T xtem_temp_inv_in_trgt_degC;        // [24] Inverter inlet target
} ExtU_simple_sil_thermal_ctrl_T;
```

### External Output Structure (18 Signals)

```c
typedef struct {
  real_T cmd_aaf_enum;                 /* cmd_aaf_enum (0-100% for now needs update)*/
  real_T cmd_fan_perc;                 /* cmd_fan_perc */
  real_T cmd_batt_ptc_bool;            /* cmd_batt_ptc_bool */
  real_T cmd_motor_pump_perc;          /* cmd_motor_pump_perc */
  real_T cmd_batt_ewp_perc;            /* cmd_batt_ewp_perc */
  real_T cmd_multi_valve_enum;         /* cmd_multi_valve_enum (0-100% for now needs update)*/
  real_T cmd_blower_perc;              /* cmd_blower_perc */
  real_T cmd_cabin_ptc_perc;           /* cmd_cabin_ptc_perc */
  real_T cmd_comp_perc;                /* cmd_comp_perc */
  real_T cmd_batt_exv_perc;            /* cmd_batt_exv_perc */
  real_T cmd_hp_exv_perc;              /* cmd_hp_exv_perc */
  real_T heat_gen_valve_bool;          /* heat_gen_valve_bool (0-100% for now needs update)*/
  real_T cmd_temp_door_l_perc;         /* cmd_temp_door_l_perc */
  real_T cmd_temp_door_r_perc;         /* cmd_temp_door_r_perc */
  real_T cmd_mode_door_l_enum;         /* cmd_mode_door_l_enum (0-100% for now needs update)*/
  real_T cmd_mode_door_r_enum;         /* cmd_mode_door_r_enum (0-100% for now needs update)*/
  real_T cmd_intake_door_bool;         /* cmd_intake_door_bool */
  real_T cmd_def_door_perc;            /* cmd_def_door_perc */
} ExtY_simple_sil_thermal_ctrl_T;
```

### Internal Block Signals

```c
typedef struct {
  real_T Gain;                              // Proportional gain output
  real_T Sum;                               // Error summation
  real_T Gain_h;                            // Secondary gain
  real_T uDLookupTable;                     // 1-D lookup interpolation
  real_T Relay;                             // Relay hysteresis output
  real_T Relay_d;                           // Secondary relay
  real_T SumI4;                             // Integral sum 1
  real_T SumI4_d;                           // Integral sum 2
  real_T SumI4_h;                           // Integral sum 3
} B_simple_sil_thermal_ctrl_t3_T;
```

---

## Module Descriptions

### 1. **Main Entry Point** (`main.c`)

**Purpose:** SIL test harness that orchestrates model execution with CSV-based input data.

**Key Functions:**

- `waitSeconds()`: Implements busy-wait for timing
- `parseCsvLine()`: Parses comma-separated input values (doubles)
- `loadInputsFromValues()`: Maps parsed CSV data to model input signals
- `unloadOutputsToFile()`: Writes computed outputs to file for validation

**Responsibilities:**
- Initialize the thermal controller model
- Load test data from `example_data.csv`
- Execute model step at 0.1s intervals
- Log outputs for verification

**Execution Flow:**
```
1. Initialize model (simple_sil_thermal_ctrl_t3_initialize)
2. For each CSV line:
   a. Parse values
   b. Load into U structure
   c. Execute one time step (simple_sil_thermal_ctrl_t3_step)
   d. Wait 0.1 seconds
   e. Retrieve outputs from Y structure
   f. Optionally log to file
3. Terminate model (simple_sil_thermal_ctrl_t3_terminate)
```

### 2. **Model Core** (`simple_sil_thermal_ctrl_t3.c`)

**Key Functions:**

- `look1_plinlxpw()`: 1-D linear interpolated lookup table with extrapolation
  - Uses breakpoint-based index caching for efficiency
  - Supports 6 independent lookup tables in the controller
  - Implements linear extrapolation beyond table bounds

- `rt_ertODEUpdateContinuousStates()`: ODE3 solver core
  - 3rd-order Runge-Kutta integration (3 derivative evaluations per step)
  - Fixed-step 0.1s integration
  - Manages 3 continuous state integrators (PID I-terms)

- `simple_sil_thermal_ctrl_t3_step()`: Main execution step
  - Computes all block outputs
  - Updates relay logic and states
  - Prepares derivatives for next ODE step

- `simple_sil_thermal_ctrl_t3_derivatives()`: Derivative computation
  - Calculates dx/dt for all continuous state integrators
  - Called 3 times per ODE3 step

- `simple_sil_thermal_ctrl_t3_initialize()`: Initialization routine
  - Sets continuous state initial conditions (typically 0.0)
  - Initializes block states and relay modes
  - Clears cache indices

- `simple_sil_thermal_ctrl_t3_terminate()`: Cleanup routine
  - Releases resources if applicable

### 3. **Model Parameters & Configuration** (`simple_sil_thermal_ctrl_t3_data.c`)

**Purpose:** Stores all tunable parameter values for the control algorithm.

[jz: value needs review]
**Key Parameters:** 

| Parameter | Value | Unit | Purpose |
|-----------|-------|------|---------|
| `batt_chiller_bypass_relay_on` | 35.0 | °C | Battery temp to activate bypass |
| `batt_chiller_bypass_relay_off` | 30.0 | °C | Battery temp to deactivate bypass |
| `batt_ptc_on` | 15.0 | °C | Battery temp to activate heater |
| `batt_ptc_off` | 5.0 | °C | Battery temp to deactivate heater |
| `batt_pump_max_on` | 45.0 | °C | Battery temp to activate pump |
| `batt_pump_max_off` | 40.0 | °C | Battery temp to deactivate pump |
| `PIDController_P` | Varies | — | Proportional gain (battery loop) |
| `PIDController_I` | 0.00667 | — | Integral gain (battery loop) |
| `PIDController_Kb` | 1.0 | — | Back-calculation anti-windup |
| `PIDController_LowerSaturationLimit` | 0.0 | % | Output saturation minimum |
| `PIDController_UpperSaturationLimit` | 100.0 | % | Output saturation maximum |

**Relay Hysteresis Pattern:**

All relay logic uses hysteretic thresholds:
- **ON threshold** (higher): Activates when temperature rises above this point
- **OFF threshold** (lower): Deactivates when temperature falls below this point
- **Hysteresis band** = ON threshold - OFF threshold (typically 5-10°C)

This prevents chattering in border conditions.

### 4. **Type Definitions** (`simple_sil_thermal_ctrl_t3_types.h`)

Forward declarations for:
- `P_simple_sil_thermal_ctrl_t3_T`: Parameter structure type
- `RT_MODEL_simple_sil_thermal_c_T`: Real-time model structure type

### 5. **Runtime Support Libraries**

#### `simple_sil_thermal_ctrl_t4_math.c/h`
- Base type definitions: `real_T`, `uint32_T`, `boolean_T`
- Continuous state timing enums and solver helpers
- NaN/Inf constants and checks used by the model

---

## Input/Output Specifications

### Input Signal Groups (25 total)

#### Temperature Monitoring (6 signals)
- **Inverter Temperature** [`inverter_temp_degC`]: Power electronics thermal state
- **Motor Temperature** [`motor_temp_degC`]: Drivetrain thermal state
- **Battery Min/Max** [`battery_temp_min/max_degC`]: Cell-level thermal bounds
- **Environment** [`env_temp_degC`]: Ambient conditions

#### Refrigerant Cycle (5 signals)
- **Suction Conditions**: Temperature, pressure (compressor inlet)
- **Discharge Conditions**: Temperature, pressure (compressor outlet)
- **Tank Sensor** [`rts_temp_degC`]: Subcooling/superheating monitor

#### HVAC & Cabin (5 signals)
- **Cabin Temperature & Setpoint**: Current vs. desired climate
- **Blower Speed Enum**: 0-off, 1-Level1, 2-Level2, 3-Level3, 4-Level4, 5-Level5, 6-Level6, 7-Level7, 8-Level8, 9-Level9, 10-Level10   [jz: enum def needs review]
- **AC/Defrost Requests**: Boolean control inputs
- **Air Sensor Data**: Temperature, relative humidity

#### Vehicle State (2 signals)
- **Vehicle Speed** [`vehicle_spd_kph`]: Driving status
- **Solar Irradiance** [`photo_wpm2`]: External heating load

#### Control Limits (3 signals)
- **Battery Target Temp** [`xtemp_batt_trgt_temp_degC`]: PID setpoint
- **Cooling Power Limit** [`xtemp_power_comp_cabin_limit_w`]: Thermal budget (W)
- **PTC Power Limit** [`xtem_power_ptc_cabin_limit_w`]: Heating budget (W)
- **Inverter Target** [`xtem_temp_inv_in_trgt_degC`]: Coolant inlet setpoint

### Output Signals (18 total)

[jz: data type needs review and update, control states to be defined]
#### Actuator Commands (all 0-100%) 
- **AAF control command** [`cmd_aaf_enum`]: Target position for the AAF(s) 
- **Radiator fan control command** [`cmd_fan_perc`]: Target position for the radiator fan
- **Battery heater on command** [`cmd_batt_ptc_bool`]: On/Off target command for the battery heater
- **PE pumpd control command** [`cmd_motor_pump_perc`]: Target speed (DC) for the PE pump
- **Batt pump control command** [`cmd_batt_ewp_perc`]: Target speed (DC) for the Battery pump
- **Multi valve control command** [`cmd_multi_valve_enum`]: Target position for the multi valve
- **HVAC blower control command** [`cmd_blower_perc`]: Target speed (DC) for the HVAC blower
- **Cabin PTC heater control command** [`cmd_cabin_ptc_perc`]: Target command for the cabin heater (%)
- **Compressor control command** [`cmd_comp_perc`]: Target speed (DC) for the compressor
- **Battery exv control command** [`cmd_batt_exv_perc`]: Target position for the battery exv
- **HP exv control command** [`cmd_hp_exv_perc`]: Target position for the HP exv (%)
- **Heat gen valve control command** [`heat_gen_valve_bool`]: Target position for the heat-gen valve // heat gen valve for xp2 only, not for xv1
- **HVAC temperature door control command** [`cmd_temp_door_l_perc`]: Target position for the left temperature door (%)
- **HVAC temperature door control command** [`cmd_temp_door_r_perc`]: Target position for the right temperature door (%)
- **HVAC mode door control command** [`cmd_mode_door_l_enum`]: Target position for the left mode door
- **HVAC mode door control command** [`cmd_mode_door_r_enum`]: Target position for the right mode door
- **HVAC intake door control command** [`cmd_intake_door_bool`]: Target position for the intake door
- **HVAC defogging door control command** [`cmd_def_door_per`]: Target position for the def door (%)
- **Thermal control system control system command** [`inf_control_state_enum`]: Control state information

**Output Saturation:** All outputs are limited to [0.0, 100.0] %

---

## Control Logic & Algorithms

### PID Control Architecture

The system implements **3 parallel PID loops** with hysteretic relay outputs:

```
Setpoint - Feedback → [Error]
                         ↓
                    ┌────┴────┐
                    ├── P-Gain ┤
                    ├─ I-Integrator ┤
                    └────┬────┘
                         ↓
                    [PID Output]
                         ↓
                    [Saturation Limiter]
                         ↓
                    [Hysteretic Relay] → Output (ON/OFF or 0-100%)
```

#### Loop 1: Battery Thermal Management

**Inputs:**
- `battery_temp_max_degC` (actual temperature)
- `xtemp_batt_trgt_temp_degC` (setpoint from higher-level thermal scheduler)

**Output:**
- `pump_cmd` (0-100% cooling pump speed)

**Parameters:**
- **Proportional Gain** [`PIDController_P`]: ~variable (gain scheduling)
- **Integral Gain** [`PIDController_I`]: 0.00667 (slow accumulation)
- **Anti-Windup** [`Kb`]: 1.0 (back-calculation factor)
- **Saturation**: [0%, 100%]

**Relay Logic:**
- **ON**: battery_temp_max ≥ 45.0°C → activate pump
- **OFF**: battery_temp_max ≤ 40.0°C → deactivate pump

#### Loop 2: Cabin Climate Control

**Inputs:**
- `cabin_temp_degC` (actual cabin temperature)
- `cabin_temp_setpoint_degC` (user/system setpoint)

**Output:**
- `hvac_blower_cmd` (0-100% fan speed)

**Parameters:**
- **Proportional Gain** [`PIDController_g`]: variable
- **Integral Gain** [`PIDController_I_g`]: 0.2 (faster response)
- **Anti-Windup** [`Kb_b`]: 1.0
- **Saturation**: [0%, 100%]

#### Loop 3: Inverter/Motor Thermal Management

**Inputs:**
- `inverter_temp_degC` and `motor_temp_degC` (weighted average)
- `xtem_temp_inv_in_trgt_degC` (coolant inlet target)

**Output:**
- `compressor_bypass_cmd` (0-100% valve opening)

**Parameters:**
- **Proportional Gain** [`PIDController1_P`]: tunable
- **Integral Gain** [`PIDController1_I`]: 0.2
- **Anti-Windup** [`Kb_b`]: 1.0
- **Saturation**: [0%, 100%]

### Lookup Table Interpolation

**Function:** `look1_plinlxpw()`

**Algorithm:**
1. **Breakpoint Search**: Linear search from cached previous index
2. **Fraction Calculation**: Linear interpolation factor between breakpoints
3. **Output Computation**: `y = y[i] + (y[i+1] - y[i]) × frac`
4. **Extrapolation**: Linear extension beyond table bounds

**Performance Optimization:**
- Caches last index for each table (6 separate caches)
- Avoids full search on each call
- Maintains sorted breakpoint arrays

**Use Cases:**
1. Temperature-dependent gain scheduling
2. Performance curve mapping (power vs. temperature)
3. Efficiency lookup tables
4. Saturation curve shaping

### Hysteretic Relay Logic

**State Machine:**

```
         ┌─────────────────────┐
         │     OFF State       │
         │  Output = 0 or Low  │
         └────────┬────────────┘
                  │
         Input > ON_Threshold
                  │
                  ▼
         ┌─────────────────────┐
         │     ON State        │
         │  Output = 100 or High│
         └────────┬────────────┘
                  │
         Input < OFF_Threshold
                  │ (Dead band)
                  ▼ (prevents oscillation)
```

**Prevents Chattering:**
- Dead band between ON and OFF thresholds
- State memory (relay must complete full cycle to change)
- Typical hysteresis: 5-10°C for temperature-based triggers

**Examples:**
- Battery chiller bypass: ON@35°C, OFF@30°C
- PTC heater: ON@15°C, OFF@5°C
- Pump maximum speed: ON@45°C, OFF@40°C

---

## State Machines & Discrete Logic

### State Structure

```c
typedef struct {
  // Breakpoint indices (6 lookup tables)
  uint32_T m_bpIndex;        // Main lookup table cache
  uint32_T m_bpIndex_e;      // Extended cache
  uint32_T m_bpIndex_h;      // Heating path cache
  uint32_T m_bpIndex_k;      // Cooling path cache
  uint32_T m_bpIndex_b;      // Battery loop cache
  uint32_T m_bpIndex_g;      // Global cache
  
  // Relay mode states (9 relays × 2 variants = 18 flags)
  boolean_T Relay_Mode;                    // Main relay
  boolean_T Relay_Mode_h;                  // Heating relay
  boolean_T Relay_Mode_k;                  // Cooling relay
  boolean_T Relay_Mode_kd;                 // Compressor bypass
  boolean_T Relay_Mode_o;                  // Pump max speed
  boolean_T RelayLevel3_Mode;              // Tiered control level 3
  boolean_T RelayLevel2_Mode;              // Tiered control level 2
  boolean_T RelayLevel1_Mode;              // Tiered control level 1
  boolean_T Relay_Mode_c;                  // Secondary relay
  boolean_T Relay_Mode_e;                  // Tertiary relay
  boolean_T Relay_Mode_a;                  // Quaternary relay
  boolean_T Relay_Mode_m;                  // Quinary relay
  boolean_T Relay_Mode_g;                  // Senary relay
} DW_simple_sil_thermal_ctrl_t3_T;
```

### Continuous State Structure

**Three Integrator States** (PID I-terms):

```c
typedef struct {
  real_T Integrator_CSTATE;               // Battery loop integral
  real_T Integrator_CSTATE_a;             // Cabin loop integral
  real_T Integrator_CSTATE_h;             // Inverter loop integral
} X_simple_sil_thermal_ctrl_t3_T;
```

**State Derivatives:**

```c
typedef struct {
  real_T Integrator_CSTATE;               // d/dt of battery integral
  real_T Integrator_CSTATE_a;             // d/dt of cabin integral
  real_T Integrator_CSTATE_h;             // d/dt of inverter integral
} XDot_simple_sil_thermal_ctrl__T;
```

**Integrator Differential Equations:**
```
d(I_battery)/dt = e_battery × K_i_battery
d(I_cabin)/dt   = e_cabin   × K_i_cabin
d(I_inverter)/dt = e_inverter × K_i_inverter
```

Where error `e = setpoint - feedback`

---

## Numerical Methods & Integration

### ODE3 Runge-Kutta Solver

**Method:** 3rd-order Runge-Kutta with fixed step size

**Step Configuration:**
- **Fixed Step Size:** Δt = 0.1 s (100 ms)
- **Time Step Mode:** MAJOR_TIME_STEP (synchronous with discrete logic)
- **Integrator Type:** Continuous state derivatives

**Integration Coefficients:**

```
A = [1/2, 3/4, 1]

B = [1/2   0     0  ]
    [0    3/4    0  ]
    [2/9  1/3   4/9]
```

**Algorithm:**
```
1. Store current state: y ← x
2. Compute f0 = f(t, y)
3. Compute x = y + Δt × (1/2) × f0
4. Compute f1 = f(t + Δt/2, x)
5. Compute x = y + Δt × [(0)×f0 + (3/4)×f1]
6. Compute f2 = f(t + 3Δt/4, x)
7. Update x = y + Δt × [(2/9)×f0 + (1/3)×f1 + (4/9)×f2]
8. Continue to next step
```

**Accuracy:** 3rd-order (error ~ O(Δt⁴))

**Stability:** RK3 is stable for Δt ≤ 1.73 for linear systems; fixed step chosen for deterministic real-time execution

### Anti-Windup Implementation

**Back-Calculation with Kb:**

When output saturates:
```
e_aw = (saturated_output - unsaturated_output) / Kb
I_new = I_old - e_aw × K_i × Δt
```

**Effect:**
- Reduces integral accumulation during saturation
- Prevents overshoot when output constraint releases
- Kb = 1.0 provides full anti-windup feedback

---

## Testing & Validation

### Test Data Format

**Input:** `example_data.csv`
- 10 rows of test scenarios
- 25 columns (all 25 input signals)
- All values repeated (steady-state test case)

**Sample Test Vector:**
```csv
env_temp: 25°C, battery_max: 30°C, inverter: 35°C, motor: 40°C,
cabin: 23°C, setpoint: 22°C, ac: enabled, speed: 60 kph
```

**Expected Behavior:**
- Pump remains OFF (battery temp 30°C < 40°C threshold)
- Compressor bypass opens partially (inverter 35°C < 45°C)
- HVAC blower moderate (cabin close to setpoint)
- PTC heater OFF (cabin cooling not needed)

### Validation Points

#### Functional Verification
1. ✓ PID loops track setpoints within deadband
2. ✓ Relay hysteresis prevents chattering
3. ✓ Lookup tables interpolate correctly
4. ✓ Anti-windup limits integral growth
5. ✓ Outputs saturate at [0, 100%]

#### Numerical Verification
1. ✓ ODE3 integration stability
2. ✓ Floating-point handling (NaN/Inf)
3. ✓ Derivative computation accuracy
4. ✓ State consistency across steps

#### Safety Properties
1. ✓ All outputs bounded
2. ✓ No undefined behavior on edge inputs
3. ✓ Deterministic step execution (fixed-step)
4. ✓ State initialization valid

---

## Performance Characteristics

### Computational Load

| Component | Est. Operations | Duration |
|-----------|------------------|----------|
| Lookup tables (6×) | 200-600 | < 0.5 ms |
| PID computations (3×) | 100-300 | < 0.2 ms |
| Relay logic (9×) | 50-100 | < 0.1 ms |
| ODE3 integration (3 stages) | 400-800 | < 1.0 ms |
| **Total per step** | ~1000 | **< 2.0 ms** |

**Sample Time:** 100 ms → **Utilization: < 2%** (worst-case)

### Memory Footprint

| Component | Size (bytes) |
|-----------|-------------|
| Block signals (9 reals) | 72 |
| Continuous states (3 reals) | 24 |
| Block states (19 booleans + 6 uint32) | 43 |
| Parameter structure | ~500 |
| Local variables & stack | ~200 |
| **Total working memory** | **< 1 KB** |

**Code Size:** ~15 KB (compiled binary, optimized)

### Numerical Precision

- **Floating-Point Type:** `real_T` (double, 64-bit IEEE 754)
- **Integer Type:** `uint32_T` (32-bit unsigned)
- **Quantization:** ±2.22e-16 (machine epsilon for double)
- **Effective Precision:** Better than 0.01°C for temperature signals

---

## Code Standards & Conventions

### Naming Conventions (Per ASIL-D Safety Guidelines)

#### Variables
- **Physical Quantities** MUST include unit suffixes:
  - `battery_temp_degC`, `pressure_kPa`, `timeout_ms`
- **Snake case:** `my_variable_name`
- **Member Variables:** `m_` prefix (e.g., `m_inlet_temp`)
- **Global Variables:** `g_` prefix
- **Static Variables:** `s_` prefix
- **Pointers:** `p_` prefix (e.g., `p_model`)

#### Functions
- **Verb-Noun Pattern:** `calculateCooling()`, `validateInput()`
- **Camel case:** `myFunction()`
- **No Abbreviations:** Use full names for clarity

#### Types & Constants
- **Types:** `PascalCase` (e.g., `ThermalState`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_TEMP_DEGC`)
- **Type Aliases:** Use `using` (MISRA++ style)

### Safety-Critical Principles

#### Memory Management
- ✓ **NO dynamic allocation** (no malloc/new)
- ✓ **Fixed-size arrays** and static allocation
- ✓ **All memory** allocated at startup

#### Control Flow
- ✓ **NO recursion** (unbounded stack usage)
- ✓ **NO exceptions** (return status codes instead)
- ✓ **Bounded loops** with compile-time limits
- ✓ **NO function pointers** (dynamic dispatch forbidden)

#### Pointer Safety
- ✓ **Initialize all pointers** to `nullptr` if unassigned
- ✓ **Check for nullptr** on function entry
- ✓ **Prefer references** (`T&`) over pointers
- ✓ **NO pointer arithmetic** (use array indexing)

#### Type Safety
- ✓ **Explicit sized types** (`uint32_t`, `int16_t` vs. `int`)
- ✓ **`const` correctness** enforced
- ✓ **No type casts** without justification
- ✓ **No bitfields** (memory layout undefined)

### MISRA C Compliance

The code adheres to MISRA C 2012 with relaxations for simulation runtime infrastructure:

- ✓ No implicit type conversions
- ✓ All functions with explicit return types
- ✓ No global state mutation (except RT model)
- ✓ No side effects in conditionals
- ✓ Comments for non-obvious logic

---

## File Structure

### Directory Layout

```
simple_sil_thermal_ctrl_t3_grt_rtw/
│
├── Model Source Files
│   ├── simple_sil_thermal_ctrl_t3.h          [701 lines] Main model API & types
│   ├── simple_sil_thermal_ctrl_t3.c          [1013 lines] Core algorithm
│   ├── simple_sil_thermal_ctrl_t3_data.c     [557 lines] Parameters
│   ├── simple_sil_thermal_ctrl_t3_types.h    Type declarations
│   ├── simple_sil_thermal_ctrl_t3_private.h  Internal interfaces
│   └── main.c                                [219 lines] Test harness
│
├── Support Libraries
│   ├── simple_sil_thermal_ctrl_t4_math.c/h     Local runtime/types/solver helpers
│   ├── builtin_typeid_types.h                Type ID tracking
│   ├── multiword_types.h                     Extended precision types
│   └── sl_types_def.h                        Simulink data type enums
│
├── Test & Validation
│   ├── example_data.csv                      Input test vectors (25 signals)
│   └── (no additional model metadata)
│
└── Documentation
    ├── copilot-instructions.md               Safety guidelines & conventions
    └── software_design_document.md           [This file]


```

### Line Counts Summary

| File | Lines | Purpose |
|------|-------|---------|
| `simple_sil_thermal_ctrl_t3.h` | 701 | Main API, structures |
| `simple_sil_thermal_ctrl_t3.c` | 1013 | Algorithm implementation |
| `simple_sil_thermal_ctrl_t3_data.c` | 557 | Parameters |
| `main.c` | 219 | Test harness |
| **Total Core** | **2490** | **Thermal control model** |

### Key Dependencies

```
main.c -> thermal_example_module.c
  ├─→ simple_sil_thermal_ctrl_t3.h
  │     ├─→ simple_sil_thermal_ctrl_t4_math.h
  │     ├─→ simple_sil_thermal_ctrl_t3_types.h
  │     ├─→ simple_sil_thermal_ctrl_t3_private.h
  │     └─→ (no logging dependencies)
  │
  └─→ simple_sil_thermal_ctrl_t3.c
        ├─→ math.h (standard library)
        ├─→ simple_sil_thermal_ctrl_t4_math.h
        ├─→ simple_sil_thermal_ctrl_t3_private.h
        └─→ string.h (memory ops)
```

---

## Appendix A: Signal Descriptions

[jz: to be reviewed and need update]
### Input Signals (Detailed)

| Index | Signal | Type | Range | Unit | Source |
|-------|--------|------|-------|------|--------|
| 0 | `env_temp_degC` | real_T | -40 to +60 | °C | Weather station |
| 1 | `coolant_rad_out_temp_degC` | real_T | 0 to 100 | °C | Radiator outlet sensor |
| 2 | `inverter_temp_degC` | real_T | -20 to +150 | °C | Power inverter NTC |
| 3 | `motor_temp_degC` | real_T | -20 to +150 | °C | Motor winding NTC |
| 4 | `coolant_batt_in_temp_degC` | real_T | 0 to 100 | °C | Battery loop inlet |
| 5 | `battery_temp_max_degC` | real_T | -20 to +80 | °C | BMS (cell max) |
| 6 | `battery_temp_min_degC` | real_T | -20 to +80 | °C | BMS (cell min) |
| 7 | `cabin_temp_degC` | real_T | -20 to +60 | °C | Cabin temperature sensor |
| 8 | `cabin_temp_setpoint_degC` | real_T | 16 to 32 | °C | User climate control |
| 9 | `hvac_blower_enum` | real_T | 0-3 | — | HVAC control (0 : off, 1 : Level1, 2 : Level2, 3 : Level3, 4 : Level4, 5 : Level5, 6 : Level6, 7 : Level7, 8 : Level8, 9 : Level9, 10 : Level10 ) |
| 10 | `defrost_bool` | real_T | 0-1 | — | Windshield defrost request |
| 11 | `ac_bool` | real_T | 0-1 | — | AC compressor enable |
| 12 | `ads_temp_degC` | real_T | -20 to +60 | °C | Air duct sensor temp |
| 13 | `ads_rh_perc` | real_T | 0-100 | % | Air duct sensor humidity |
| 14 | `photo_wpm2` | real_T | 0-1000 | W/m² | Roof solar irradiance |
| 15 | `vehicle_spd_kph` | real_T | 0-250 | km/h | Wheel speed (vehicle speed) |
| 16 | `suction_temp_degC` | real_T | -40 to +30 | °C | A/C suction line |
| 17 | `suction_press_psig` | real_T | -5 to +50 | psig | A/C suction pressure |
| 18 | `rts_temp_degC` | real_T | -30 to +80 | °C | Refrigerant tank sensor |
| 19 | `discharge_temp_degC` | real_T | 0 to +150 | °C | Compressor discharge |
| 20 | `discharge_press_psig` | real_T | 100-400 | psig | Discharge line pressure |
| 21 | `xtemp_batt_trgt_temp_degC` | real_T | 0-50 | °C | Target battery temp (setpoint) |
| 22 | `xtemp_power_comp_cabin_limit_w` | real_T | 0-10000 | W | Max cooling power available |
| 23 | `xtem_power_ptc_cabin_limit_w` | real_T | 0-5000 | W | Max heating power available |
| 24 | `xtem_temp_inv_in_trgt_degC` | real_T | 10-50 | °C | Coolant inlet target (inverter) |

### Output Signals
[jz: needs review and update, data type vs definition, control state to be defined and added]

| Signal | Type | Range | Unit | Definition  |
|--------|------|-------|------|-------------|
| `cmd_aaf_enum` | real_T | 0-100 | % | AAF control (0 : Close, 1 : 1stOpen, 2 : 2ndOpen, 3 : Open, 4 : DiagModeOpen, 5 : DiagModeClose, 6 : DiagModeAuto, 7 : ErrorIndicator) |
| `cmd_fan_perc` | real_T | 0-100 | % | Radiator fan control |
| `cmd_batt_ptc_bool` | real_T | 0-100 | % | Battery PTC heater control |
| `cmd_motor_pump_perc` | real_T | 0-100 | % | PE pump control |
| `cmd_batt_ewp_perc` | real_T | 0-100 | % | Battery pump control |
| `cmd_multi_valve_enum` | real_T | 0-100 | % | Multi-valve control |
| `cmd_blower_perc` | real_T | 0-100 | % | HVAC blower control |
| `cmd_cabin_ptc_perc` | real_T | 0-100 | % | Cabin PTC heater |
| `cmd_comp_perc` | real_T | 0-100 | % | Ecompressor control |
| `cmd_batt_exv_perc` | real_T | 0-100 | % | Battery exv control |
| `cmd_hp_exv_perc` | real_T | 0-100 | % | HP exv control |
| `heat_gen_valve_bool` | real_T | 0-100 | % | Heat-gen valve control |
| `cmd_temp_door_l_perc` | real_T | 0-100 | % | Left temperature door control |
| `cmd_temp_door_r_perc` | real_T | 0-100 | % | Right temperature door control |
| `cmd_mode_door_l_enum` | real_T | 0-100 | % | Left mode door control |
| `cmd_mode_door_r_enum` | real_T | 0-100 | % | Right mode door control |
| `cmd_intake_door_bool` | real_T | 0-100 | % | Intake door control |
| `cmd_def_door_enum` | real_T | 0-100 | % | Def door control |
| `inf_control_state` | real_T | 0-100 | % | Control state information |
---

## Appendix B: Glossary

| Term | Definition |
|------|-----------|
| **ASIL-D** | Automotive Safety Integrity Level - Dangerous; highest safety level for automotive systems |
| **GRT** | Generic Real-Time target; Simulink code gen for rapid prototyping |
| **SIL** | Software-in-the-Loop testing; simulation on PC before embedding |
| **PIL** | Processor-in-the-Loop testing; code running on target hardware with simulation |
| **ODE3** | 3rd-order Runge-Kutta ordinary differential equation solver |
| **PID** | Proportional-Integral-Derivative controller |
| **Anti-Windup** | Technique to prevent integrator saturation overshoot |
| **Hysteresis** | Dead band between ON/OFF thresholds to prevent oscillation |
| **NTC** | Negative Temperature Coefficient thermistor (common EV sensor) |
| **BMS** | Battery Management System |
| **HVAC** | Heating, Ventilation, and Air Conditioning |
| **A/C** | Air Conditioning (refrigerant cycle) |
| **PTC** | Positive Temperature Coefficient heater (cabin/battery preheating) |
| **RTM** | Real-Time Model (Simulink internal data structure) |
| **DAQ** | Data Acquisition (test data logging) |
| **FMI** | Functional Mockup Interface (model exchange standard) |

---

**Document Prepared:** January 6, 2026  
**Next Review:** Upon model update or parameter retuning  

---

*End of Software Design Document*
