/*
 * simple_sil_thermal_ctrl_t3_data.c
 */

#include "simple_sil_thermal_ctrl_t3.h"

/* Block parameters (default storage) */
P_simple_sil_thermal_ctrl_t3_T simple_sil_thermal_ctrl_t3_P = {
  /* Variable: batt_chiller_bypass_relay_off
   * Referenced by: Relay
   */
  30.0,

  /* Variable: batt_chiller_bypass_relay_on
   * Referenced by: Relay
   */
  35.0,

  /* Variable: batt_ptc_off
   * Referenced by: Relay
   */
  5.0,

  /* Variable: batt_ptc_on
   * Referenced by: Relay
   */
  15.0,

  /* Variable: batt_pump_max_off
   * Referenced by: Relay
   */
  40.0,

  /* Variable: batt_pump_max_on
   * Referenced by: Relay
   */
  45.0,

  /* Mask Parameter: PIDController_I
   * Referenced by: Integral Gain
   */
  0.0066666666666666671,

  /* Mask Parameter: PIDController_I_g
   * Referenced by: Integral Gain
   */
  0.2,

  /* Mask Parameter: PIDController1_I
   * Referenced by: Integral Gain
   */
  0.2,

  /* Mask Parameter: PIDController_InitialConditionF
   * Referenced by: Integrator
   */
  0.0,

  /* Mask Parameter: PIDController_InitialConditio_e
   * Referenced by: Integrator
   */
  0.0,

  /* Mask Parameter: PIDController1_InitialCondition
   * Referenced by: Integrator
   */
  0.0,

  /* Mask Parameter: PIDController_Kb
   * Referenced by: Kb
   */
  1.0,

  /* Mask Parameter: PIDController_Kb_b
   * Referenced by: Kb
   */
  1.0,

  /* Mask Parameter: PIDController1_Kb
   * Referenced by: Kb
   */
  1.0,

  /* Mask Parameter: PIDController_LowerSaturationLi
   * Referenced by: Saturation
   */
  0.0,

  /* Mask Parameter: PIDController_LowerSaturation_p
   * Referenced by: Saturation
   */
  0.0,

  /* Mask Parameter: PIDController1_LowerSaturationL
   * Referenced by: Saturation
   */
  0.0,

  /* Mask Parameter: PIDController_P
   * Referenced by: Proportional Gain
   */
  1.0,

  /* Mask Parameter: PIDController_P_h
   * Referenced by: Proportional Gain
   */
  0.02,

  /* Mask Parameter: PIDController1_P
   * Referenced by: Proportional Gain
   */
  1.0,

  /* Mask Parameter: PIDController_UpperSaturationLi
   * Referenced by: Saturation
   */
  1.0,

  /* Mask Parameter: PIDController_UpperSaturation_j
   * Referenced by: Saturation
   */
  1.0,

  /* Mask Parameter: PIDController1_UpperSaturationL
   * Referenced by: Saturation
   */
  1.0,

  /* Expression: [0 0 1 1]
   * Referenced by: Freezing Cutoff
   */
  { 0.0, 0.0, 1.0, 1.0 },

  /* Expression: [0 0.15 0.25 0.4]
   * Referenced by: Freezing Cutoff
   */
  { 0.0, 0.15, 0.25, 0.4 },

  /* Expression: 0.3
   * Referenced by: Constant
   */
  0.3,

  /* Expression: 0.5
   * Referenced by: Constant1
   */
  0.5,

  /* Expression: 0.5
   * Referenced by: Switch1
   */
  0.5,

  /* Expression: 0
   * Referenced by: Constant
   */
  0.0,

  /* Expression: 15
   * Referenced by: Relay
   */
  15.0,

  /* Expression: 10
   * Referenced by: Relay
   */
  10.0,

  /* Expression: 0
   * Referenced by: Relay
   */
  0.0,

  /* Expression: 1
   * Referenced by: Relay
   */
  1.0,

  /* Expression: [2.0 2.0 1.8 1.5 1.3]
   * Referenced by: 1-D Lookup Table
   */
  { 2.0, 2.0, 1.8, 1.5, 1.3 },

  /* Expression: [0 20 30 40 50]
   * Referenced by: 1-D Lookup Table
   */
  { 0.0, 20.0, 30.0, 40.0, 50.0 },

  /* Expression: 0.4
   * Referenced by: Bias
   */
  0.4,

  /* Expression: 1.5
   * Referenced by: Relay
   */
  1.5,

  /* Expression: 0.5
   * Referenced by: Relay
   */
  0.5,

  /* Expression: 1
   * Referenced by: Relay
   */
  1.0,

  /* Expression: 0
   * Referenced by: Relay
   */
  0.0,

  /* Expression: [1.4 1.4 1.3 1.2 1.1]
   * Referenced by: 1-D Lookup Table1
   */
  { 1.4, 1.4, 1.3, 1.2, 1.1 },

  /* Expression: [0 20 30 40 50]
   * Referenced by: 1-D Lookup Table1
   */
  { 0.0, 20.0, 30.0, 40.0, 50.0 },

  /* Expression: 0.4
   * Referenced by: Bias1
   */
  0.4,

  /* Expression: 1.5
   * Referenced by: Relay
   */
  1.5,

  /* Expression: 0.5
   * Referenced by: Relay
   */
  0.5,

  /* Expression: 1
   * Referenced by: Relay
   */
  1.0,

  /* Expression: 0
   * Referenced by: Relay
   */
  0.0,

  /* Expression: [0.8 0.8 0.8 0.8 0.8]
   * Referenced by: 1-D Lookup Table2
   */
  { 0.8, 0.8, 0.8, 0.8, 0.8 },

  /* Expression: [0 20 30 40 50]
   * Referenced by: 1-D Lookup Table2
   */
  { 0.0, 20.0, 30.0, 40.0, 50.0 },

  /* Expression: 0.3
   * Referenced by: Bias2
   */
  0.3,

  /* Expression: 1.5
   * Referenced by: Relay
   */
  1.5,

  /* Expression: 0.5
   * Referenced by: Relay
   */
  0.5,

  /* Expression: 1
   * Referenced by: Relay
   */
  1.0,

  /* Expression: 0
   * Referenced by: Relay
   */
  0.0,

  /* Expression: 1/3
   * Referenced by: Gain
   */
  0.33333333333333331,

  /* Expression: 0.3
   * Referenced by: Pressure Target [MPa]
   */
  0.3,

  /* Expression: 1
   * Referenced by: Constant
   */
  1.0,

  /* Expression: 35
   * Referenced by: Relay
   */
  35.0,

  /* Expression: 30
   * Referenced by: Relay
   */
  30.0,

  /* Expression: 0
   * Referenced by: Relay
   */
  0.0,

  /* Expression: 1
   * Referenced by: Relay
   */
  1.0,

  /* Expression: 0
   * Referenced by: Constant1
   */
  0.0,

  /* Expression: 0.5
   * Referenced by: Switch
   */
  0.5,

  /* Expression: 0
   * Referenced by: Constant
   */
  0.0,

  /* Expression: 0
   * Referenced by: Switch
   */
  0.0,

  /* Expression: 95
   * Referenced by: Relay Level 3
   */
  95.0,

  /* Expression: 86
   * Referenced by: Relay Level 3
   */
  86.0,

  /* Expression: 1
   * Referenced by: Relay Level 3
   */
  1.0,

  /* Expression: 0
   * Referenced by: Relay Level 3
   */
  0.0,

  /* Expression: 85
   * Referenced by: Relay Level 2
   */
  85.0,

  /* Expression: 76
   * Referenced by: Relay Level 2
   */
  76.0,

  /* Expression: 1
   * Referenced by: Relay Level 2
   */
  1.0,

  /* Expression: 0
   * Referenced by: Relay Level 2
   */
  0.0,

  /* Expression: 75
   * Referenced by: Relay Level 1
   */
  75.0,

  /* Expression: 65
   * Referenced by: Relay Level 1
   */
  65.0,

  /* Expression: 1
   * Referenced by: Relay Level 1
   */
  1.0,

  /* Expression: 0
   * Referenced by: Relay Level 1
   */
  0.0,

  /* Expression: 1/3
   * Referenced by: Gain
   */
  0.33333333333333331,

  /* Expression: [0 0 0.1 0.3 0.5 0.7 1 1]
   * Referenced by: 1-D Lookup Table
   */
  { 0.0, 0.0, 0.1, 0.3, 0.5, 0.7, 1.0, 1.0 },

  /* Expression: [-50 45 48 52 58 60 75 130]
   * Referenced by: 1-D Lookup Table
   */
  { -50.0, 45.0, 48.0, 52.0, 58.0, 60.0, 75.0, 130.0 },

  /* Expression: 0
   * Referenced by: Constant
   */
  0.0,

  /* Expression: 0
   * Referenced by: Relay
   */
  0.0,

  /* Expression: 1
   * Referenced by: Relay
   */
  1.0,

  /* Expression: 5
   * Referenced by: Switch
   */
  5.0,

  /* Expression: [0 0 0.1 0.3 0.5 0.7 1 1]
   * Referenced by: 1-D Lookup Table
   */
  { 0.0, 0.0, 0.1, 0.3, 0.5, 0.7, 1.0, 1.0 },

  /* Expression: [-50 45 48 52 58 60 75 130]
   * Referenced by: 1-D Lookup Table
   */
  { -50.0, 45.0, 48.0, 52.0, 58.0, 60.0, 75.0, 130.0 },

  /* Expression: 1
   * Referenced by: Saturation
   */
  1.0,

  /* Expression: 0.3
   * Referenced by: Saturation
   */
  0.3,

  /* Expression: 35
   * Referenced by: Relay
   */
  35.0,

  /* Expression: 30
   * Referenced by: Relay
   */
  30.0,

  /* Expression: 0
   * Referenced by: Relay
   */
  0.0,

  /* Expression: 1
   * Referenced by: Relay
   */
  1.0,

  /* Expression: 0
   * Referenced by: Relay
   */
  0.0,

  /* Expression: 1
   * Referenced by: Relay
   */
  1.0,

  /* Expression: 0.5
   * Referenced by: Switch
   */
  0.5,

  /* Expression: 1
   * Referenced by: Relay
   */
  1.0,

  /* Expression: 0
   * Referenced by: Relay
   */
  0.0,

  /* Expression: 0.5
   * Referenced by: Switch
   */
  0.5,

  /* Expression: 0
   * Referenced by: Constant
   */
  0.0,

  /* Expression: 45
   * Referenced by: Relay
   */
  45.0,

  /* Expression: 35
   * Referenced by: Relay
   */
  35.0,

  /* Expression: 0
   * Referenced by: Relay
   */
  0.0,

  /* Expression: 1
   * Referenced by: Relay
   */
  1.0,

  /* Expression: 0
   * Referenced by: Switch
   */
  0.0,

  /* Expression: 0
   * Referenced by: Constant2
   */
  0.0,

  /* Expression: 0.5
   * Referenced by: Switch1
   */
  0.5,

  /* Expression: 1
   * Referenced by: Constant1
   */
  1.0,

  /* Expression: 0
   * Referenced by: Constant
   */
  0.0
};



