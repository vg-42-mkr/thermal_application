package com.thermal.hil.ev

/**
 * EV live data model for navigation, energy utilization, and range estimation.
 * Maps to VHAL properties (VehiclePropertyIds) when Car API is available.
 */
data class EvLiveData(
    val batteryLevelWhOrPercent: Float,
    val batteryCapacityWh: Float,
    val instantaneousChargeRateMw: Float,
    val chargeState: EvChargeState,
    val chargePortConnected: Boolean,
    val batteryTemperatureCelsius: Float,
    val regenerativeBrakingActive: Boolean,
    val vehicleSpeedMps: Float,
    val hvacPowerOn: Boolean,
    val source: EvDataSource = EvDataSource.MOCK,
) {
    val socPercent: Float
        get() = if (batteryCapacityWh > 0f) (batteryLevelWhOrPercent / batteryCapacityWh * 100f).coerceIn(0f, 100f)
        else batteryLevelWhOrPercent.coerceIn(0f, 100f)

    val rangeEstimateKm: Float
        get() {
            if (batteryCapacityWh <= 0f) return 0f
            val usableWh = batteryLevelWhOrPercent.coerceIn(0f, batteryCapacityWh)
            val whPerKm = 180f
            return usableWh / whPerKm
        }
}

enum class EvChargeState { UNKNOWN, CHARGING, DISCHARGING, FULL }

enum class EvDataSource { MOCK, VHAL }
