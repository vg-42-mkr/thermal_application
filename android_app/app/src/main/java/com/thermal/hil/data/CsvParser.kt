package com.thermal.hil.data

import java.io.InputStream
import java.util.Scanner

private const val EXPECTED_HEADER =
    "dt_s,driver_speed_mps,vehicle_speed_mps,battery_soc,battery_soh,battery_temp_K,battery_current_A,battery_voltage_V,battery_heat_gen_W,battery_heat_rej_W,emotor_torque_Nm,emotor_speed_radps,env_temp_degC,vehicle_spd_kph,coolant_rad_out_temp_degC,coolant_batt_in_temp_degC,inverter_temp_degC"

/**
 * Parses thermal HIL response CSV (same format as thermal_data_base.csv).
 * Skips header row; ignores lines that look like headers (contain letters in value fields).
 */
object CsvParser {

    fun parse(input: InputStream): List<ThermalDataRow> {
        val scanner = Scanner(input).useDelimiter("\\A")
        val content = if (scanner.hasNext()) scanner.next() else ""
        return parse(content)
    }

    fun parse(csvContent: String): List<ThermalDataRow> {
        val lines = csvContent.lines().filter { it.isNotBlank() }
        if (lines.isEmpty()) return emptyList()

        val header = lines[0].trim()
        if (header.equals(EXPECTED_HEADER, ignoreCase = true).not()) {
            // Still try to parse if column count matches
        }

        val result = mutableListOf<ThermalDataRow>()
        for (i in 1 until lines.size) {
            val line = lines[i].trim()
            if (line.isEmpty()) continue
            val row = parseRow(line) ?: continue
            result.add(row)
        }
        return result
    }

    private fun parseRow(line: String): ThermalDataRow? {
        val parts = line.split(",").map { it.trim() }
        if (parts.size < 17) return null
        return try {
            ThermalDataRow(
                dt_s = parts[0].toDouble(),
                driver_speed_mps = parts[1].toDouble(),
                vehicle_speed_mps = parts[2].toDouble(),
                battery_soc = parts[3].toDouble(),
                battery_soh = parts[4].toDouble(),
                battery_temp_K = parts[5].toDouble(),
                battery_current_A = parts[6].toDouble(),
                battery_voltage_V = parts[7].toDouble(),
                battery_heat_gen_W = parts[8].toDouble(),
                battery_heat_rej_W = parts[9].toDouble(),
                emotor_torque_Nm = parts[10].toDouble(),
                emotor_speed_radps = parts[11].toDouble(),
                env_temp_degC = parts[12].toDouble(),
                vehicle_spd_kph = parts[13].toDouble(),
                coolant_rad_out_temp_degC = parts[14].toDouble(),
                coolant_batt_in_temp_degC = parts[15].toDouble(),
                inverter_temp_degC = parts[16].toDouble(),
            )
        } catch (_: NumberFormatException) {
            null
        }
    }
}
