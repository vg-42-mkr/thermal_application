package com.thermal.hil.ev

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.BatteryChargingFull
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.thermal.hil.ui.ThermalGreenDark

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EvLiveUiScreen(
    evDataProvider: EvDataProvider,
    modifier: Modifier = Modifier,
) {
    val data by evDataProvider.liveData.collectAsStateWithLifecycle(initialValue = EvLiveData(0f, 0f, 0f, EvChargeState.UNKNOWN, false, 0f, false, 0f, false, EvDataSource.MOCK))

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("EV Navigation & Energy", fontWeight = FontWeight.SemiBold) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = ThermalGreenDark,
                    titleContentColor = Color.White,
                ),
            )
        },
        modifier = modifier.fillMaxSize(),
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                "Live parameters (VHAL / mock)",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            EvMetricCard(title = "Battery level (SoC)", value = "%.1f%%".format(data.socPercent), Icons.Default.BatteryChargingFull)
            EvMetricCard(title = "Battery capacity", value = "%.0f Wh".format(data.batteryCapacityWh), Icons.Default.BatteryChargingFull)
            EvMetricCard(title = "Charge rate", value = "%.0f mW".format(data.instantaneousChargeRateMw), Icons.Default.BatteryChargingFull)
            EvMetricCard(title = "Charge state", value = data.chargeState.name, Icons.Default.BatteryChargingFull)
            EvMetricCard(title = "Charge port", value = if (data.chargePortConnected) "Connected" else "Disconnected", Icons.Default.BatteryChargingFull)
            EvMetricCard(title = "Battery temperature", value = "%.1f °C".format(data.batteryTemperatureCelsius), Icons.Default.Thermostat)
            EvMetricCard(title = "Regen braking", value = if (data.regenerativeBrakingActive) "Active" else "Inactive", Icons.Default.DirectionsCar)
            EvMetricCard(title = "Vehicle speed", value = "%.1f m/s".format(data.vehicleSpeedMps), Icons.Default.DirectionsCar)
            EvMetricCard(title = "HVAC power", value = if (data.hvacPowerOn) "On" else "Off", Icons.Default.Thermostat)

            Spacer(modifier = Modifier.height(8.dp))
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Range estimate", style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.onPrimaryContainer)
                    Text("%.1f km".format(data.rangeEstimateKm), style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onPrimaryContainer)
                }
            }

            Spacer(modifier = Modifier.height(8.dp))
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Range-aware routing", style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("Send current_soc to routing engine → route with charging_stations as waypoints (ComputeRoutes, travelMode: DRIVE, routingPreference: FUEL_EFFICIENT).", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }

            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Thermal / preconditioning", style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.onTertiaryContainer)
                    Text("If next waypoint is a charger and distance < 20 km, call vendor property to start battery preconditioning.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onTertiaryContainer)
                }
            }

            Text("Data source: %s".format(data.source.name), style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.outline)
        }
    }
}

@Composable
private fun EvMetricCard(
    title: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(icon, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
            Spacer(modifier = Modifier.padding(8.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Text(value, style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Medium, color = MaterialTheme.colorScheme.onSurface)
            }
        }
    }
}
