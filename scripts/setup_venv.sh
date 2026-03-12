#!/bin/bash
# Create a virtual environment and install dependencies for thermal HIL tests.
# Run from repo root: ./scripts/setup_venv.sh

set -e
cd "$(dirname "$0")/.."

VENV_DIR="${VENV_DIR:-.venv}"

echo "Creating virtual environment at $VENV_DIR ..."
python3 -m venv "$VENV_DIR"

echo "Installing dependencies ..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt

echo "Done. Activate with:"
echo "  source $VENV_DIR/bin/activate"
echo "Then run tests, e.g.:"
echo "  python tests/test_thermal_hil_1.py --help"
echo "  python tests/test_thermal_hil_2.py --help"
