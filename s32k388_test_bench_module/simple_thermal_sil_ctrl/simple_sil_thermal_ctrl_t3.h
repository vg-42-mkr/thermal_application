/*
 * simple_sil_thermal_ctrl_t3.h
 */

#ifndef simple_sil_thermal_ctrl_t3_h_
#define simple_sil_thermal_ctrl_t3_h_
#ifndef simple_sil_thermal_ctrl_t3_COMMON_INCLUDES_
#define simple_sil_thermal_ctrl_t3_COMMON_INCLUDES_
#include "simple_sil_thermal_ctrl_t4_math.h"
#include "math.h"
#endif                         /* simple_sil_thermal_ctrl_t3_COMMON_INCLUDES_ */

#include "simple_sil_thermal_ctrl_t3_types.h"
#include <float.h>
#include <string.h>
#include <stddef.h>

/* Macros for accessing real-time model data structure */
#ifndef rtmGetContStateDisabled
#define rtmGetContStateDisabled(rtm)   ((rtm)->contStateDisabled)
#endif

#ifndef rtmSetContStateDisabled
#define rtmSetContStateDisabled(rtm, val) ((rtm)->contStateDisabled = (val))
#endif

#ifndef rtmGetContStates
#define rtmGetContStates(rtm)          ((rtm)->contStates)
#endif

#ifndef rtmSetContStates
#define rtmSetContStates(rtm, val)     ((rtm)->contStates = (val))
#endif

#ifndef rtmGetContTimeOutputInconsistentWithStateAtMajorStepFlag
#define rtmGetContTimeOutputInconsistentWithStateAtMajorStepFlag(rtm) ((rtm)->CTOutputIncnstWithState)
#endif

#ifndef rtmSetContTimeOutputInconsistentWithStateAtMajorStepFlag
#define rtmSetContTimeOutputInconsistentWithStateAtMajorStepFlag(rtm, val) ((rtm)->CTOutputIncnstWithState = (val))
#endif

#ifndef rtmGetDerivCacheNeedsReset
#define rtmGetDerivCacheNeedsReset(rtm) ((rtm)->derivCacheNeedsReset)
#endif

#ifndef rtmSetDerivCacheNeedsReset
#define rtmSetDerivCacheNeedsReset(rtm, val) ((rtm)->derivCacheNeedsReset = (val))
#endif

#ifndef rtmGetFinalTime
#define rtmGetFinalTime(rtm)           ((rtm)->Timing.tFinal)
#endif

#ifndef rtmGetIntgData
#define rtmGetIntgData(rtm)            ((rtm)->intgData)
#endif

#ifndef rtmSetIntgData
#define rtmSetIntgData(rtm, val)       ((rtm)->intgData = (val))
#endif

#ifndef rtmGetOdeF
#define rtmGetOdeF(rtm)                ((rtm)->odeF)
#endif

#ifndef rtmSetOdeF
#define rtmSetOdeF(rtm, val)           ((rtm)->odeF = (val))
#endif

#ifndef rtmGetOdeY
#define rtmGetOdeY(rtm)                ((rtm)->odeY)
#endif

#ifndef rtmSetOdeY
#define rtmSetOdeY(rtm, val)           ((rtm)->odeY = (val))
#endif

#ifndef rtmGetPeriodicContStateIndices
#define rtmGetPeriodicContStateIndices(rtm) ((rtm)->periodicContStateIndices)
#endif

#ifndef rtmSetPeriodicContStateIndices
#define rtmSetPeriodicContStateIndices(rtm, val) ((rtm)->periodicContStateIndices = (val))
#endif

#ifndef rtmGetPeriodicContStateRanges
#define rtmGetPeriodicContStateRanges(rtm) ((rtm)->periodicContStateRanges)
#endif

#ifndef rtmSetPeriodicContStateRanges
#define rtmSetPeriodicContStateRanges(rtm, val) ((rtm)->periodicContStateRanges = (val))
#endif

#ifndef rtmGetZCCacheNeedsReset
#define rtmGetZCCacheNeedsReset(rtm)   ((rtm)->zCCacheNeedsReset)
#endif

#ifndef rtmSetZCCacheNeedsReset
#define rtmSetZCCacheNeedsReset(rtm, val) ((rtm)->zCCacheNeedsReset = (val))
#endif

#ifndef rtmGetdX
#define rtmGetdX(rtm)                  ((rtm)->derivs)
#endif

#ifndef rtmSetdX
#define rtmSetdX(rtm, val)             ((rtm)->derivs = (val))
#endif

#ifndef rtmGetErrorStatus
#define rtmGetErrorStatus(rtm)         ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
#define rtmSetErrorStatus(rtm, val)    ((rtm)->errorStatus = (val))
#endif

#ifndef rtmGetStopRequested
#define rtmGetStopRequested(rtm)       ((rtm)->Timing.stopRequestedFlag)
#endif

#ifndef rtmSetStopRequested
#define rtmSetStopRequested(rtm, val)  ((rtm)->Timing.stopRequestedFlag = (val))
#endif

#ifndef rtmGetStopRequestedPtr
#define rtmGetStopRequestedPtr(rtm)    (&((rtm)->Timing.stopRequestedFlag))
#endif

#ifndef rtmGetT
#define rtmGetT(rtm)                   (rtmGetTPtr((rtm))[0])
#endif

#ifndef rtmGetTFinal
#define rtmGetTFinal(rtm)              ((rtm)->Timing.tFinal)
#endif

#ifndef rtmGetTPtr
#define rtmGetTPtr(rtm)                ((rtm)->Timing.t)
#endif

#ifndef rtmGetTStart
#define rtmGetTStart(rtm)              ((rtm)->Timing.tStart)
#endif

/* Block signals (default storage) */
typedef struct {
  real_T Gain;
  real_T Sum;
  real_T Gain_h;
  real_T uDLookupTable;
  real_T Relay;
  real_T Relay_d;
  real_T SumI4;
  real_T SumI4_d;
  real_T SumI4_h;
} B_simple_sil_thermal_ctrl_t3_T;

/* Block states (default storage) for system '<Root>' */
typedef struct {
  uint32_T m_bpIndex;
  uint32_T m_bpIndex_e;
  uint32_T m_bpIndex_h;
  uint32_T m_bpIndex_k;
  uint32_T m_bpIndex_b;
  uint32_T m_bpIndex_g;
  boolean_T Relay_Mode;
  boolean_T Relay_Mode_h;
  boolean_T Relay_Mode_k;
  boolean_T Relay_Mode_kd;
  boolean_T Relay_Mode_o;
  boolean_T RelayLevel3_Mode;
  boolean_T RelayLevel2_Mode;
  boolean_T RelayLevel1_Mode;
  boolean_T Relay_Mode_c;
  boolean_T Relay_Mode_e;
  boolean_T Relay_Mode_a;
  boolean_T Relay_Mode_m;
  boolean_T Relay_Mode_g;
} DW_simple_sil_thermal_ctrl_t3_T;

/* Continuous states (default storage) */
typedef struct {
  real_T Integrator_CSTATE;
  real_T Integrator_CSTATE_a;
  real_T Integrator_CSTATE_h;
} X_simple_sil_thermal_ctrl_t3_T;

/* State derivatives (default storage) */
typedef struct {
  real_T Integrator_CSTATE;
  real_T Integrator_CSTATE_a;
  real_T Integrator_CSTATE_h;
} XDot_simple_sil_thermal_ctrl__T;

/* State disabled  */
typedef struct {
  boolean_T Integrator_CSTATE;
  boolean_T Integrator_CSTATE_a;
  boolean_T Integrator_CSTATE_h;
} XDis_simple_sil_thermal_ctrl__T;

#ifndef ODE3_INTG
#define ODE3_INTG

/* ODE3 Integration Data */
typedef struct {
  real_T *y;                           /* output */
  real_T *f[3];                        /* derivatives */
} ODE3_IntgData;

#endif

/* External inputs (root inport signals with default storage) */
typedef struct {
  real_T env_temp_degC;                /* env_temp_degC */
  real_T coolant_rad_out_temp_degC;    /* coolant_rad_out_temp_degC */
  real_T inverter_temp_degC;           /* inverter_temp_degC */
  real_T motor_temp_degC;              /* motor_temp_degC */
  real_T coolant_batt_in_temp_degC;    /* coolant_batt_in_temp_degC */
  real_T battery_temp_max_degC;        /* battery_temp_max_degC */
  real_T battery_temp_min_degC;        /* battery_temp_min_degC */
  real_T cabin_temp_degC;              /* cabin_temp_degC */
  real_T cabin_temp_setpoint_degC;     /* cabin_temp_setpoint_degC */
  real_T hvac_blower_enum;             /* hvac_blower_enum */
  real_T defrost_bool;                 /* defrost_bool */
  real_T ac_bool;                      /* ac_bool */
  real_T ads_temp_degC;                /* ads_temp_degC */
  real_T ads_rh_perc;                  /* ads_rh_perc */
  real_T photo_wpm2;                   /* photo_wpm2 */
  real_T vehicle_spd_kph;              /* vehicle_spd_kph */
  real_T suction_temp_degC;            /* suction_temp_degC */
  real_T suction_press_psig;           /* suction_press_psig */
  real_T rts_temp_degC;                /* rts_temp_degC */
  real_T discharge_temp_degC;          /* discharge_temp_degC */
  real_T discharge_press_psig;         /* discharge_press_psig */
  real_T xtemp_batt_trgt_temp_degC;    /* xtemp_batt_trgt_temp_degC */
  real_T xtemp_power_comp_cabin_limit_w;
                                   /* xtemp_power_comp_cabin_limit_w */
  real_T xtem_power_ptc_cabin_limit_w;
                                     /* xtem_power_ptc_cabin_limit_w */
  real_T xtem_temp_inv_in_trgt_degC;   /* xtem_temp_inv_in_trgt_degC */
} ExtU_simple_sil_thermal_ctrl__T;

/* External outputs (root outports fed by signals with default storage) */
typedef struct {
  real_T cmd_aaf_enum;                 /* cmd_aaf_enum */
  real_T cmd_fan_perc;                 /* cmd_fan_perc */
  real_T cmd_batt_ptc_bool;            /* cmd_batt_ptc_bool */
  real_T cmd_motor_pump_perc;          /* cmd_motor_pump_perc */
  real_T cmd_batt_ewp_perc;            /* cmd_batt_ewp_perc */
  real_T cmd_multi_valve_enum;         /* cmd_multi_valve_enum */
  real_T cmd_blower_enum;              /* cmd_blower_enum */
  real_T cmd_cabin_ptc_perc;           /* cmd_cabin_ptc_perc */
  real_T cmd_comp_perc;                /* cmd_comp_perc */
  real_T cmd_batt_exv_perc;            /* cmd_batt_exv_perc */
  real_T cmd_hp_exv_perc;              /* cmd_hp_exv_perc */
  real_T heat_gen_valve_bool;          /* heat_gen_valve_bool */
  real_T cmd_temp_door_l_perc;         /* cmd_temp_door_l_perc */
  real_T cmd_temp_door_r_perc;         /* cmd_temp_door_r_perc */
  real_T cmd_mode_door_l_enum;         /* cmd_mode_door_l_enum */
  real_T cmd_mode_door_r_enum;         /* cmd_mode_door_r_enum */
  real_T cmd_intake_door_bool;         /* cmd_intake_door_bool */
  real_T cmd_def_door_enum;            /* cmd_def_door_enum */
} ExtY_simple_sil_thermal_ctrl__T;

/* Parameters (default storage) */
struct P_simple_sil_thermal_ctrl_t3_T_ {
  real_T batt_chiller_bypass_relay_off;
                                      /* Variable: batt_chiller_bypass_relay_off
                                       * Referenced by: Relay
                                       */
  real_T batt_chiller_bypass_relay_on; /* Variable: batt_chiller_bypass_relay_on
                                        * Referenced by: Relay
                                        */
  real_T batt_ptc_off;                 /* Variable: batt_ptc_off
                                        * Referenced by: Relay
                                        */
  real_T batt_ptc_on;                  /* Variable: batt_ptc_on
                                        * Referenced by: Relay
                                        */
  real_T batt_pump_max_off;            /* Variable: batt_pump_max_off
                                        * Referenced by: Relay
                                        */
  real_T batt_pump_max_on;             /* Variable: batt_pump_max_on
                                        * Referenced by: Relay
                                        */
  real_T PIDController_I;              /* Mask Parameter: PIDController_I
                                        * Referenced by: Integral Gain
                                        */
  real_T PIDController_I_g;            /* Mask Parameter: PIDController_I_g
                                        * Referenced by: Integral Gain
                                        */
  real_T PIDController1_I;             /* Mask Parameter: PIDController1_I
                                        * Referenced by: Integral Gain
                                        */
  real_T PIDController_InitialConditionF;
                              /* Mask Parameter: PIDController_InitialConditionF
                               * Referenced by: Integrator
                               */
  real_T PIDController_InitialConditio_e;
                              /* Mask Parameter: PIDController_InitialConditio_e
                               * Referenced by: Integrator
                               */
  real_T PIDController1_InitialCondition;
                              /* Mask Parameter: PIDController1_InitialCondition
                               * Referenced by: Integrator
                               */
  real_T PIDController_Kb;             /* Mask Parameter: PIDController_Kb
                                        * Referenced by: Kb
                                        */
  real_T PIDController_Kb_b;           /* Mask Parameter: PIDController_Kb_b
                                        * Referenced by: Kb
                                        */
  real_T PIDController1_Kb;            /* Mask Parameter: PIDController1_Kb
                                        * Referenced by: Kb
                                        */
  real_T PIDController_LowerSaturationLi;
                              /* Mask Parameter: PIDController_LowerSaturationLi
                               * Referenced by: Saturation
                               */
  real_T PIDController_LowerSaturation_p;
                              /* Mask Parameter: PIDController_LowerSaturation_p
                               * Referenced by: Saturation
                               */
  real_T PIDController1_LowerSaturationL;
                              /* Mask Parameter: PIDController1_LowerSaturationL
                               * Referenced by: Saturation
                               */
  real_T PIDController_P;              /* Mask Parameter: PIDController_P
                                        * Referenced by: Proportional Gain
                                        */
  real_T PIDController_P_h;            /* Mask Parameter: PIDController_P_h
                                        * Referenced by: Proportional Gain
                                        */
  real_T PIDController1_P;             /* Mask Parameter: PIDController1_P
                                        * Referenced by: Proportional Gain
                                        */
  real_T PIDController_UpperSaturationLi;
                              /* Mask Parameter: PIDController_UpperSaturationLi
                               * Referenced by: Saturation
                               */
  real_T PIDController_UpperSaturation_j;
                              /* Mask Parameter: PIDController_UpperSaturation_j
                               * Referenced by: Saturation
                               */
  real_T PIDController1_UpperSaturationL;
                              /* Mask Parameter: PIDController1_UpperSaturationL
                               * Referenced by: Saturation
                               */
  real_T FreezingCutoff_tableData[4];  /* Expression: [0 0 1 1]
                                        * Referenced by: Freezing Cutoff
                                        */
  real_T FreezingCutoff_bp01Data[4];   /* Expression: [0 0.15 0.25 0.4]
                                        * Referenced by: Freezing Cutoff
                                        */
  real_T Constant_Value;               /* Expression: 0.3
                                        * Referenced by: Constant
                                        */
  real_T Constant1_Value;              /* Expression: 0.5
                                        * Referenced by: Constant1
                                        */
  real_T Switch1_Threshold;            /* Expression: 0.5
                                        * Referenced by: Switch1
                                        */
  real_T Constant_Value_k;             /* Expression: 0
                                        * Referenced by: Constant
                                        */
  real_T Relay_OnVal;                  /* Expression: 15
                                        * Referenced by: Relay
                                        */
  real_T Relay_OffVal;                 /* Expression: 10
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOn;                    /* Expression: 0
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOff;                   /* Expression: 1
                                        * Referenced by: Relay
                                        */
  real_T uDLookupTable_tableData[5];   /* Expression: [2.0 2.0 1.8 1.5 1.3]
                                        * Referenced by: 1-D Lookup Table
                                        */
  real_T uDLookupTable_bp01Data[5];    /* Expression: [0 20 30 40 50]
                                        * Referenced by: 1-D Lookup Table
                                        */
  real_T Bias_Bias;                    /* Expression: 0.4
                                        * Referenced by: Bias
                                        */
  real_T Relay_OnVal_k;                /* Expression: 1.5
                                        * Referenced by: Relay
                                        */
  real_T Relay_OffVal_n;               /* Expression: 0.5
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOn_h;                  /* Expression: 1
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOff_f;                 /* Expression: 0
                                        * Referenced by: Relay
                                        */
  real_T uDLookupTable1_tableData[5];  /* Expression: [1.4 1.4 1.3 1.2 1.1]
                                        * Referenced by: 1-D Lookup Table1
                                        */
  real_T uDLookupTable1_bp01Data[5];   /* Expression: [0 20 30 40 50]
                                        * Referenced by: 1-D Lookup Table1
                                        */
  real_T Bias1_Bias;                   /* Expression: 0.4
                                        * Referenced by: Bias1
                                        */
  real_T Relay_OnVal_j;                /* Expression: 1.5
                                        * Referenced by: Relay
                                        */
  real_T Relay_OffVal_e;               /* Expression: 0.5
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOn_m;                  /* Expression: 1
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOff_b;                 /* Expression: 0
                                        * Referenced by: Relay
                                        */
  real_T uDLookupTable2_tableData[5];  /* Expression: [0.8 0.8 0.8 0.8 0.8]
                                        * Referenced by: 1-D Lookup Table2
                                        */
  real_T uDLookupTable2_bp01Data[5];   /* Expression: [0 20 30 40 50]
                                        * Referenced by: 1-D Lookup Table2
                                        */
  real_T Bias2_Bias;                   /* Expression: 0.3
                                        * Referenced by: Bias2
                                        */
  real_T Relay_OnVal_i;                /* Expression: 1.5
                                        * Referenced by: Relay
                                        */
  real_T Relay_OffVal_f;               /* Expression: 0.5
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOn_l;                  /* Expression: 1
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOff_e;                 /* Expression: 0
                                        * Referenced by: Relay
                                        */
  real_T Gain_Gain;                    /* Expression: 1/3
                                        * Referenced by: Gain
                                        */
  real_T PressureTargetMPa_Value;      /* Expression: 0.3
                                        * Referenced by: Pressure Target [MPa]
                                        */
  real_T Constant_Value_k5;            /* Expression: 1
                                        * Referenced by: Constant
                                        */
  real_T Relay_OnVal_b;                /* Expression: 35
                                        * Referenced by: Relay
                                        */
  real_T Relay_OffVal_ep;              /* Expression: 30
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOn_i;                  /* Expression: 0
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOff_h;                 /* Expression: 1
                                        * Referenced by: Relay
                                        */
  real_T Constant1_Value_p;            /* Expression: 0
                                        * Referenced by: Constant1
                                        */
  real_T Switch_Threshold;             /* Expression: 0.5
                                        * Referenced by: Switch
                                        */
  real_T Constant_Value_c;             /* Expression: 0
                                        * Referenced by: Constant
                                        */
  real_T Switch_Threshold_a;           /* Expression: 0
                                        * Referenced by: Switch
                                        */
  real_T RelayLevel3_OnVal;            /* Expression: 95
                                        * Referenced by: Relay Level 3
                                        */
  real_T RelayLevel3_OffVal;           /* Expression: 86
                                        * Referenced by: Relay Level 3
                                        */
  real_T RelayLevel3_YOn;              /* Expression: 1
                                        * Referenced by: Relay Level 3
                                        */
  real_T RelayLevel3_YOff;             /* Expression: 0
                                        * Referenced by: Relay Level 3
                                        */
  real_T RelayLevel2_OnVal;            /* Expression: 85
                                        * Referenced by: Relay Level 2
                                        */
  real_T RelayLevel2_OffVal;           /* Expression: 76
                                        * Referenced by: Relay Level 2
                                        */
  real_T RelayLevel2_YOn;              /* Expression: 1
                                        * Referenced by: Relay Level 2
                                        */
  real_T RelayLevel2_YOff;             /* Expression: 0
                                        * Referenced by: Relay Level 2
                                        */
  real_T RelayLevel1_OnVal;            /* Expression: 75
                                        * Referenced by: Relay Level 1
                                        */
  real_T RelayLevel1_OffVal;           /* Expression: 65
                                        * Referenced by: Relay Level 1
                                        */
  real_T RelayLevel1_YOn;              /* Expression: 1
                                        * Referenced by: Relay Level 1
                                        */
  real_T RelayLevel1_YOff;             /* Expression: 0
                                        * Referenced by: Relay Level 1
                                        */
  real_T Gain_Gain_o;                  /* Expression: 1/3
                                        * Referenced by: Gain
                                        */
  real_T uDLookupTable_tableData_o[8]; /* Expression: [0 0 0.1 0.3 0.5 0.7 1 1]
                                        * Referenced by: 1-D Lookup Table
                                        */
  real_T uDLookupTable_bp01Data_b[8]; /* Expression: [-50 45 48 52 58 60 75 130]
                                       * Referenced by: 1-D Lookup Table
                                       */
  real_T Constant_Value_ch;            /* Expression: 0
                                        * Referenced by: Constant
                                        */
  real_T Relay_YOn_j;                  /* Expression: 0
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOff_g;                 /* Expression: 1
                                        * Referenced by: Relay
                                        */
  real_T Switch_Threshold_e;           /* Expression: 5
                                        * Referenced by: Switch
                                        */
  real_T uDLookupTable_tableData_f[8]; /* Expression: [0 0 0.1 0.3 0.5 0.7 1 1]
                                        * Referenced by: 1-D Lookup Table
                                        */
  real_T uDLookupTable_bp01Data_bm[8];/* Expression: [-50 45 48 52 58 60 75 130]
                                       * Referenced by: 1-D Lookup Table
                                       */
  real_T Saturation_UpperSat;          /* Expression: 1
                                        * Referenced by: Saturation
                                        */
  real_T Saturation_LowerSat;          /* Expression: 0.3
                                        * Referenced by: Saturation
                                        */
  real_T Relay_OnVal_c;                /* Expression: 35
                                        * Referenced by: Relay
                                        */
  real_T Relay_OffVal_o;               /* Expression: 30
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOn_a;                  /* Expression: 0
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOff_k;                 /* Expression: 1
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOn_i1;                 /* Expression: 0
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOff_a;                 /* Expression: 1
                                        * Referenced by: Relay
                                        */
  real_T Switch_Threshold_f;           /* Expression: 0.5
                                        * Referenced by: Switch
                                        */
  real_T Relay_YOn_b;                  /* Expression: 1
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOff_d;                 /* Expression: 0
                                        * Referenced by: Relay
                                        */
  real_T Switch_Threshold_n;           /* Expression: 0.5
                                        * Referenced by: Switch
                                        */
  real_T Constant_Value_a;             /* Expression: 0
                                        * Referenced by: Constant
                                        */
  real_T Relay_OnVal_n;                /* Expression: 45
                                        * Referenced by: Relay
                                        */
  real_T Relay_OffVal_h;               /* Expression: 35
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOn_ih;                 /* Expression: 0
                                        * Referenced by: Relay
                                        */
  real_T Relay_YOff_p;                 /* Expression: 1
                                        * Referenced by: Relay
                                        */
  real_T Switch_Threshold_p;           /* Expression: 0
                                        * Referenced by: Switch
                                        */
  real_T Constant2_Value;              /* Expression: 0
                                        * Referenced by: Constant2
                                        */
  real_T Switch1_Threshold_h;          /* Expression: 0.5
                                        * Referenced by: Switch1
                                        */
  real_T Constant1_Value_l;            /* Expression: 1
                                        * Referenced by: Constant1
                                        */
  real_T Constant_Value_b;             /* Expression: 0
                                        * Referenced by: Constant
                                        */
};

/* Real-time Model Data Structure */
struct tag_RTM_simple_sil_thermal_ct_T {
  const char_T *errorStatus;
  SimSolverInfo solverInfo;
  X_simple_sil_thermal_ctrl_t3_T *contStates;
  int_T *periodicContStateIndices;
  real_T *periodicContStateRanges;
  real_T *derivs;
  XDis_simple_sil_thermal_ctrl__T *contStateDisabled;
  boolean_T zCCacheNeedsReset;
  boolean_T derivCacheNeedsReset;
  boolean_T CTOutputIncnstWithState;
  real_T odeY[3];
  real_T odeF[3][3];
  ODE3_IntgData intgData;

  /*
   * Sizes:
   * The following substructure contains sizes information
   * for many of the model attributes such as inputs, outputs,
   * dwork, sample times, etc.
   */
  struct {
    int_T numContStates;
    int_T numPeriodicContStates;
    int_T numSampTimes;
  } Sizes;

  /*
   * Timing:
   * The following substructure contains information regarding
   * the timing information for the model.
   */
  struct {
    uint32_T clockTick0;
    uint32_T clockTickH0;
    time_T stepSize0;
    uint32_T clockTick1;
    uint32_T clockTickH1;
    time_T tStart;
    time_T tFinal;
    SimTimeStep simTimeStep;
    boolean_T stopRequestedFlag;
    time_T *t;
    time_T tArray[2];
  } Timing;
};

/* Block parameters (default storage) */
extern P_simple_sil_thermal_ctrl_t3_T simple_sil_thermal_ctrl_t3_P;

/* Block signals (default storage) */
extern B_simple_sil_thermal_ctrl_t3_T simple_sil_thermal_ctrl_t3_B;

/* Continuous states (default storage) */
extern X_simple_sil_thermal_ctrl_t3_T simple_sil_thermal_ctrl_t3_X;

/* Disabled states (default storage) */
extern XDis_simple_sil_thermal_ctrl__T simple_sil_thermal_ctrl_t3_XDis;

/* Block states (default storage) */
extern DW_simple_sil_thermal_ctrl_t3_T simple_sil_thermal_ctrl_t3_DW;

/* External inputs (root inport signals with default storage) */
extern ExtU_simple_sil_thermal_ctrl__T simple_sil_thermal_ctrl_t3_U;

/* External outputs (root outports fed by signals with default storage) */
extern ExtY_simple_sil_thermal_ctrl__T simple_sil_thermal_ctrl_t3_Y;

/* Model entry point functions */
extern void simple_sil_thermal_ctrl_t3_initialize(void);
extern void simple_sil_thermal_ctrl_t3_step(void);
extern void simple_sil_thermal_ctrl_t3_terminate(void);

/* Real-time Model object */
extern RT_MODEL_simple_sil_thermal_c_T *const simple_sil_thermal_ctrl_t3_M;


#endif                                 /* simple_sil_thermal_ctrl_t3_h_ */



