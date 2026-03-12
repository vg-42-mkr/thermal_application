package com.thermal.hil.ev

import android.content.Context
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Provides EV data from VHAL (CarPropertyManager) or mock for testing.
 * Implementation flow: Car.createCar(context) -> CarPropertyManager -> getProperty / registerCallback
 * with EvVehiclePropertyIds.
 */
interface EvDataProvider {
    val liveData: Flow<EvLiveData>
    fun release()
}

/**
 * Mock provider for testing without DUT / automotive device.
 * Simulates SoC, speed, and other parameters.
 */
class MockEvDataProvider(private val context: Context) : EvDataProvider {
    private val _liveData = MutableStateFlow(
        EvLiveData(
            batteryLevelWhOrPercent = 65f,
            batteryCapacityWh = 75_000f,
            instantaneousChargeRateMw = 0f,
            chargeState = EvChargeState.DISCHARGING,
            chargePortConnected = false,
            batteryTemperatureCelsius = 24f,
            regenerativeBrakingActive = false,
            vehicleSpeedMps = 0f,
            hvacPowerOn = false,
            source = EvDataSource.MOCK,
        )
    )
    override val liveData = _liveData.asStateFlow()

    fun update(block: EvLiveData.() -> EvLiveData) {
        _liveData.value = _liveData.value.block()
    }

    override fun release() {}
}

/**
 * VHAL-backed provider. Initialize with Car.createCar(context), then
 * CarPropertyManager.getProperty(INFO_EV_BATTERY_CAPACITY) and
 * registerCallback for EV_BATTERY_LEVEL, PERF_VEHICLE_SPEED, etc.
 * Use when running on Android Automotive with car service.
 */
class CarEvDataProvider(
    private val context: Context,
    private val propertyManager: Any?, // CarPropertyManager when Car API available
) : EvDataProvider {
    private val _liveData = MutableStateFlow(
        EvLiveData(
            batteryLevelWhOrPercent = 0f,
            batteryCapacityWh = 0f,
            instantaneousChargeRateMw = 0f,
            chargeState = EvChargeState.UNKNOWN,
            chargePortConnected = false,
            batteryTemperatureCelsius = 0f,
            regenerativeBrakingActive = false,
            vehicleSpeedMps = 0f,
            hvacPowerOn = false,
            source = EvDataSource.VHAL,
        )
    )
    override val liveData = _liveData.asStateFlow()

    override fun release() {
        // Unregister callbacks, disconnect Car
    }
}
