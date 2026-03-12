#include "psal_config.h"
#include "zenoh-pico.h"
#include "px5_socket.h"
#include "src/psal/zenoh_pico_implementation/inc/zenoh_helper_macro_definition.h"

// parasoft-begin-suppress MISRAC2025-RULE_5_8-a "Variables with the same name in a different module wouldn't cause problem"
// parasoft-begin-suppress MISRAC2025-RULE_5_9-a  "Variable with same name in a different module wouldn't cause problems"
// parasoft-begin-suppress MISRAC2025-RULE_5_9-b  "Variable with same name in a different module wouldn't cause problems"
// parasoft-begin-suppress MISRAC2025-RULE_8_4-a  "These handles are set up as an example"
// parasoft-begin-suppress MISRAC2025-RULE_8_6-a  "Variable with same name in a different module wouldn't cause problems"
// parasoft-begin-suppress MISRAC2025-RULE_8_7-a  "Variable with same name in a different module wouldn't cause problems"
// parasoft-begin-suppress MISRAC2025-RULE_8_9-a  "Declare static variables used for zenoh-pico"
// parasoft-begin-suppress MISRAC2025-RULE_11_2-a  "Pointer to the only element in struct is equivalent to pointer to the struct"

DEFINE_ZENOH_SUBSCRIBHER(thermal_sub_example)
DEFINE_ZENOH_PUBLISHER(thermal_pub_example)

psal_api_t* g_psal_api;
static data_handler_fn_t g_data_handler = NULL;

static void data_handler_examplea(void *data, uint32_t len, void *arg) { /* parasoft-suppress MISRAC2025-RULE_8_13-a "not changing to const before ZED" */
    (void)(arg);
    if (NULL != g_data_handler)
    {
        g_data_handler(data, len);
    }
}

static PsalCallbackContext_t psal_callback_context = {
    .user_call_back = &data_handler_examplea,
    .user_context = NULL
};

// parasoft-end-suppress MISRAC2025-RULE_5_9-b  "Variable with same name in a different module wouldn't cause problems"
// parasoft-end-suppress MISRAC2025-RULE_8_4-a  "These handles are set up as an example"
// parasoft-end-suppress MISRAC2025-RULE_8_6-a  "Variable with same name in a different module wouldn't cause problems"
// parasoft-end-suppress MISRAC2025-RULE_8_7-a  "Variable with same name in a different module wouldn't cause problems"
// parasoft-end-suppress MISRAC2025-RULE_8_9-a  "Declare static variables used for zenoh-pico"
// parasoft-end-suppress MISRAC2025-RULE_11_2-a  "Pointer to the only element in struct is equivalent to pointer to the struct"

Fe56ErrorCode_t thermal_example_module_psal_init(psal_api_t* psal_api_ptr, data_handler_fn_t data_handler)
{
    g_data_handler = data_handler;
    g_psal_api = psal_api_ptr;
    Fe56ErrorCode_t ret = kSuccess;
    INIT_ZENOH_SUBSCRIBER(thermal_sub_example, g_psal_api, "some/topic", &psal_callback_context)
    INIT_ZENOH_PUBLISHER(thermal_pub_example, g_psal_api, "other/topic")
    return ret;
}

// parasoft-end-suppress MISRAC2025-RULE_5_8-a "Variables with the same name in a different module wouldn't cause problem"
// parasoft-end-suppress MISRAC2025-RULE_5_9-a  "Variable with same name in a different module wouldn't cause problems"
