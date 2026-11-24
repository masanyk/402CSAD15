# ЛР3 АПКС — SPI Master на VHDL

**Студент:** Процак Максим Степанович, КІ-402, варіант 15 — **SPI, VHDL**
**Інструменти:** GHDL 6.0 (симуляція, VHDL-2008), Yosys + nextpnr (синтез, Lattice iCE40)

## Структура

| Шлях | Вміст |
|------|-------|
| `hdl/src/spi_master_tx.vhd` | передавач: FSM, дільник частоти, SCLK/SS_N/MOSI |
| `hdl/src/spi_master_rx.vhd` | приймач: зсувний регістр MISO |
| `hdl/src/spi_master.vhd` | верхній модуль Master (Tx + Rx) |
| `hdl/src/spi_slave.vhd` | SPI Slave — «інший пристрій» для перевірки Rx |
| `hdl/tb/tb_spi.vhd` | тестбенч: CLK/RESET, тестові вектори, монітор шини, перевірки |
| `hdl/sim/run_sim.sh` | симуляція в GHDL для режимів 0–3 |
| `hdl/sim/render_waves.sh`, `vcd2svg.py` | осцилограми VCD → SVG/PNG |
| `hdl/sim/out/` | логи симуляції |
| `img/` | осцилограми |

## Параметри

- Розрядність 8 біт, MSB first, повний дуплекс.
- Режими SPI 0–3 через generic `CPOL`/`CPHA`.
- `f_sclk = f_clk / (2·CLK_DIV)`; у тестбенчі 50 МГц / 8 = 6.25 МГц.

## Запуск

```bash
cd hdl
bash sim/run_sim.sh       # симуляція 4 режимів, очікується "RESULT: PASS"
bash sim/render_waves.sh  # осцилограми в ../img
```

GHDL не підтримує кирилицю у шляху робочої бібліотеки, тому `run_sim.sh`
компілює в тимчасовому ASCII-каталозі.

## Результат симуляції

| Режим | CPOL | CPHA | Кадрів | Результат |
|-------|------|------|--------|-----------|
| 0 | 0 | 0 | 8 | PASS |
| 1 | 0 | 1 | 8 | PASS |
| 2 | 1 | 0 | 8 | PASS |
| 3 | 1 | 1 | 8 | PASS |
