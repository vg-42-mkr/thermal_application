#!/bin/bash
nohup python3 tests/thermal_hil_live_ui_dcfc_chart_bt_cycle.py --web &
sleep 1
nohup python3 tests/test_thermal_hil_2.py --hz 100 --csv tests/csv_data/hil_dcfc_output_2.csv &
sleep 1
nohup python3 tests/zenoh_echo.py &
