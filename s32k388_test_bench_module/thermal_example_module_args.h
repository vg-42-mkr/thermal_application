#ifndef THERMAL_EXAMPLE_MODULE_ARGS_H
#define THERMAL_EXAMPLE_MODULE_ARGS_H

#include "src/ddal/api/ddal_fe56.h"
#include "src/osal/api/osal_fe56.h"
#include "src/psal/api/psal_fe56.h"

typedef struct {
    DdalGpioSet_FuncPtr_t set_gpio_api;
    psal_api_t* psal_api_ptr;
} thermal_example_module_args_t;

#endif /* THERMAL_EXAMPLE_MODULE_ARGS_H */