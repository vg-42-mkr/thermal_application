#ifndef SIMPLE_SIL_THERMAL_CTRL_T4_MATH_H
#define SIMPLE_SIL_THERMAL_CTRL_T4_MATH_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef void *pointer_T;

typedef double real_T;
typedef float real32_T;
typedef double time_T;
typedef bool boolean_T;
typedef char char_T;

typedef int8_t int8_T;
typedef uint8_t uint8_T;
typedef int16_t int16_T;
typedef uint16_t uint16_T;
typedef int32_t int32_T;
typedef uint32_t uint32_T;
typedef int64_t int64_T;
typedef uint64_t uint64_T;

typedef int32_T int_T;
typedef uint32_T uint_T;

typedef unsigned char uchar_T;
typedef unsigned short ushort_T;
typedef unsigned long ulong_T;
typedef unsigned long long ulonglong_T;

typedef uint8_T byte_T;

typedef enum { MINOR_TIME_STEP, MAJOR_TIME_STEP } SimTimeStep;

typedef struct {
  void *rtModelPtr;
  SimTimeStep *simTimeStepPtr;
  void *solverData;
  const char_T *solverName;
  time_T solverStopTime;
  time_T *stepSizePtr;
  real_T **dXPtr;
  time_T **tPtr;
  int_T *numContStatesPtr;
  real_T **contStatesPtr;
  int_T *numPeriodicContStatesPtr;
  int_T **periodicContStateIndicesPtr;
  real_T **periodicContStateRangesPtr;
  boolean_T **contStateDisabledPtr;
  const char_T **errStatusPtr;
  boolean_T isMinorTimeStepWithModeChange;
  boolean_T isContModeFrozen;
} SimSolverInfo;

static inline void simSolverSetRTModelPtr(SimSolverInfo *s, void *rtmp)
{
  s->rtModelPtr = rtmp;
}

static inline void *simSolverGetRTModelPtr(SimSolverInfo *s)
{
  return s->rtModelPtr;
}

static inline void simSolverSetSimTimeStepPtr(SimSolverInfo *s, SimTimeStep *stp)
{
  s->simTimeStepPtr = stp;
}

static inline SimTimeStep *simSolverGetSimTimeStepPtr(SimSolverInfo *s)
{
  return s->simTimeStepPtr;
}

static inline SimTimeStep simSolverGetSimTimeStep(SimSolverInfo *s)
{
  return *(s->simTimeStepPtr);
}

static inline void simSolverSetSimTimeStep(SimSolverInfo *s, SimTimeStep st)
{
  *(s->simTimeStepPtr) = st;
}

static inline void simSolverSetSolverData(SimSolverInfo *s, void *sd)
{
  s->solverData = sd;
}

static inline void *simSolverGetSolverData(SimSolverInfo *s)
{
  return s->solverData;
}

static inline void simSolverSetSolverName(SimSolverInfo *s, const char_T *sn)
{
  s->solverName = sn;
}

static inline const char_T *simSolverGetSolverName(SimSolverInfo *s)
{
  return s->solverName;
}

static inline void simSolverSetSolverStopTime(SimSolverInfo *s, time_T st)
{
  s->solverStopTime = st;
}

static inline time_T simSolverGetSolverStopTime(SimSolverInfo *s)
{
  return s->solverStopTime;
}

static inline void simSolverSetStepSizePtr(SimSolverInfo *s, time_T *ssp)
{
  s->stepSizePtr = ssp;
}

static inline time_T simSolverGetStepSize(SimSolverInfo *s)
{
  return *(s->stepSizePtr);
}

static inline void simSolverSetdXPtr(SimSolverInfo *s, real_T **dxp)
{
  s->dXPtr = dxp;
}

static inline void simSolverSetdX(SimSolverInfo *s, real_T *dx)
{
  *(s->dXPtr) = dx;
}

static inline void simSolverSetTPtr(SimSolverInfo *s, time_T **tp)
{
  s->tPtr = tp;
}

static inline void simSolverSetT(SimSolverInfo *s, time_T t)
{
  (*(s->tPtr))[0] = t;
}

static inline time_T simSolverGetT(SimSolverInfo *s)
{
  return (*(s->tPtr))[0];
}

static inline void simSolverSetContStatesPtr(SimSolverInfo *s, real_T **cp)
{
  s->contStatesPtr = cp;
}

static inline real_T *simSolverGetContStates(SimSolverInfo *s)
{
  return *(s->contStatesPtr);
}

static inline void simSolverSetNumContStatesPtr(SimSolverInfo *s, int_T *cp)
{
  s->numContStatesPtr = cp;
}

static inline void simSolverSetNumPeriodicContStatesPtr(SimSolverInfo *s, int_T *cp)
{
  s->numPeriodicContStatesPtr = cp;
}

static inline void simSolverSetPeriodicContStateIndicesPtr(SimSolverInfo *s, int_T **cp)
{
  s->periodicContStateIndicesPtr = cp;
}

static inline void simSolverSetPeriodicContStateRangesPtr(SimSolverInfo *s, real_T **cp)
{
  s->periodicContStateRangesPtr = cp;
}

static inline void simSolverSetContStateDisabledPtr(SimSolverInfo *s, boolean_T **cdp)
{
  s->contStateDisabledPtr = cdp;
}

static inline void simSolverSetErrorStatusPtr(SimSolverInfo *s, const char_T **esp)
{
  s->errStatusPtr = esp;
}

static inline void simSolverSetIsMinorTimeStepWithModeChange(SimSolverInfo *s,
                                                             boolean_T sn)
{
  s->isMinorTimeStepWithModeChange = sn;
}

static inline void simSolverSetIsContModeFrozen(SimSolverInfo *s, boolean_T val)
{
  s->isContModeFrozen = val;
}

static inline boolean_T simSolverIsModeUpdateTimeStep(SimSolverInfo *s)
{
  return ((simSolverGetSimTimeStep(s) == MAJOR_TIME_STEP ||
           s->isMinorTimeStepWithModeChange) &&
          (!s->isContModeFrozen));
}

extern real_T simInf;
extern real_T simMinusInf;
extern real_T simNaN;
extern real32_T simInfF;
extern real32_T simMinusInfF;
extern real32_T simNaNF;

boolean_T simIsInf(real_T value);
boolean_T simIsInfF(real32_T value);
boolean_T simIsNaN(real_T value);
boolean_T simIsNaNF(real32_T value);

#endif /* SIMPLE_SIL_THERMAL_CTRL_T4_MATH_H */
