#!/bin/bash
# Setup venv and launch End-to-End without DUT in 3 terminal tabs.
#
# Tab 1: Zenoh router (zenohd)
# Tab 2: Zenoh echo (in-topic → out-topic)
# Tab 3: CSV publisher (test_thermal_hil_1) in background + Live UI (thermal_hil_live_ui_dcfc_chart_bt --web)
#
# Prerequisites: zenohd on PATH (Eclipse Zenoh router). Install from:
#   https://github.com/eclipse-zenoh/zenoh/releases
#
# Run from repo root: ./scripts/run_e2e_no_dut.sh
# Kill all E2E processes: ./scripts/run_e2e_no_dut.sh kill

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# --- Kill mode: stop all Python scripts and zenohd started by this E2E run ---
if [ "${1:-}" = "kill" ] || [ "${1:-}" = "--kill" ] || [ "${1:-}" = "stop" ]; then
  echo "=== Killing E2E processes ==="
  KILLED=0
  for pattern in "zenoh_echo.py" "test_thermal_hil_1.py" "test_thermal_hil_2.py" "thermal_hil_live_ui_dcfc_chart_bt.py" "thermal_hil_live_ui_dcfc_chart_bt_cycle.py"; do
    if pkill -f "$pattern" 2>/dev/null; then
      echo "  killed: $pattern"
      KILLED=1
    fi
  done
  if pkill -f "zenohd" 2>/dev/null; then
    echo "  killed: zenohd"
    KILLED=1
  fi
  if [ "$KILLED" = 0 ]; then
    echo "  No matching processes found."
  else
    echo "Done."
  fi
  exit 0
fi

VENV_DIR="${VENV_DIR:-.venv}"
ENDPOINT="${ENDPOINT:-tcp/127.0.0.1:1234}"
IN_TOPIC="${IN_TOPIC:-some/topic}"
OUT_TOPIC="${OUT_TOPIC:-other/topic}"

echo "=== Setup venv at $REPO_ROOT/$VENV_DIR ==="
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install --upgrade pip
  "$VENV_DIR/bin/pip" install -r requirements.txt
  echo "Venv created and dependencies installed."
else
  echo "Venv exists. (Delete $VENV_DIR to recreate.)"
fi

ACTIVATE="source $REPO_ROOT/$VENV_DIR/bin/activate"
PY="$REPO_ROOT/$VENV_DIR/bin/python"
TESTS="$REPO_ROOT/tests"

#CMD1="cd $REPO_ROOT && $ACTIVATE && $PY $TESTS/zenoh_echo.py --endpoint $ENDPOINT --in-topic $IN_TOPIC --out-topic $OUT_TOPIC"
#CMD2="cd $REPO_ROOT && $ACTIVATE && ($PY $TESTS/test_thermal_hil_2.py --hz 100 --duration 84000 --endpoint $ENDPOINT --in-topic $IN_TOPIC --out-topic $OUT_TOPIC &) && sleep 2 && $PY $TESTS/tthermal_hil_live_ui_dcfc_chart_bt.py --web --endpoint $ENDPOINT --out-topic $OUT_TOPIC"
#CMD3="cd $REPO_ROOT && $ACTIVATE && ($PY $TESTS/test_thermal_hil_1.py --duration 3600 --endpoint $ENDPOINT --in-topic $IN_TOPIC --out-topic $OUT_TOPIC &) && sleep 2 && $PY $TESTS/thermal_hil_live_ui_dcfc_chart_bt.py --web --endpoint $ENDPOINT --out-topic $OUT_TOPIC"

#CMD3="python3 tests/test_thermal_hil_2.py --hz 100 --duration 86,400 --csv tests/csv_data/hil_dcfc_output_2.csv"
#CMD4="python3 tests/thermal_hil_live_ui_dcfc_chart_bt.py --web --out-topic other/topic --endpoint tcp/192.168.1.10:1234"

#CMD1="zenohd --listen tcp/0.0.0.0:1234"
CMD1="cd $REPO_ROOT && $ACTIVATE && $PY $TESTS/zenoh_echo.py"
CMD2="cd $REPO_ROOT && $ACTIVATE && ($PY $TESTS/test_thermal_hil_2.py --hz 100 --duration 86400 --endpoint $ENDPOINT --in-topic $IN_TOPIC --out-topic $OUT_TOPIC)"
CMD3="cd $REPO_ROOT && $ACTIVATE && ($PY $TESTS/thermal_hil_live_ui_dcfc_chart_bt.py --web --endpoint $ENDPOINT --out-topic $OUT_TOPIC --port 8082)"


# CMD1="zenohd --listen tcp/0.0.0.0:1234"
# CMD2="cd $REPO_ROOT && $ACTIVATE && $PY $TESTS/zenoh_echo.py --endpoint $ENDPOINT --in-topic $IN_TOPIC --out-topic $OUT_TOPIC"
# CMD3="cd $REPO_ROOT && $ACTIVATE && ($PY $TESTS/test_thermal_hil_1.py --duration 3600 --endpoint $ENDPOINT --in-topic $IN_TOPIC --out-topic $OUT_TOPIC &) && sleep 2 && $PY $TESTS/thermal_hil_live_ui_dcfc_chart_bt.py --web --endpoint $ENDPOINT --out-topic $OUT_TOPIC"


if [[ "$OSTYPE" == darwin* ]]; then
  echo "=== Opening 3 Terminal tabs (macOS) ==="
  # Escape double quotes and backslashes for AppleScript
  C1="${CMD1//\"/\\\"}"
  C2="${CMD2//\"/\\\"}"
  C3="${CMD3//\"/\\\"}"
  osascript <<EOF
tell application "Terminal" to activate
tell application "Terminal" to do script "echo 'Tab 1: Zenoh router'; $C1"
delay 0.8
tell application "System Events" to keystroke "t" using command down
delay 0.5
tell application "Terminal" to do script "echo 'Tab 2: Zenoh echo'; $C2" in front window
delay 0.8
tell application "System Events" to keystroke "t" using command down
delay 0.5
tell application "Terminal" to do script "echo 'Tab 3: Publisher + Live UI'; $C3" in front window
EOF
  echo "Done. Tab 1: zenohd, Tab 2: echo, Tab 3: publisher + Live UI (browser will open)."
elif command -v gnome-terminal &>/dev/null; then
  echo "=== Opening 3 gnome-terminal tabs ==="
  gnome-terminal --tab --title="zenohd" -- bash -c "echo 'Tab 1: Zenoh router'; $CMD1; exec bash"
  gnome-terminal --tab --title="echo" -- bash -c "echo 'Tab 2: Zenoh echo'; $CMD2; exec bash"
  gnome-terminal --tab --title="Publisher+UI" -- bash -c "echo 'Tab 3: Publisher + Live UI'; $CMD3; exec bash"
  echo "Done. Close the terminal window when finished."
else
  echo "=== Run these in 3 separate terminal tabs ==="
  echo ""
  echo "Tab 1 (Zenoh router):"
  echo "  $CMD1"
  echo ""
  echo "Tab 2 (Zenoh echo):"
  echo "  $CMD2"
  echo ""
  echo "Tab 3 (Publisher + Live UI):"
  echo "  $CMD3"
  echo ""
  echo "Start Tab 1 first, then Tab 2, then Tab 3. Browser will open for the Live UI."
fi
