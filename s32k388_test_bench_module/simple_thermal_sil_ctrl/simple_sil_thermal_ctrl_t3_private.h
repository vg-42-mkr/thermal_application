/*
 * simple_sil_thermal_ctrl_t3_private.h
 *
 * Internal declarations for the thermal controller model.
 */

#ifndef simple_sil_thermal_ctrl_t3_private_h_
#define simple_sil_thermal_ctrl_t3_private_h_
#include "simple_sil_thermal_ctrl_t4_math.h"
#include "builtin_typeid_types.h"
#include "multiword_types.h"
#include "simple_sil_thermal_ctrl_t3_types.h"
#include "simple_sil_thermal_ctrl_t3.h"

/* Private macros used by the generated code to access rtModel */
#ifndef simIsMajorTimeStep
#define simIsMajorTimeStep(rtm)        (((rtm)->Timing.simTimeStep) == MAJOR_TIME_STEP)
#endif

#ifndef simIsMinorTimeStep
#define simIsMinorTimeStep(rtm)        (((rtm)->Timing.simTimeStep) == MINOR_TIME_STEP)
#endif

#ifndef simSetTFinal
#define simSetTFinal(rtm, val)         ((rtm)->Timing.tFinal = (val))
#endif

#ifndef simSetTPtr
#define simSetTPtr(rtm, val)           ((rtm)->Timing.t = (val))
#endif

extern real_T look1_plinlxpw(real_T u0, const real_T bp0[], const real_T table[],
  uint32_T prevIndex[], uint32_T maxIndex);

/* private model entry point functions */
extern void simple_sil_thermal_ctrl_t3_derivatives(void);

#endif                               /* simple_sil_thermal_ctrl_t3_private_h_ */



