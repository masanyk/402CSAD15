#!/bin/bash
# Симуляція тестбенча tb_spi у GHDL для всіх 4 режимів SPI.
# GHDL не підтримує не-ASCII символи у шляху робочої бібліотеки, тому
# компіляція виконується в тимчасовому ASCII-каталозі, результати копіюються назад.
# Запуск: bash sim/run_sim.sh   (з каталогу hdl/)
set -e
cd "$(dirname "$0")/.."
GHDL="${GHDL:-/c/Users/maksp/tools/ghdl/bin/ghdl.exe}"
W="${TMPDIR:-/tmp}/lab3-sim"
rm -rf "$W" && mkdir -p "$W"
cp src/*.vhd tb/*.vhd "$W/"
mkdir -p sim/out
cd "$W"
SRC="spi_master_tx.vhd spi_master_rx.vhd spi_master.vhd spi_slave.vhd tb_spi.vhd"
"$GHDL" -a --std=08 $SRC
"$GHDL" -e --std=08 tb_spi
status=0
for mode in 0 1 2 3; do
  cpol=$((mode >> 1)); cpha=$((mode & 1))
  echo "----- mode $mode (CPOL=$cpol, CPHA=$cpha)"
  if ! "$GHDL" -r --std=08 tb_spi -gCPOL="'$cpol'" -gCPHA="'$cpha'" --vcd=wave_mode$mode.vcd > sim_mode$mode.log 2>&1; then
    status=1
  fi
  sed 's/^.*(report note): //' sim_mode$mode.log | grep -vE "^\s*$" | sed 's/^/  /'
done
cd - > /dev/null
cp "$W"/*.vcd "$W"/*.log sim/out/
exit $status
