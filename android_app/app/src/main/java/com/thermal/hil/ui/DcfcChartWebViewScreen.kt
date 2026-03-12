package com.thermal.hil.ui

import android.annotation.SuppressLint
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
// Title bar – kept for future use
// import androidx.compose.material3.TopAppBar
// import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView

// private const val DEFAULT_DCFC_URL = "http://192.168.1.10:5000" // DEFAULT_DCFC_URL
//private const val DEFAULT_DCFC_URL = "http://172.29.37.14:5000/" // Wifis
private const val DEFAULT_DCFC_URL = "http://172.27.151.190:8082/" // guest Wifis

// Match HIL web UI background so the area above vehicle bar is not a visible white strip
private val DcfcScreenBackground = Color(0xFF1a1a2e)
@SuppressLint("SetJavaScriptEnabled")
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DcfcChartWebViewScreen(
    modifier: Modifier = Modifier,
) {
    var url by remember { mutableStateOf(DEFAULT_DCFC_URL) }
    var loadUrl by remember { mutableStateOf(DEFAULT_DCFC_URL) }
    var showUrlBar by remember { mutableStateOf(false) }

    // Title bar – uncomment to restore
    // Scaffold(
    //     topBar = {
    //         TopAppBar(
    //             title = { Text("HIL DCFC Chart") },
    //             colors = TopAppBarDefaults.topAppBarColors(
    //                 containerColor = ThermalGreenDark,
    //                 titleContentColor = androidx.compose.ui.graphics.Color.White,
    //             ),
    //         )
    //     },
    // ) { padding ->
    Scaffold(
        modifier = modifier.fillMaxSize(),
        containerColor = DcfcScreenBackground,
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize()) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .statusBarsPadding()
                    .navigationBarsPadding(),
            ) {
                if (showUrlBar) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        OutlinedTextField(
                            value = url,
                            onValueChange = { url = it },
                            label = { Text("Server URL") },
                            modifier = Modifier.weight(1f),
                            singleLine = true,
                        )
                        Button(
                            onClick = {
                                val target = url.trim()
                                if (target.isNotEmpty()) {
                                    loadUrl = if (target.startsWith("http://") || target.startsWith("https://")) target
                                    else "http://$target"
                                }
                            },
                            modifier = Modifier.padding(start = 8.dp),
                        ) {
                            Text("Go")
                        }
                    }
                }
                Box(modifier = Modifier.fillMaxSize()) {
                    key(loadUrl) {
                        AndroidView(
                            factory = { context ->
                                WebView(context).apply {
                                    settings.javaScriptEnabled = true
                                    settings.domStorageEnabled = true
                                    webViewClient = WebViewClient()
                                    webChromeClient = WebChromeClient()
                                    loadUrl(loadUrl)
                                }
                            },
                            modifier = Modifier.fillMaxSize(),
                        )
                    }
                }
            }
            FloatingActionButton(
                onClick = { showUrlBar = !showUrlBar },
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(top = 8.dp, end = 8.dp),
                containerColor = ThermalGreenDark,
                contentColor = androidx.compose.ui.graphics.Color.White,
            ) {
                Icon(Icons.Default.Settings, contentDescription = "Show server URL")
            }
        }
    }
}
