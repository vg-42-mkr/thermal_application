#include "simple_sil_thermal_ctrl_t4_math.h"

#include <math.h>

real_T simNaN = -(real_T)NAN;
real_T simInf = (real_T)INFINITY;
real_T simMinusInf = -(real_T)INFINITY;
real32_T simNaNF = -(real32_T)NAN;
real32_T simInfF = (real32_T)INFINITY;
real32_T simMinusInfF = -(real32_T)INFINITY;

boolean_T simIsInf(real_T value)
{
  return (boolean_T)isinf(value);
}

boolean_T simIsInfF(real32_T value)
{
  return (boolean_T)isinf(value);
}

boolean_T simIsNaN(real_T value)
{
  return (boolean_T)(isnan(value) != 0);
}

boolean_T simIsNaNF(real32_T value)
{
  return (boolean_T)(isnan(value) != 0);
}
