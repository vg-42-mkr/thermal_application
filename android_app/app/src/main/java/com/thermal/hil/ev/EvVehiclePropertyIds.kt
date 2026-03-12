package com.thermal.hil.ev

/**
 * VHAL property IDs for EV (align with android.car.VehiclePropertyIds as of 2026.1).
 * Use with CarPropertyManager.getProperty() / registerCallback() when Car API is available.
 * On Android Automotive, prefer linking against platform VehiclePropertyIds directly.
 */
object EvVehiclePropertyIds {
    const val EV_BATTERY_LEVEL = 0x11610307
    const val INFO_EV_BATTERY_CAPACITY = 0x11610304
    const val EV_BATTERY_INSTANTANEOUS_CHARGE_RATE = 0x11610306
    const val EV_CHARGE_STATE = 0x11610302
    const val EV_CHARGE_PORT_CONNECTED = 0x11610301
    const val EV_BATTERY_AVERAGE_TEMPERATURE = 0x11610305
    const val EV_REGENERATIVE_BRAKING_STATE = 0x11610308
    const val PERF_VEHICLE_SPEED = 0x11600207
    const val HVAC_POWER_ON = 0x11400401
}
