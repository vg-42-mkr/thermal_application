#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "simple_thermal_sil_ctrl/simple_sil_thermal_ctrl_t3.h"
#include "src/osal/api/osal_fe56.h"
#include "thermal_example_module_args.h"
#include "s32k388_test_bench_module/config/psal_config/psal_config.h"

#define EXAMPLE_QUEUE_BUFFER_SIZE           (4096U)
#define ITEM_SIZE 256U
#define HDR_SIZE  2U  // uint16 length 
#define MAX_PAYLOAD (ITEM_SIZE - HDR_SIZE) 

uint8_t example_queue_buffer[EXAMPLE_QUEUE_BUFFER_SIZE];
OsalQueueHandle_t example_queue_handle = {
    .item_size = ITEM_SIZE,
    .max_item_count = EXAMPLE_QUEUE_BUFFER_SIZE / ITEM_SIZE,
    .queue_buffer = example_queue_buffer,
    .queue_buffer_size = EXAMPLE_QUEUE_BUFFER_SIZE,
};

extern ExtU_simple_sil_thermal_ctrl__T simple_sil_thermal_ctrl_t3_U;
extern ExtY_simple_sil_thermal_ctrl__T simple_sil_thermal_ctrl_t3_Y;

/**
 * @brief Parse CSV line and extract values
 */
static uint32_T parseCsvLine(const char* const line, double values[], const uint32_T max_values)
{
    uint32_T count = 0U;
    const char* p_line = line;
    char* p_end = NULL;

    if ((line == NULL) || (values == NULL)) {
        return 0U;
    }

    while ((count < max_values) && (*p_line != '\0') && (*p_line != '\n') && (*p_line != '\r')) {
        while ((*p_line == ' ') || (*p_line == '\t')) {
            p_line++;
        }

        if ((*p_line == '\0') || (*p_line == '\n') || (*p_line == '\r')) {
            break;
        }

        values[count] = strtod(p_line, &p_end);
        if (p_end == p_line) {
            break;
        }

        count++;
        p_line = p_end;
        if (*p_line == ',') {
            p_line++;
        }
    }

    return count;
}

/* ===== Subscriber callback ===== */
static void example_data_handler(const uint8_t* data, uint32_t len)
{
    static const uint32_t MAX_LINE_LENGTH = 2048U;
    static const uint32_t NUM_INPUT_VARS = 25U;
    static const double SAMPLE_TIME_S = 0.1;

    static uint32_t step = 0U;
    static char line_buf[2048 + 1U];

    double input_values[NUM_INPUT_VARS];
    uint32_t ncols;

    if ((data == NULL) || (len == 0U)) {
        return;
    }

    if (len > MAX_LINE_LENGTH) {
        len = MAX_LINE_LENGTH;
    }

    memcpy(line_buf, data, len);
    line_buf[len] = '\0';

    ncols = parseCsvLine(line_buf, input_values, NUM_INPUT_VARS);
    if (ncols < NUM_INPUT_VARS) {
        return;
    }

    /* Load model inputs */
    simple_sil_thermal_ctrl_t3_U.env_temp_degC                  = input_values[0];
    simple_sil_thermal_ctrl_t3_U.coolant_rad_out_temp_degC      = input_values[1];
    simple_sil_thermal_ctrl_t3_U.inverter_temp_degC             = input_values[2];
    simple_sil_thermal_ctrl_t3_U.motor_temp_degC                = input_values[3];
    simple_sil_thermal_ctrl_t3_U.coolant_batt_in_temp_degC      = input_values[4];
    simple_sil_thermal_ctrl_t3_U.battery_temp_max_degC          = input_values[5];
    simple_sil_thermal_ctrl_t3_U.battery_temp_min_degC          = input_values[6];
    simple_sil_thermal_ctrl_t3_U.cabin_temp_degC                = input_values[7];
    simple_sil_thermal_ctrl_t3_U.cabin_temp_setpoint_degC       = input_values[8];
    simple_sil_thermal_ctrl_t3_U.hvac_blower_enum               = input_values[9];
    simple_sil_thermal_ctrl_t3_U.defrost_bool                   = input_values[10];
    simple_sil_thermal_ctrl_t3_U.ac_bool                        = input_values[11];
    simple_sil_thermal_ctrl_t3_U.ads_temp_degC                  = input_values[12];
    simple_sil_thermal_ctrl_t3_U.ads_rh_perc                    = input_values[13];
    simple_sil_thermal_ctrl_t3_U.photo_wpm2                     = input_values[14];
    simple_sil_thermal_ctrl_t3_U.vehicle_spd_kph                = input_values[15];
    simple_sil_thermal_ctrl_t3_U.suction_temp_degC              = input_values[16];
    simple_sil_thermal_ctrl_t3_U.suction_press_psig             = input_values[17];
    simple_sil_thermal_ctrl_t3_U.rts_temp_degC                  = input_values[18];
    simple_sil_thermal_ctrl_t3_U.discharge_temp_degC            = input_values[19];
    simple_sil_thermal_ctrl_t3_U.discharge_press_psig           = input_values[20];
    simple_sil_thermal_ctrl_t3_U.xtemp_batt_trgt_temp_degC      = input_values[21];
    simple_sil_thermal_ctrl_t3_U.xtemp_power_comp_cabin_limit_w = input_values[22];
    simple_sil_thermal_ctrl_t3_U.xtem_power_ptc_cabin_limit_w   = input_values[23];
    simple_sil_thermal_ctrl_t3_U.xtem_temp_inv_in_trgt_degC     = input_values[24];

    simple_sil_thermal_ctrl_t3_step();

    double time_sec = (double)step * SAMPLE_TIME_S;
// build the packet
    uint8_t pkt[ITEM_SIZE] = {0};
    
    int n = snprintf((char*)(pkt + HDR_SIZE), MAX_PAYLOAD,
                    "%u,%0.3f,"
                    "%0.6f,%0.6f,%0.6f,%0.6f,%0.6f,%0.6f,%0.6f,%0.6f,%0.6f,"
                    "%0.6f,%0.6f,%0.6f,%0.6f,%0.6f,%0.6f,%0.6f,%0.6f,%0.6f\n",
                    (unsigned)step,
                    time_sec,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_aaf_enum,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_fan_perc,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_batt_ptc_bool,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_motor_pump_perc,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_batt_ewp_perc,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_multi_valve_enum,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_blower_enum,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_cabin_ptc_perc,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_comp_perc,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_batt_exv_perc,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_hp_exv_perc,
                    (double)simple_sil_thermal_ctrl_t3_Y.heat_gen_valve_bool,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_temp_door_l_perc,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_temp_door_r_perc,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_mode_door_l_enum,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_mode_door_r_enum,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_intake_door_bool,
                    (double)simple_sil_thermal_ctrl_t3_Y.cmd_def_door_enum);

    if (n <= 0) return;

    uint16_t len_to_send = (uint16_t)n;
    if (len_to_send >= MAX_PAYLOAD) len_to_send = (uint16_t)(MAX_PAYLOAD - 1U);

    // write length header (little-endian)
    pkt[0] = (uint8_t)(len_to_send & 0xFF);
    pkt[1] = (uint8_t)((len_to_send >> 8) & 0xFF);

    (void)Osal_QueueSend(&example_queue_handle, pkt, ITEM_SIZE);          

    step++;
}

/* ===== Module entry ===== */
void* module_entry(void* argument_area, uint32_t argument_size)
{
    (void)argument_size;

    /* Initialize the model */
    simple_sil_thermal_ctrl_t3_initialize();

    Osal_Module_Init();
    Osal_QueueCreate(&example_queue_handle);
    thermal_example_module_args_t* args = (thermal_example_module_args_t*)argument_area; /* parasoft-suppress MISRAC2025-RULE_11_5-b "Casting is necessary when passing args from base image to module" */
    thermal_example_module_psal_init(args->psal_api_ptr, &example_data_handler); /* parasoft-suppress MISRAC2025-RULE_17_7-a "Not using this for this example for now. Should check in real module code" */
    /* Loop to increment the module entry thread counter.  */
    while (1)
    {
        /****  valid payload bytes only ****/
        uint8_t rx[ITEM_SIZE];
        if (kSuccess == Osal_QueueReceive(&example_queue_handle, rx, ITEM_SIZE, 0xFFFFFFFF)) {
            uint16_t payload_len = (uint16_t)rx[0] | ((uint16_t)rx[1] << 8);

            if (payload_len > MAX_PAYLOAD) payload_len = MAX_PAYLOAD;

            PsalMessage_t pub_data = {
                .payload = (rx + HDR_SIZE),
                .payload_size = payload_len
            };
            g_psal_api->publish(thermal_pub_example, &pub_data);
        }

    }

    return NULL;
}

/* ===== Module exit ===== */
void module_exit(void)
{
    /* no-op */
}
