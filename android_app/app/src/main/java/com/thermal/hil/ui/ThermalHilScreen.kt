package com.thermal.hil.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.BatteryChargingFull
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material.icons.filled.WaterDrop
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.thermal.hil.data.ThermalDataRow

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ThermalHilScreen(
    rows: List<ThermalDataRow>,
    modifier: Modifier = Modifier,
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Thermal HIL 1 Response", fontWeight = FontWeight.SemiBold) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = ThermalGreenDark,
                    titleContentColor = androidx.compose.ui.graphics.Color.White,
                ),
            )
        },
        modifier = modifier.fillMaxSize(),
    ) { padding ->
        if (rows.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(24.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    "No data loaded. Add thermal_example_module_out.csv to assets.",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            return@Scaffold
        }

        val latest = rows.last()
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            item {
                Text(
                    "Live metrics (latest sample)",
                    style = MaterialTheme.typography.titleMedium,
                    color = ThermalGreenDark,
                    fontWeight = FontWeight.SemiBold,
                )
            }
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    MetricCard(
                        title = "Battery SOC",
                        value = "${(latest.battery_soc * 100).toInt()}%",
                        icon = Icons.Default.BatteryChargingFull,
                        modifier = Modifier.weight(1f),
                    )
                    MetricCard(
                        title = "Vehicle speed",
                        value = "${latest.vehicle_spd_kph.toInt()} kph",
                        icon = Icons.Default.Speed,
                        modifier = Modifier.weight(1f),
                    )
                }
            }
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    MetricCard(
                        title = "Battery temp",
                        value = String.format("%.1f °C", latest.battery_temp_degC),
                        icon = Icons.Default.Thermostat,
                        modifier = Modifier.weight(1f),
                    )
                    MetricCard(
                        title = "Coolant out",
                        value = String.format("%.1f °C", latest.coolant_rad_out_temp_degC),
                        icon = Icons.Default.WaterDrop,
                        modifier = Modifier.weight(1f),
                    )
                }
            }
            item {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    "Time series (${rows.size} rows)",
                    style = MaterialTheme.typography.titleMedium,
                    color = ThermalGreenDark,
                    fontWeight = FontWeight.SemiBold,
                )
            }
            itemsIndexed(rows) { index, row ->
                RowCard(index = index, row = row)
            }
        }
    }
}

@Composable
private fun MetricCard(
    title: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceVariant),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = ThermalGreen,
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                title,
                style = MaterialTheme.typography.labelMedium,
                color = OnSurfaceVariant,
            )
            Text(
                value,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = ThermalGreenDark,
            )
        }
    }
}

@Composable
private fun RowCard(
    index: Int,
    row: ThermalDataRow,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(8.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    "t = ${row.dt_s}s",
                    style = MaterialTheme.typography.labelLarge,
                    color = ThermalGreen,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    "row ${index + 1}",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Spacer(modifier = Modifier.height(6.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text("SOC ${(row.battery_soc * 100).toInt()}%", style = MaterialTheme.typography.bodySmall)
                Text("${row.vehicle_spd_kph.toInt()} kph", style = MaterialTheme.typography.bodySmall)
                Text("${String.format("%.1f", row.battery_temp_degC)} °C", style = MaterialTheme.typography.bodySmall)
                Text("${String.format("%.1f", row.coolant_rad_out_temp_degC)} °C", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
