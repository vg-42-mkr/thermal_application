/*
 * simple_sil_thermal_ctrl_t3.c
 */

#include "simple_sil_thermal_ctrl_t3.h"
#include <math.h>
#include "simple_sil_thermal_ctrl_t4_math.h"
#include "simple_sil_thermal_ctrl_t3_private.h"
#include <string.h>

/* Block signals (default storage) */
B_simple_sil_thermal_ctrl_t3_T simple_sil_thermal_ctrl_t3_B;

/* Continuous states */
X_simple_sil_thermal_ctrl_t3_T simple_sil_thermal_ctrl_t3_X;

/* Disabled State Vector */
XDis_simple_sil_thermal_ctrl__T simple_sil_thermal_ctrl_t3_XDis;

/* Block states (default storage) */
DW_simple_sil_thermal_ctrl_t3_T simple_sil_thermal_ctrl_t3_DW;

/* External inputs (root inport signals with default storage) */
ExtU_simple_sil_thermal_ctrl__T simple_sil_thermal_ctrl_t3_U;

/* External outputs (root outports fed by signals with default storage) */
ExtY_simple_sil_thermal_ctrl__T simple_sil_thermal_ctrl_t3_Y;

/* Real-time model */
static RT_MODEL_simple_sil_thermal_c_T simple_sil_thermal_ctrl_t3_M_;
RT_MODEL_simple_sil_thermal_c_T *const simple_sil_thermal_ctrl_t3_M =
  &simple_sil_thermal_ctrl_t3_M_;
real_T look1_plinlxpw(real_T u0, const real_T bp0[], const real_T table[],
                      uint32_T prevIndex[], uint32_T maxIndex)
{
  real_T frac;
  real_T yL_0d0;
  uint32_T bpIdx;

  /* Column-major Lookup 1-D
     Search method: 'linear'
     Use previous index: 'on'
     Interpolation method: 'Linear point-slope'
     Extrapolation method: 'Linear'
     Use last breakpoint for index at or above upper limit: 'off'
     Remove protection against out-of-range input in generated code: 'off'
   */
  /* Prelookup - Index and Fraction
     Index Search method: 'linear'
     Extrapolation method: 'Linear'
     Use previous index: 'on'
     Use last breakpoint for index at or above upper limit: 'off'
     Remove protection against out-of-range input in generated code: 'off'
   */
  if (u0 <= bp0[0U]) {
    bpIdx = 0U;
    frac = (u0 - bp0[0U]) / (bp0[1U] - bp0[0U]);
  } else if (u0 < bp0[maxIndex]) {
    /* Linear Search */
    for (bpIdx = prevIndex[0U]; u0 < bp0[bpIdx]; bpIdx--) {
    }

    while (u0 >= bp0[bpIdx + 1U]) {
      bpIdx++;
    }

    frac = (u0 - bp0[bpIdx]) / (bp0[bpIdx + 1U] - bp0[bpIdx]);
  } else {
    bpIdx = maxIndex - 1U;
    frac = (u0 - bp0[maxIndex - 1U]) / (bp0[maxIndex] - bp0[maxIndex - 1U]);
  }

  prevIndex[0U] = bpIdx;

  /* Column-major Interpolation 1-D
     Interpolation method: 'Linear point-slope'
     Use last breakpoint for index at or above upper limit: 'off'
     Overflow mode: 'portable wrapping'
   */
  yL_0d0 = table[bpIdx];
  return (table[bpIdx + 1U] - yL_0d0) * frac + yL_0d0;
}

/*
 * This function updates continuous states using the ODE3 fixed-step
 * solver algorithm
 */
static void rt_ertODEUpdateContinuousStates(SimSolverInfo *si )
{
  /* Solver Matrices */
  static const real_T rt_ODE3_A[3] = {
    1.0/2.0, 3.0/4.0, 1.0
  };

  static const real_T rt_ODE3_B[3][3] = {
    { 1.0/2.0, 0.0, 0.0 },

    { 0.0, 3.0/4.0, 0.0 },

    { 2.0/9.0, 1.0/3.0, 4.0/9.0 }
  };

  time_T t = simSolverGetT(si);
  time_T tnew = simSolverGetSolverStopTime(si);
  time_T h = simSolverGetStepSize(si);
  real_T *x = simSolverGetContStates(si);
  ODE3_IntgData *id = (ODE3_IntgData *)simSolverGetSolverData(si);
  real_T *y = id->y;
  real_T *f0 = id->f[0];
  real_T *f1 = id->f[1];
  real_T *f2 = id->f[2];
  real_T hB[3];
  int_T i;
  int_T nXc = 3;
  simSolverSetSimTimeStep(si,MINOR_TIME_STEP);

  /* Save the state values at time t in y, we'll use x as ynew. */
  (void) memcpy(y, x,
                (uint_T)nXc*sizeof(real_T));

  /* Assumes that simSolverSetT and ModelOutputs are up-to-date */
  /* f0 = f(t,y) */
  simSolverSetdX(si, f0);
  simple_sil_thermal_ctrl_t3_derivatives();

  /* f(:,2) = feval(odefile, t + hA(1), y + f*hB(:,1), args(:)(*)); */
  hB[0] = h * rt_ODE3_B[0][0];
  for (i = 0; i < nXc; i++) {
    x[i] = y[i] + (f0[i]*hB[0]);
  }

  simSolverSetT(si, t + h*rt_ODE3_A[0]);
  simSolverSetdX(si, f1);
  simple_sil_thermal_ctrl_t3_step();
  simple_sil_thermal_ctrl_t3_derivatives();

  /* f(:,3) = feval(odefile, t + hA(2), y + f*hB(:,2), args(:)(*)); */
  for (i = 0; i <= 1; i++) {
    hB[i] = h * rt_ODE3_B[1][i];
  }

  for (i = 0; i < nXc; i++) {
    x[i] = y[i] + (f0[i]*hB[0] + f1[i]*hB[1]);
  }

  simSolverSetT(si, t + h*rt_ODE3_A[1]);
  simSolverSetdX(si, f2);
  simple_sil_thermal_ctrl_t3_step();
  simple_sil_thermal_ctrl_t3_derivatives();

  /* tnew = t + hA(3);
     ynew = y + f*hB(:,3); */
  for (i = 0; i <= 2; i++) {
    hB[i] = h * rt_ODE3_B[2][i];
  }

  for (i = 0; i < nXc; i++) {
    x[i] = y[i] + (f0[i]*hB[0] + f1[i]*hB[1] + f2[i]*hB[2]);
  }

  simSolverSetT(si, tnew);
  simSolverSetSimTimeStep(si,MAJOR_TIME_STEP);
}

/* Model step function */
void simple_sil_thermal_ctrl_t3_step(void)
{
  real_T rtb_DataTypeConversion;
  real_T rtb_Max;
  real_T rtb_ProportionalGain;
  real_T rtb_ProportionalGain_n;
  real_T rtb_Relay;
  real_T rtb_RelayLevel3;
  real_T rtb_Saturation;
  real_T rtb_Switch;
  real_T rtb_Switch1_b;
  real_T rtb_Switch_i;
  uint8_T rtb_Sum_a;
  boolean_T tmp;
  boolean_T tmp_0;
  if (simIsMajorTimeStep(simple_sil_thermal_ctrl_t3_M)) {
    /* set solver stop time */
    if (!(simple_sil_thermal_ctrl_t3_M->Timing.clockTick0+1)) {
      simSolverSetSolverStopTime(&simple_sil_thermal_ctrl_t3_M->solverInfo,
                            ((simple_sil_thermal_ctrl_t3_M->Timing.clockTickH0 +
        1) * simple_sil_thermal_ctrl_t3_M->Timing.stepSize0 * 4294967296.0));
    } else {
      simSolverSetSolverStopTime(&simple_sil_thermal_ctrl_t3_M->solverInfo,
                            ((simple_sil_thermal_ctrl_t3_M->Timing.clockTick0 +
        1) * simple_sil_thermal_ctrl_t3_M->Timing.stepSize0 +
        simple_sil_thermal_ctrl_t3_M->Timing.clockTickH0 *
        simple_sil_thermal_ctrl_t3_M->Timing.stepSize0 * 4294967296.0));
    }
  }                                    /* end MajorTimeStep */

  /* Update absolute time of base rate at minor time step */
  if (simIsMinorTimeStep(simple_sil_thermal_ctrl_t3_M)) {
    simple_sil_thermal_ctrl_t3_M->Timing.t[0] = simSolverGetT
      (&simple_sil_thermal_ctrl_t3_M->solverInfo);
  }

  /* MinMax: Max incorporates:
   *  Inport: coolant_rad_out_temp_degC
   *  Inport: env_temp_degC
   */
  rtb_Max = fmax(simple_sil_thermal_ctrl_t3_U.env_temp_degC,
                 simple_sil_thermal_ctrl_t3_U.coolant_rad_out_temp_degC);

  /* Relay: Relay incorporates:
   *  Relay: Relay
   *  Relay: Relay
   *  Relay: Relay
   *  Relay: Relay
   *  Relay: Relay
   */
  tmp = simSolverIsModeUpdateTimeStep(&simple_sil_thermal_ctrl_t3_M->solverInfo);
  if (tmp) {
    simple_sil_thermal_ctrl_t3_DW.Relay_Mode = ((rtb_Max >=
      simple_sil_thermal_ctrl_t3_P.Relay_OnVal) || ((!(rtb_Max <=
      simple_sil_thermal_ctrl_t3_P.Relay_OffVal)) &&
      simple_sil_thermal_ctrl_t3_DW.Relay_Mode));
  }

  tmp_0 = simIsMajorTimeStep(simple_sil_thermal_ctrl_t3_M);
  if (tmp_0) {
    if (simple_sil_thermal_ctrl_t3_DW.Relay_Mode) {
      /* Outport: cmd_aaf_enum incorporates:
       *  Relay: Relay
       */
      simple_sil_thermal_ctrl_t3_Y.cmd_aaf_enum =
        simple_sil_thermal_ctrl_t3_P.Relay_YOn;
    } else {
      /* Outport: cmd_aaf_enum incorporates:
       *  Relay: Relay
       */
      simple_sil_thermal_ctrl_t3_Y.cmd_aaf_enum =
        simple_sil_thermal_ctrl_t3_P.Relay_YOff;
    }
  }

  /* Lookup_n-D: 1-D Lookup Table incorporates:
   *  Inport: env_temp_degC
   */
  rtb_DataTypeConversion = look1_plinlxpw
    (simple_sil_thermal_ctrl_t3_U.env_temp_degC,
     simple_sil_thermal_ctrl_t3_P.uDLookupTable_bp01Data,
     simple_sil_thermal_ctrl_t3_P.uDLookupTable_tableData,
     &simple_sil_thermal_ctrl_t3_DW.m_bpIndex, 4U);

  /* Sum: Sum incorporates:
   *  Bias: Bias
   *  Inport: discharge_press_psig
   *  RelationalOperator: Relational Operator
   *  RelationalOperator: Relational Operator1
   */
  rtb_Sum_a = (uint8_T)((uint32_T)
                        (simple_sil_thermal_ctrl_t3_U.discharge_press_psig >=
    rtb_DataTypeConversion + simple_sil_thermal_ctrl_t3_P.Bias_Bias) + (uint32_T)
                        (simple_sil_thermal_ctrl_t3_U.discharge_press_psig >
    rtb_DataTypeConversion));

  /* Relay: Relay incorporates:
   *  DataTypeConversion: Data Type Conversion
   */
  if (tmp) {
    simple_sil_thermal_ctrl_t3_DW.Relay_Mode_h = ((rtb_Sum_a >=
      simple_sil_thermal_ctrl_t3_P.Relay_OnVal_k) || ((!(rtb_Sum_a <=
      simple_sil_thermal_ctrl_t3_P.Relay_OffVal_n)) &&
      simple_sil_thermal_ctrl_t3_DW.Relay_Mode_h));
  }

  /* Lookup_n-D: 1-D Lookup Table1 incorporates:
   *  Inport: env_temp_degC
   */
  rtb_DataTypeConversion = look1_plinlxpw
    (simple_sil_thermal_ctrl_t3_U.env_temp_degC,
     simple_sil_thermal_ctrl_t3_P.uDLookupTable1_bp01Data,
     simple_sil_thermal_ctrl_t3_P.uDLookupTable1_tableData,
     &simple_sil_thermal_ctrl_t3_DW.m_bpIndex_e, 4U);

  /* Sum: Sum incorporates:
   *  Bias: Bias1
   *  Inport: discharge_press_psig
   *  RelationalOperator: Relational Operator
   *  RelationalOperator: Relational Operator1
   */
  rtb_Sum_a = (uint8_T)((uint32_T)
                        (simple_sil_thermal_ctrl_t3_U.discharge_press_psig >=
    rtb_DataTypeConversion + simple_sil_thermal_ctrl_t3_P.Bias1_Bias) +
                        (uint32_T)
                        (simple_sil_thermal_ctrl_t3_U.discharge_press_psig >
    rtb_DataTypeConversion));

  /* Relay: Relay incorporates:
   *  DataTypeConversion: Data Type Conversion
   */
  if (tmp) {
    simple_sil_thermal_ctrl_t3_DW.Relay_Mode_k = ((rtb_Sum_a >=
      simple_sil_thermal_ctrl_t3_P.Relay_OnVal_j) || ((!(rtb_Sum_a <=
      simple_sil_thermal_ctrl_t3_P.Relay_OffVal_e)) &&
      simple_sil_thermal_ctrl_t3_DW.Relay_Mode_k));
  }

  /* Lookup_n-D: 1-D Lookup Table2 incorporates:
   *  Inport: env_temp_degC
   */
  rtb_DataTypeConversion = look1_plinlxpw
    (simple_sil_thermal_ctrl_t3_U.env_temp_degC,
     simple_sil_thermal_ctrl_t3_P.uDLookupTable2_bp01Data,
     simple_sil_thermal_ctrl_t3_P.uDLookupTable2_tableData,
     &simple_sil_thermal_ctrl_t3_DW.m_bpIndex_h, 4U);

  /* Sum: Sum incorporates:
   *  Bias: Bias2
   *  Inport: discharge_press_psig
   *  RelationalOperator: Relational Operator
   *  RelationalOperator: Relational Operator1
   */
  rtb_Sum_a = (uint8_T)((uint32_T)
                        (simple_sil_thermal_ctrl_t3_U.discharge_press_psig >=
    rtb_DataTypeConversion + simple_sil_thermal_ctrl_t3_P.Bias2_Bias) +
                        (uint32_T)
                        (simple_sil_thermal_ctrl_t3_U.discharge_press_psig >
    rtb_DataTypeConversion));

  /* Relay: Relay incorporates:
   *  DataTypeConversion: Data Type Conversion
   */
  if (tmp) {
    simple_sil_thermal_ctrl_t3_DW.Relay_Mode_kd = ((rtb_Sum_a >=
      simple_sil_thermal_ctrl_t3_P.Relay_OnVal_i) || ((!(rtb_Sum_a <=
      simple_sil_thermal_ctrl_t3_P.Relay_OffVal_f)) &&
      simple_sil_thermal_ctrl_t3_DW.Relay_Mode_kd));
  }

  if (tmp_0) {
    if (simple_sil_thermal_ctrl_t3_DW.Relay_Mode_h) {
      rtb_RelayLevel3 = simple_sil_thermal_ctrl_t3_P.Relay_YOn_h;
    } else {
      rtb_RelayLevel3 = simple_sil_thermal_ctrl_t3_P.Relay_YOff_f;
    }
    if (simple_sil_thermal_ctrl_t3_DW.Relay_Mode_k) {
      rtb_Relay = simple_sil_thermal_ctrl_t3_P.Relay_YOn_m;
    } else {
      rtb_Relay = simple_sil_thermal_ctrl_t3_P.Relay_YOff_b;
    }
    if (simple_sil_thermal_ctrl_t3_DW.Relay_Mode_kd) {
      rtb_DataTypeConversion = simple_sil_thermal_ctrl_t3_P.Relay_YOn_l;
    } else {
      rtb_DataTypeConversion = simple_sil_thermal_ctrl_t3_P.Relay_YOff_e;
    }

    /* Gain: Gain incorporates:
     *  Relay: Relay
     *  Relay: Relay
     *  Relay: Relay
     *  Sum: Sum
     */
    simple_sil_thermal_ctrl_t3_B.Gain = ((rtb_RelayLevel3 + rtb_Relay) +
      rtb_DataTypeConversion) * simple_sil_thermal_ctrl_t3_P.Gain_Gain;
  }

  /* Sum: Sum1 incorporates:
   *  Constant: Pressure Target [MPa]
   *  Inport: suction_press_psig
   *  MinMax: MinMax
   */
  rtb_DataTypeConversion = fmax(simple_sil_thermal_ctrl_t3_U.suction_press_psig,
    simple_sil_thermal_ctrl_t3_U.suction_press_psig) -
    simple_sil_thermal_ctrl_t3_P.PressureTargetMPa_Value;

  /* Gain: Proportional Gain incorporates:
   *  Integrator: Integrator
   *  Sum: Sum
   */
  rtb_ProportionalGain = (rtb_DataTypeConversion +
    simple_sil_thermal_ctrl_t3_X.Integrator_CSTATE) *
    simple_sil_thermal_ctrl_t3_P.PIDController_P;
  if (rtb_ProportionalGain >
      simple_sil_thermal_ctrl_t3_P.PIDController_UpperSaturationLi) {
    rtb_Saturation =
      simple_sil_thermal_ctrl_t3_P.PIDController_UpperSaturationLi;
  } else if (rtb_ProportionalGain <
             simple_sil_thermal_ctrl_t3_P.PIDController_LowerSaturationLi) {
    rtb_Saturation =
      simple_sil_thermal_ctrl_t3_P.PIDController_LowerSaturationLi;
  } else {
    rtb_Saturation = rtb_ProportionalGain;
  }
  if (tmp_0) {
    /* Relay: Relay incorporates:
     *  Inport: battery_temp_max_degC
     */
    simple_sil_thermal_ctrl_t3_DW.Relay_Mode_o =
      ((simple_sil_thermal_ctrl_t3_U.battery_temp_max_degC >=
        simple_sil_thermal_ctrl_t3_P.Relay_OnVal_b) ||
       ((!(simple_sil_thermal_ctrl_t3_U.battery_temp_max_degC <=
           simple_sil_thermal_ctrl_t3_P.Relay_OffVal_ep)) &&
        simple_sil_thermal_ctrl_t3_DW.Relay_Mode_o));
    if (simple_sil_thermal_ctrl_t3_DW.Relay_Mode_o) {
      rtb_RelayLevel3 = simple_sil_thermal_ctrl_t3_P.Relay_YOn_i;
    } else {
      rtb_RelayLevel3 = simple_sil_thermal_ctrl_t3_P.Relay_YOff_h;
    }

    /* Sum: Sum incorporates:
     *  Constant: Constant
     *  Relay: Relay
     */
    simple_sil_thermal_ctrl_t3_B.Sum =
      simple_sil_thermal_ctrl_t3_P.Constant_Value_k5 - rtb_RelayLevel3;
  }

  /* MinMax: MinMax2 incorporates:
   *  Inport: ac_bool
   */
  rtb_Switch1_b = fmax(simple_sil_thermal_ctrl_t3_B.Sum,
                       simple_sil_thermal_ctrl_t3_U.ac_bool);

  /* Switch: Switch incorporates:
   *  Constant: Constant1
   *  Product: Product
   */
  if (rtb_Switch1_b > simple_sil_thermal_ctrl_t3_P.Switch_Threshold) {
    /* Lookup_n-D: Freezing Cutoff incorporates:
     *  Inport: suction_press_psig
     *  MinMax: MinMax1
     */
    rtb_ProportionalGain_n = look1_plinlxpw(fmin
      (simple_sil_thermal_ctrl_t3_U.suction_press_psig,
       simple_sil_thermal_ctrl_t3_U.suction_press_psig),
      simple_sil_thermal_ctrl_t3_P.FreezingCutoff_bp01Data,
      simple_sil_thermal_ctrl_t3_P.FreezingCutoff_tableData,
      &simple_sil_thermal_ctrl_t3_DW.m_bpIndex_g, 3U);
    rtb_ProportionalGain_n *= rtb_Saturation;
  } else {
    rtb_ProportionalGain_n = simple_sil_thermal_ctrl_t3_P.Constant1_Value_p;
  }
  if (tmp_0) {
    simple_sil_thermal_ctrl_t3_DW.RelayLevel3_Mode =
      ((simple_sil_thermal_ctrl_t3_P.RelayLevel3_OnVal <= 0.0) ||
       ((!(simple_sil_thermal_ctrl_t3_P.RelayLevel3_OffVal >= 0.0)) &&
        simple_sil_thermal_ctrl_t3_DW.RelayLevel3_Mode));
    simple_sil_thermal_ctrl_t3_DW.RelayLevel2_Mode =
      ((simple_sil_thermal_ctrl_t3_P.RelayLevel2_OnVal <= 0.0) ||
       ((!(simple_sil_thermal_ctrl_t3_P.RelayLevel2_OffVal >= 0.0)) &&
        simple_sil_thermal_ctrl_t3_DW.RelayLevel2_Mode));
    simple_sil_thermal_ctrl_t3_DW.RelayLevel1_Mode =
      ((simple_sil_thermal_ctrl_t3_P.RelayLevel1_OnVal <= 0.0) ||
       ((!(simple_sil_thermal_ctrl_t3_P.RelayLevel1_OffVal >= 0.0)) &&
        simple_sil_thermal_ctrl_t3_DW.RelayLevel1_Mode));
    if (simple_sil_thermal_ctrl_t3_DW.RelayLevel1_Mode) {
      rtb_Switch_i = simple_sil_thermal_ctrl_t3_P.RelayLevel1_YOn;
    } else {
      rtb_Switch_i = simple_sil_thermal_ctrl_t3_P.RelayLevel1_YOff;
    }
    if (simple_sil_thermal_ctrl_t3_DW.RelayLevel3_Mode) {
      rtb_RelayLevel3 = simple_sil_thermal_ctrl_t3_P.RelayLevel3_YOn;
    } else {
      rtb_RelayLevel3 = simple_sil_thermal_ctrl_t3_P.RelayLevel3_YOff;
    }
    if (simple_sil_thermal_ctrl_t3_DW.RelayLevel2_Mode) {
      rtb_Relay = simple_sil_thermal_ctrl_t3_P.RelayLevel2_YOn;
    } else {
      rtb_Relay = simple_sil_thermal_ctrl_t3_P.RelayLevel2_YOff;
    }

    /* Gain: Gain incorporates:
     *  Relay: Relay Level 2
     *  Relay: Relay Level 3
     *  Sum: Sum
     */
    simple_sil_thermal_ctrl_t3_B.Gain_h = ((rtb_RelayLevel3 + rtb_Relay) +
      rtb_Switch_i) * simple_sil_thermal_ctrl_t3_P.Gain_Gain_o;
    simple_sil_thermal_ctrl_t3_B.uDLookupTable = look1_plinlxpw(0.0,
      simple_sil_thermal_ctrl_t3_P.uDLookupTable_bp01Data_b,
      simple_sil_thermal_ctrl_t3_P.uDLookupTable_tableData_o,
      &simple_sil_thermal_ctrl_t3_DW.m_bpIndex_k, 7U);
  }

  /* Switch: Switch incorporates:
   *  Constant: Constant
   */
  if (rtb_ProportionalGain_n > simple_sil_thermal_ctrl_t3_P.Switch_Threshold_a)
  {
    rtb_RelayLevel3 = simple_sil_thermal_ctrl_t3_B.Gain;
  } else {
    rtb_RelayLevel3 = simple_sil_thermal_ctrl_t3_P.Constant_Value_c;
  }

  /* Outport: cmd_fan_perc incorporates:
   *  MinMax: MinMax
   *  Switch: Switch
   */
  simple_sil_thermal_ctrl_t3_Y.cmd_fan_perc = fmax(fmax(rtb_RelayLevel3,
    simple_sil_thermal_ctrl_t3_B.Gain_h),
    simple_sil_thermal_ctrl_t3_B.uDLookupTable);

  /* Relay: Relay incorporates:
   *  Inport: coolant_batt_in_temp_degC
   */
  if (tmp) {
    simple_sil_thermal_ctrl_t3_DW.Relay_Mode_c =
      ((simple_sil_thermal_ctrl_t3_U.coolant_batt_in_temp_degC >=
        simple_sil_thermal_ctrl_t3_P.batt_ptc_on) ||
       ((!(simple_sil_thermal_ctrl_t3_U.coolant_batt_in_temp_degC <=
           simple_sil_thermal_ctrl_t3_P.batt_ptc_off)) &&
        simple_sil_thermal_ctrl_t3_DW.Relay_Mode_c));
  }

  if (simple_sil_thermal_ctrl_t3_DW.Relay_Mode_c) {
    simple_sil_thermal_ctrl_t3_B.Relay =
      simple_sil_thermal_ctrl_t3_P.Relay_YOn_j;
  } else {
    simple_sil_thermal_ctrl_t3_B.Relay =
      simple_sil_thermal_ctrl_t3_P.Relay_YOff_g;
  }

  /* Switch: Switch incorporates:
   *  Inport: env_temp_degC
   */
  if (simple_sil_thermal_ctrl_t3_U.env_temp_degC >
      simple_sil_thermal_ctrl_t3_P.Switch_Threshold_e) {
    /* Outport: cmd_batt_ptc_bool incorporates:
     *  Constant: Constant
     */
    simple_sil_thermal_ctrl_t3_Y.cmd_batt_ptc_bool =
      simple_sil_thermal_ctrl_t3_P.Constant_Value_ch;
  } else {
    /* Outport: cmd_batt_ptc_bool */
    simple_sil_thermal_ctrl_t3_Y.cmd_batt_ptc_bool =
      simple_sil_thermal_ctrl_t3_B.Relay;
  }
  if (tmp_0) {
    rtb_Switch_i = look1_plinlxpw(0.0,
      simple_sil_thermal_ctrl_t3_P.uDLookupTable_bp01Data_bm,
      simple_sil_thermal_ctrl_t3_P.uDLookupTable_tableData_f,
      &simple_sil_thermal_ctrl_t3_DW.m_bpIndex_b, 7U);
    if (rtb_Switch_i > simple_sil_thermal_ctrl_t3_P.Saturation_UpperSat) {
      rtb_Switch_i = simple_sil_thermal_ctrl_t3_P.Saturation_UpperSat;
    } else if (rtb_Switch_i < simple_sil_thermal_ctrl_t3_P.Saturation_LowerSat)
    {
      rtb_Switch_i = simple_sil_thermal_ctrl_t3_P.Saturation_LowerSat;
    }

    /* Outport: cmd_motor_pump_perc */
    simple_sil_thermal_ctrl_t3_Y.cmd_motor_pump_perc = rtb_Switch_i;
  }

  /* Relay: Relay incorporates:
   *  MinMax: MinMax
   */
  if (tmp) {
    simple_sil_thermal_ctrl_t3_DW.Relay_Mode_e = ((rtb_Max >=
      simple_sil_thermal_ctrl_t3_P.Relay_OnVal_c) || ((!(rtb_Max <=
      simple_sil_thermal_ctrl_t3_P.Relay_OffVal_o)) &&
      simple_sil_thermal_ctrl_t3_DW.Relay_Mode_e));
  }

  if (tmp_0) {
    /* Relay: Relay incorporates:
     *  Inport: battery_temp_max_degC
     */
    simple_sil_thermal_ctrl_t3_DW.Relay_Mode_a =
      ((simple_sil_thermal_ctrl_t3_U.battery_temp_max_degC >=
        simple_sil_thermal_ctrl_t3_P.batt_chiller_bypass_relay_on) ||
       ((!(simple_sil_thermal_ctrl_t3_U.battery_temp_max_degC <=
           simple_sil_thermal_ctrl_t3_P.batt_chiller_bypass_relay_off)) &&
        simple_sil_thermal_ctrl_t3_DW.Relay_Mode_a));
    if (simple_sil_thermal_ctrl_t3_DW.Relay_Mode_a) {
      rtb_Relay = simple_sil_thermal_ctrl_t3_P.Relay_YOn_i1;
    } else {
      rtb_Relay = simple_sil_thermal_ctrl_t3_P.Relay_YOff_a;
    }

    /* Switch: Switch incorporates:
     *  Constant: Constant
     *  Relay: Relay
     */
    if (rtb_Relay > simple_sil_thermal_ctrl_t3_P.Switch_Threshold_f) {
      if (simple_sil_thermal_ctrl_t3_DW.Relay_Mode_e) {
        rtb_Switch = simple_sil_thermal_ctrl_t3_P.Relay_YOn_a;
      } else {
        rtb_Switch = simple_sil_thermal_ctrl_t3_P.Relay_YOff_k;
      }
    } else {
      rtb_Switch = simple_sil_thermal_ctrl_t3_P.Constant_Value_k;
    }

    /* Relay: Relay incorporates:
     *  Inport: battery_temp_max_degC
     */
    simple_sil_thermal_ctrl_t3_DW.Relay_Mode_m =
      ((simple_sil_thermal_ctrl_t3_U.battery_temp_max_degC >=
        simple_sil_thermal_ctrl_t3_P.batt_pump_max_on) ||
       ((!(simple_sil_thermal_ctrl_t3_U.battery_temp_max_degC <=
           simple_sil_thermal_ctrl_t3_P.batt_pump_max_off)) &&
        simple_sil_thermal_ctrl_t3_DW.Relay_Mode_m));

    /* Switch: Switch incorporates:
     *  MinMax: MinMax
     *  Relay: Relay
     *  Switch: Switch1
     */
    if (!(rtb_Switch > simple_sil_thermal_ctrl_t3_P.Switch_Threshold_n)) {
      if (simple_sil_thermal_ctrl_t3_DW.Relay_Mode_m) {
        rtb_RelayLevel3 = simple_sil_thermal_ctrl_t3_P.Relay_YOn_b;
      } else {
        rtb_RelayLevel3 = simple_sil_thermal_ctrl_t3_P.Relay_YOff_d;
      }

      /* Switch: Switch1 incorporates:
       *  Constant: Constant
       *  Constant: Constant1
       */
      if (rtb_Relay > simple_sil_thermal_ctrl_t3_P.Switch1_Threshold) {
        rtb_Relay = simple_sil_thermal_ctrl_t3_P.Constant_Value;
      } else {
        rtb_Relay = simple_sil_thermal_ctrl_t3_P.Constant1_Value;
      }

      rtb_Switch_i = fmax(rtb_RelayLevel3, rtb_Relay);
    }

    /* Outport: cmd_batt_ewp_perc */
    simple_sil_thermal_ctrl_t3_Y.cmd_batt_ewp_perc = rtb_Switch_i;

    /* Outport: cmd_multi_valve_enum */
    simple_sil_thermal_ctrl_t3_Y.cmd_multi_valve_enum = rtb_Switch;
  }

  /* Sum: Sum1 incorporates:
   *  Inport: cabin_temp_setpoint_degC
   *  Inport: env_temp_degC
   */
  rtb_Max = simple_sil_thermal_ctrl_t3_U.env_temp_degC -
    simple_sil_thermal_ctrl_t3_U.cabin_temp_setpoint_degC;
  if (simIsNaN(rtb_Max)) {
    rtb_RelayLevel3 = (simNaN);
  } else if (rtb_Max < 0.0) {
    rtb_RelayLevel3 = -1.0;
  } else {
    rtb_RelayLevel3 = (rtb_Max > 0.0);
  }

  /* Product: Product incorporates:
   *  Inport: cabin_temp_degC
   *  Inport: cabin_temp_setpoint_degC
   *  Signum: Sign
   *  Sum: Sum
   */
  rtb_RelayLevel3 *= simple_sil_thermal_ctrl_t3_U.cabin_temp_degC -
    simple_sil_thermal_ctrl_t3_U.cabin_temp_setpoint_degC;

  /* Gain: Proportional Gain incorporates:
   *  Integrator: Integrator
   *  Sum: Sum
   */
  rtb_Switch = (rtb_RelayLevel3 +
                simple_sil_thermal_ctrl_t3_X.Integrator_CSTATE_a) *
    simple_sil_thermal_ctrl_t3_P.PIDController_P_h;
  if (rtb_Switch > simple_sil_thermal_ctrl_t3_P.PIDController_UpperSaturation_j)
  {
    rtb_Switch_i = simple_sil_thermal_ctrl_t3_P.PIDController_UpperSaturation_j;
  } else if (rtb_Switch <
             simple_sil_thermal_ctrl_t3_P.PIDController_LowerSaturation_p) {
    rtb_Switch_i = simple_sil_thermal_ctrl_t3_P.PIDController_LowerSaturation_p;
  } else {
    rtb_Switch_i = rtb_Switch;
  }

  /* Outport: cmd_blower_enum */
  simple_sil_thermal_ctrl_t3_Y.cmd_blower_enum = rtb_Switch_i;
  if (tmp_0) {
    simple_sil_thermal_ctrl_t3_DW.Relay_Mode_g =
      ((simple_sil_thermal_ctrl_t3_P.Relay_OnVal_n <= 0.0) ||
       ((!(simple_sil_thermal_ctrl_t3_P.Relay_OffVal_h >= 0.0)) &&
        simple_sil_thermal_ctrl_t3_DW.Relay_Mode_g));
    if (simple_sil_thermal_ctrl_t3_DW.Relay_Mode_g) {
      simple_sil_thermal_ctrl_t3_B.Relay_d =
        simple_sil_thermal_ctrl_t3_P.Relay_YOn_ih;
    } else {
      simple_sil_thermal_ctrl_t3_B.Relay_d =
        simple_sil_thermal_ctrl_t3_P.Relay_YOff_p;
    }
  }
  if (rtb_Max >= simple_sil_thermal_ctrl_t3_P.Switch_Threshold_p) {
    /* Outport: cmd_cabin_ptc_perc incorporates:
     *  Constant: Constant
     */
    simple_sil_thermal_ctrl_t3_Y.cmd_cabin_ptc_perc =
      simple_sil_thermal_ctrl_t3_P.Constant_Value_a;
  } else {
    /* Outport: cmd_cabin_ptc_perc */
    simple_sil_thermal_ctrl_t3_Y.cmd_cabin_ptc_perc =
      simple_sil_thermal_ctrl_t3_B.Relay_d;
  }

  /* Outport: cmd_comp_perc */
  simple_sil_thermal_ctrl_t3_Y.cmd_comp_perc = rtb_ProportionalGain_n;

  /* Sum: Sum2 incorporates:
   *  Inport: coolant_batt_in_temp_degC
   *  Inport: xtemp_batt_trgt_temp_degC
   */
  rtb_Max = simple_sil_thermal_ctrl_t3_U.xtemp_batt_trgt_temp_degC -
    simple_sil_thermal_ctrl_t3_U.coolant_batt_in_temp_degC;

  /* Gain: Proportional Gain incorporates:
   *  Integrator: Integrator
   *  Sum: Sum
   */
  rtb_ProportionalGain_n = (rtb_Max +
    simple_sil_thermal_ctrl_t3_X.Integrator_CSTATE_h) *
    simple_sil_thermal_ctrl_t3_P.PIDController1_P;
  if (rtb_ProportionalGain_n >
      simple_sil_thermal_ctrl_t3_P.PIDController1_UpperSaturationL) {
    rtb_Relay = simple_sil_thermal_ctrl_t3_P.PIDController1_UpperSaturationL;
  } else if (rtb_ProportionalGain_n <
             simple_sil_thermal_ctrl_t3_P.PIDController1_LowerSaturationL) {
    rtb_Relay = simple_sil_thermal_ctrl_t3_P.PIDController1_LowerSaturationL;
  } else {
    rtb_Relay = rtb_ProportionalGain_n;
  }
  if (rtb_Switch1_b > simple_sil_thermal_ctrl_t3_P.Switch1_Threshold_h) {
    /* Outport: cmd_batt_exv_perc */
    simple_sil_thermal_ctrl_t3_Y.cmd_batt_exv_perc = rtb_Relay;
  } else {
    /* Outport: cmd_batt_exv_perc incorporates:
     *  Constant: Constant2
     */
    simple_sil_thermal_ctrl_t3_Y.cmd_batt_exv_perc =
      simple_sil_thermal_ctrl_t3_P.Constant2_Value;
  }

  /* Sum: SumI4 incorporates:
   *  Gain: Kb
   *  Gain: Integral Gain
   *  Sum: SumI2
   */
  simple_sil_thermal_ctrl_t3_B.SumI4 = (rtb_Switch_i - rtb_Switch) *
    simple_sil_thermal_ctrl_t3_P.PIDController_Kb +
    simple_sil_thermal_ctrl_t3_P.PIDController_I * rtb_RelayLevel3;

  /* Sum: SumI4 incorporates:
   *  Gain: Kb
   *  Gain: Integral Gain
   *  Sum: SumI2
   */
  simple_sil_thermal_ctrl_t3_B.SumI4_d = (rtb_Saturation - rtb_ProportionalGain)
    * simple_sil_thermal_ctrl_t3_P.PIDController_Kb_b +
    simple_sil_thermal_ctrl_t3_P.PIDController_I_g * rtb_DataTypeConversion;

  /* Sum: SumI4 incorporates:
   *  Gain: Kb
   *  Gain: Integral Gain
   *  Sum: SumI2
   */
  simple_sil_thermal_ctrl_t3_B.SumI4_h = (rtb_Relay - rtb_ProportionalGain_n) *
    simple_sil_thermal_ctrl_t3_P.PIDController1_Kb +
    simple_sil_thermal_ctrl_t3_P.PIDController1_I * rtb_Max;
  if (tmp_0) {
    /* Outport: cmd_hp_exv_perc incorporates:
     *  Constant: Constant1
     */
    simple_sil_thermal_ctrl_t3_Y.cmd_hp_exv_perc =
      simple_sil_thermal_ctrl_t3_P.Constant1_Value_l;

    /* Outport: heat_gen_valve_bool incorporates:
     *  Constant: Constant1
     */
    simple_sil_thermal_ctrl_t3_Y.heat_gen_valve_bool =
      simple_sil_thermal_ctrl_t3_P.Constant1_Value_l;

    /* Outport: cmd_temp_door_l_perc incorporates:
     *  Constant: Constant
     */
    simple_sil_thermal_ctrl_t3_Y.cmd_temp_door_l_perc =
      simple_sil_thermal_ctrl_t3_P.Constant_Value_b;

    /* Outport: cmd_temp_door_r_perc incorporates:
     *  Constant: Constant
     */
    simple_sil_thermal_ctrl_t3_Y.cmd_temp_door_r_perc =
      simple_sil_thermal_ctrl_t3_P.Constant_Value_b;

    /* Outport: cmd_mode_door_l_enum incorporates:
     *  Constant: Constant
     */
    simple_sil_thermal_ctrl_t3_Y.cmd_mode_door_l_enum =
      simple_sil_thermal_ctrl_t3_P.Constant_Value_b;

    /* Outport: cmd_mode_door_r_enum incorporates:
     *  Constant: Constant
     */
    simple_sil_thermal_ctrl_t3_Y.cmd_mode_door_r_enum =
      simple_sil_thermal_ctrl_t3_P.Constant_Value_b;

    /* Outport: cmd_intake_door_bool incorporates:
     *  Constant: Constant
     */
    simple_sil_thermal_ctrl_t3_Y.cmd_intake_door_bool =
      simple_sil_thermal_ctrl_t3_P.Constant_Value_b;

    /* Outport: cmd_def_door_enum incorporates:
     *  Constant: Constant
     */
    simple_sil_thermal_ctrl_t3_Y.cmd_def_door_enum =
      simple_sil_thermal_ctrl_t3_P.Constant_Value_b;
  }

  if (simIsMajorTimeStep(simple_sil_thermal_ctrl_t3_M)) {
    /* signal main to stop simulation */
    {                                  /* Sample time: [0.0s, 0.0s] */
      if ((rtmGetTFinal(simple_sil_thermal_ctrl_t3_M)!=-1) &&
          !((rtmGetTFinal(simple_sil_thermal_ctrl_t3_M)-
             (((simple_sil_thermal_ctrl_t3_M->Timing.clockTick1+
                simple_sil_thermal_ctrl_t3_M->Timing.clockTickH1* 4294967296.0))
              * 0.01)) > (((simple_sil_thermal_ctrl_t3_M->Timing.clockTick1+
                            simple_sil_thermal_ctrl_t3_M->Timing.clockTickH1*
                            4294967296.0)) * 0.01) * (DBL_EPSILON))) {
        rtmSetErrorStatus(simple_sil_thermal_ctrl_t3_M, "Simulation finished");
      }
    }

    rt_ertODEUpdateContinuousStates(&simple_sil_thermal_ctrl_t3_M->solverInfo);

    /* Update absolute time for base rate */
    /* The "clockTick0" counts the number of times the code of this task has
     * been executed. The absolute time is the multiplication of "clockTick0"
     * and "Timing.stepSize0". Size of "clockTick0" ensures timer will not
     * overflow during the application lifespan selected.
     * Timer of this task consists of two 32 bit unsigned integers.
     * The two integers represent the low bits Timing.clockTick0 and the high bits
     * Timing.clockTickH0. When the low bit overflows to 0, the high bits increment.
     */
    if (!(++simple_sil_thermal_ctrl_t3_M->Timing.clockTick0)) {
      ++simple_sil_thermal_ctrl_t3_M->Timing.clockTickH0;
    }

    simple_sil_thermal_ctrl_t3_M->Timing.t[0] = simSolverGetSolverStopTime
      (&simple_sil_thermal_ctrl_t3_M->solverInfo);

    {
      /* Update absolute timer for sample time: [0.01s, 0.0s] */
      /* The "clockTick1" counts the number of times the code of this task has
       * been executed. The resolution of this integer timer is 0.01, which is the step size
       * of the task. Size of "clockTick1" ensures timer will not overflow during the
       * application lifespan selected.
       * Timer of this task consists of two 32 bit unsigned integers.
       * The two integers represent the low bits Timing.clockTick1 and the high bits
       * Timing.clockTickH1. When the low bit overflows to 0, the high bits increment.
       */
      simple_sil_thermal_ctrl_t3_M->Timing.clockTick1++;
      if (!simple_sil_thermal_ctrl_t3_M->Timing.clockTick1) {
        simple_sil_thermal_ctrl_t3_M->Timing.clockTickH1++;
      }
    }
  }                                    /* end MajorTimeStep */
}

/* Derivatives for root system: '<Root>' */
void simple_sil_thermal_ctrl_t3_derivatives(void)
{
  XDot_simple_sil_thermal_ctrl__T *_rtXdot;
  _rtXdot = ((XDot_simple_sil_thermal_ctrl__T *)
             simple_sil_thermal_ctrl_t3_M->derivs);
  _rtXdot->Integrator_CSTATE = simple_sil_thermal_ctrl_t3_B.SumI4_d;
  _rtXdot->Integrator_CSTATE_a = simple_sil_thermal_ctrl_t3_B.SumI4;
  _rtXdot->Integrator_CSTATE_h = simple_sil_thermal_ctrl_t3_B.SumI4_h;
}

/* Model initialize function */
void simple_sil_thermal_ctrl_t3_initialize(void)
{
  /* Registration code */

  /* initialize real-time model */
  (void) memset((void *)simple_sil_thermal_ctrl_t3_M, 0,
                sizeof(RT_MODEL_simple_sil_thermal_c_T));

  {
    /* Setup solver object */
    simSolverSetSimTimeStepPtr(&simple_sil_thermal_ctrl_t3_M->solverInfo,
                          &simple_sil_thermal_ctrl_t3_M->Timing.simTimeStep);
    simSolverSetTPtr(&simple_sil_thermal_ctrl_t3_M->solverInfo, &rtmGetTPtr
                (simple_sil_thermal_ctrl_t3_M));
    simSolverSetStepSizePtr(&simple_sil_thermal_ctrl_t3_M->solverInfo,
                       &simple_sil_thermal_ctrl_t3_M->Timing.stepSize0);
    simSolverSetdXPtr(&simple_sil_thermal_ctrl_t3_M->solverInfo,
                 &simple_sil_thermal_ctrl_t3_M->derivs);
    simSolverSetContStatesPtr(&simple_sil_thermal_ctrl_t3_M->solverInfo, (real_T **)
                         &simple_sil_thermal_ctrl_t3_M->contStates);
    simSolverSetNumContStatesPtr(&simple_sil_thermal_ctrl_t3_M->solverInfo,
      &simple_sil_thermal_ctrl_t3_M->Sizes.numContStates);
    simSolverSetNumPeriodicContStatesPtr(&simple_sil_thermal_ctrl_t3_M->solverInfo,
      &simple_sil_thermal_ctrl_t3_M->Sizes.numPeriodicContStates);
    simSolverSetPeriodicContStateIndicesPtr(&simple_sil_thermal_ctrl_t3_M->solverInfo,
      &simple_sil_thermal_ctrl_t3_M->periodicContStateIndices);
    simSolverSetPeriodicContStateRangesPtr(&simple_sil_thermal_ctrl_t3_M->solverInfo,
      &simple_sil_thermal_ctrl_t3_M->periodicContStateRanges);
    simSolverSetContStateDisabledPtr(&simple_sil_thermal_ctrl_t3_M->solverInfo,
      (boolean_T**) &simple_sil_thermal_ctrl_t3_M->contStateDisabled);
    simSolverSetErrorStatusPtr(&simple_sil_thermal_ctrl_t3_M->solverInfo,
                          (&rtmGetErrorStatus(simple_sil_thermal_ctrl_t3_M)));
    simSolverSetRTModelPtr(&simple_sil_thermal_ctrl_t3_M->solverInfo,
                      simple_sil_thermal_ctrl_t3_M);
  }

  simSolverSetSimTimeStep(&simple_sil_thermal_ctrl_t3_M->solverInfo, MAJOR_TIME_STEP);
  simSolverSetIsMinorTimeStepWithModeChange(&simple_sil_thermal_ctrl_t3_M->solverInfo,
    false);
  simSolverSetIsContModeFrozen(&simple_sil_thermal_ctrl_t3_M->solverInfo, false);
  simple_sil_thermal_ctrl_t3_M->intgData.y = simple_sil_thermal_ctrl_t3_M->odeY;
  simple_sil_thermal_ctrl_t3_M->intgData.f[0] =
    simple_sil_thermal_ctrl_t3_M->odeF[0];
  simple_sil_thermal_ctrl_t3_M->intgData.f[1] =
    simple_sil_thermal_ctrl_t3_M->odeF[1];
  simple_sil_thermal_ctrl_t3_M->intgData.f[2] =
    simple_sil_thermal_ctrl_t3_M->odeF[2];
  simple_sil_thermal_ctrl_t3_M->contStates = ((X_simple_sil_thermal_ctrl_t3_T *)
    &simple_sil_thermal_ctrl_t3_X);
  simple_sil_thermal_ctrl_t3_M->contStateDisabled =
    ((XDis_simple_sil_thermal_ctrl__T *) &simple_sil_thermal_ctrl_t3_XDis);
  simple_sil_thermal_ctrl_t3_M->Timing.tStart = (0.0);
  simSolverSetSolverData(&simple_sil_thermal_ctrl_t3_M->solverInfo, (void *)
                    &simple_sil_thermal_ctrl_t3_M->intgData);
  simSolverSetSolverName(&simple_sil_thermal_ctrl_t3_M->solverInfo,"ode3");
  simSetTPtr(simple_sil_thermal_ctrl_t3_M,
             &simple_sil_thermal_ctrl_t3_M->Timing.tArray[0]);
  simSetTFinal(simple_sil_thermal_ctrl_t3_M, 10.0);
  simple_sil_thermal_ctrl_t3_M->Timing.stepSize0 = 0.01;

  /* block I/O */
  (void) memset(((void *) &simple_sil_thermal_ctrl_t3_B), 0,
                sizeof(B_simple_sil_thermal_ctrl_t3_T));

  /* states (continuous) */
  {
    (void) memset((void *)&simple_sil_thermal_ctrl_t3_X, 0,
                  sizeof(X_simple_sil_thermal_ctrl_t3_T));
  }

  /* disabled states */
  {
    (void) memset((void *)&simple_sil_thermal_ctrl_t3_XDis, 0,
                  sizeof(XDis_simple_sil_thermal_ctrl__T));
  }

  /* states (dwork) */
  (void) memset((void *)&simple_sil_thermal_ctrl_t3_DW, 0,
                sizeof(DW_simple_sil_thermal_ctrl_t3_T));

  /* external inputs */
  (void)memset(&simple_sil_thermal_ctrl_t3_U, 0, sizeof
               (ExtU_simple_sil_thermal_ctrl__T));

  /* external outputs */
  (void)memset(&simple_sil_thermal_ctrl_t3_Y, 0, sizeof
               (ExtY_simple_sil_thermal_ctrl__T));

  simple_sil_thermal_ctrl_t3_X.Integrator_CSTATE =
    simple_sil_thermal_ctrl_t3_P.PIDController_InitialConditionF;
  simple_sil_thermal_ctrl_t3_X.Integrator_CSTATE_a =
    simple_sil_thermal_ctrl_t3_P.PIDController_InitialConditio_e;
  simple_sil_thermal_ctrl_t3_X.Integrator_CSTATE_h =
    simple_sil_thermal_ctrl_t3_P.PIDController1_InitialCondition;
}

/* Model terminate function */
void simple_sil_thermal_ctrl_t3_terminate(void)
{
  /* (no terminate code required) */
}


