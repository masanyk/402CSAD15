#!/bin/bash
# Осцилограми з VCD (після sim/run_sim.sh) -> SVG -> PNG (headless Chrome).
# Запуск: bash sim/render_waves.sh   (з каталогу hdl/)
set -e
cd "$(dirname "$0")/.."
PY="${PY:-/c/Users/maksp/AppData/Local/Programs/Python/Python39/python.exe}"
CHROME="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
T="${TMPDIR:-/tmp}/lab3-wave"            # Chrome пише скріншот в ASCII-шлях
mkdir -p "$T" ../img
for m in 0 1 2 3; do
  "$PY" -I sim/vcd2svg.py sim/out/wave_mode$m.vcd "$T/wave_mode$m.svg" 120 1860 \
    "SPI mode $m (CPOL=$((m>>1)), CPHA=$((m&1))): кадр 0 — Master TX A5 / Slave TX C3"
done
"$PY" -I sim/vcd2svg.py sim/out/wave_mode0.vcd "$T/wave_overview.svg" 0 15300 \
  "SPI mode 0: усі 8 кадрів (A5 3C FF 00 81 5A 01 80) і скидання посеред кадру"
TW="$(cygpath -m "$T")"
for f in wave_mode0 wave_mode1 wave_mode2 wave_mode3 wave_overview; do
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$TW/chrome-prof" \
    --force-device-scale-factor=1.5 --window-size=1220,500 \
    --screenshot="$TW/$f.png" "file:///$TW/$f.svg" > /dev/null 2>&1
done
cp "$T"/*.png "$T"/*.svg ../img/
echo "waveforms -> ../img"
