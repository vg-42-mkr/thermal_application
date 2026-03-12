package com.thermal.hil.data

/**
 * One row of thermal HIL response CSV data.
 * Matches columns from thermal_data_base.csv / thermal_example_module_out.csv.
 */
data class ThermalDataRow(
    val dt_s: Double,
    val driver_speed_mps: Double,
    val vehicle_speed_mps: Double,
    val battery_soc: Double,
    val battery_soh: Double,
    val battery_temp_K: Double,
    val battery_current_A: Double,
    val battery_voltage_V: Double,
    val battery_heat_gen_W: Double,
    val battery_heat_rej_W: Double,
    val emotor_torque_Nm: Double,
    val emotor_speed_radps: Double,
    val env_temp_degC: Double,
    val vehicle_spd_kph: Double,
    val coolant_rad_out_temp_degC: Double,
    val coolant_batt_in_temp_degC: Double,
    val inverter_temp_degC: Double,
) {
    val battery_temp_degC: Double get() = battery_temp_K - 273.15
}
