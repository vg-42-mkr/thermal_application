package com.thermal.hil.ev

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.thermal.hil.ui.ThermalHilTheme

/**
 * EV Navigation Live UI: energy utilization, range estimation, and navigation/thermal hints.
 *
 * Initialization flow (when Car API is available):
 * 1. Car.createCar(context)
 * 2. CarPropertyManager.getProperty(INFO_EV_BATTERY_CAPACITY)
 * 3. CarPropertyManager.registerCallback(..., EV_BATTERY_LEVEL, PERF_VEHICLE_SPEED, ...)
 *
 * This activity uses MockEvDataProvider for testing without DUT. On Android Automotive,
 * replace with CarEvDataProvider backed by CarPropertyManager.
 */
class EvNavigationActivity : ComponentActivity() {

    private lateinit var evDataProvider: EvDataProvider

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        evDataProvider = MockEvDataProvider(applicationContext)

        setContent {
            ThermalHilTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    EvLiveUiScreen(evDataProvider = evDataProvider)
                }
            }
        }
    }

    override fun onDestroy() {
        if (::evDataProvider.isInitialized) evDataProvider.release()
        super.onDestroy()
    }
}
