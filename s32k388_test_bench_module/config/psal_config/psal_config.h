#ifndef PSAL_CONFIG_H
#define PSAL_CONFIG_H

#include "src/psal/api/psal_fe56.h"

// parasoft-begin-suppress MISRAC2025-RULE_5_6-a  "Variable with same name in a different module wouldn't cause problems"
typedef void (*data_handler_fn_t)(const uint8_t* data, uint32_t len);
// parasoft-end-suppress MISRAC2025-RULE_5_6-a  "Variable with same name in a different module wouldn't cause problems"

extern psal_api_t* g_psal_api;
extern const PsalPublisherHandle_t thermal_pub_example;

Fe56ErrorCode_t thermal_example_module_psal_init(psal_api_t* psal_api_ptr, data_handler_fn_t data_handler);

#endif /* PSAL_CONFIG_H */