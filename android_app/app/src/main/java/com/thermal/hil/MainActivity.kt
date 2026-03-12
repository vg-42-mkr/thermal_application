package com.thermal.hil

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.thermal.hil.ui.DcfcChartWebViewScreen
import com.thermal.hil.ui.ThermalHilTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ThermalHilTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    DcfcChartWebViewScreen()
                }
            }
        }
    }
}
