package com.thermal.hil.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val ThermalGreen = Color(0xFF1B5E20)
val ThermalGreenLight = Color(0xFF4CAF50)
val ThermalGreenDark = Color(0xFF0D3D10)
val SurfaceVariant = Color(0xFFE8F5E9)
val ErrorRed = Color(0xFFB00020)
val OnSurfaceVariant = Color(0xFF1B5E20)

@Composable
fun ThermalHilTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = MaterialTheme.colorScheme.copy(
            primary = ThermalGreen,
            primaryContainer = ThermalGreenLight,
            onPrimary = Color.White,
            surface = Color(0xFFFAFAFA),
        ),
        content = content,
    )
}
