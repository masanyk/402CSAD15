#!/bin/bash
# Повний ланцюжок ЛР2: GUID -> бібліотека/схема -> ERC -> плата -> трасування -> DRC -> Gerber -> зображення.
# Запуск (Git Bash): bash scripts/build.sh
set -e
cd "$(dirname "$0")/.."
KICAD="${KICAD:-/c/Users/maksp/AppData/Local/Programs/KiCad/10.0/bin}"
FREEROUTING="${FREEROUTING:-/c/Users/maksp/tools/freerouting/freerouting-2.1.0.jar}"
PY="$KICAD/python.exe"; CLI="$KICAD/kicad-cli.exe"
WORK="${TMPDIR:-/tmp}/lab2-route"   # Freerouting працює в ASCII-шляху

echo "== 1. GUID і таблиця з'єднань"
"$PY" scripts/design.py kicad/netlist.json

echo "== 2. Бібліотека і схема"
"$PY" scripts/gen_lib_sch.py
(cd kicad && "$CLI" sch erc --severity-all --exit-code-violations -o erc.rpt lab2.kicad_sch)
(cd kicad && "$CLI" sch export netlist --format kicadsexpr -o sch.net lab2.kicad_sch >/dev/null)

echo "== 3. Плата + DSN"
"$PY" scripts/gen_pcb.py

echo "== 4. Автотрасування (Freerouting)"
mkdir -p "$WORK" && cp kicad/lab2.dsn "$WORK/" && rm -f "$WORK/lab2.ses"
(cd "$WORK" && java -jar "$FREEROUTING" -de lab2.dsn -do lab2.ses -mp 50 --gui.enabled=false > route.log 2>&1)
cp "$WORK/lab2.ses" kicad/ && cp "$WORK/route.log" kicad/freerouting.log
"$PY" scripts/gen_pcb.py import

echo "== 5. DRC (з перевіркою відповідності схемі)"
(cd kicad && "$CLI" pcb drc --schematic-parity --severity-all --exit-code-violations -o drc.rpt lab2.kicad_pcb)

echo "== 6. Gerber RS-274X + свердління"
rm -rf gerber && mkdir gerber
(cd kicad && "$CLI" pcb export gerbers --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts -o ../gerber/ lab2.kicad_pcb >/dev/null)
(cd kicad && "$CLI" pcb export drill --format excellon -o ../gerber/ lab2.kicad_pcb >/dev/null)
rm -f lab2_gerber.zip && (cd gerber && powershell -NoProfile -Command "Compress-Archive -Force -Path * -DestinationPath ..\\lab2_gerber.zip")

echo "== 7. Зображення для звіту"
mkdir -p img
(cd kicad && "$CLI" sch export pdf -o ../img/schematic.pdf lab2.kicad_sch >/dev/null)
(cd kicad && "$CLI" pcb export pdf --layers F.Cu,B.Cu,F.Silkscreen,Edge.Cuts --mode-single -o ../img/pcb_layout.pdf lab2.kicad_pcb >/dev/null)
(cd kicad && "$CLI" pcb render --side top --width 1600 --height 1000 -o ../img/render_top.png lab2.kicad_pcb >/dev/null)
(cd kicad && "$CLI" pcb render --side bottom --width 1600 --height 1000 -o ../img/render_bottom.png lab2.kicad_pcb >/dev/null)
IMG="$(cygpath -w "$PWD/img")"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/pdf2png.ps1 -Pdf "$IMG\\schematic.pdf" -OutPrefix "$IMG\\schematic" -Width 2400
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/pdf2png.ps1 -Pdf "$IMG\\pcb_layout.pdf" -OutPrefix "$IMG\\pcb_layout_page" -Width 4000
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/crop.ps1 -In "$IMG\\pcb_layout_page.png" -Out "$IMG\\pcb_layout.png"
rm -f img/pcb_layout_page.png
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/crop.ps1 -In "$IMG\\render_top.png" -Out "$IMG\\render_top_c.png" -Margin 10
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/crop.ps1 -In "$IMG\\render_bottom.png" -Out "$IMG\\render_bottom_c.png" -Margin 10

echo "== 8. Звіт (HTML -> Word docx/pdf)"
"$PY" scripts/make_report.py
cp -n "$IMG\\..\\report\\logo.jpeg" report/ 2>/dev/null || true
R="$(cygpath -w "$PWD")"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/report_to_docx.ps1 -Html "$R\\report\\report.html" \
  -Docx "$R\\АПКС_Процак_Ki-402_lab2.docx" -Pdf "$R\\АПКС_Процак_Ki-402_lab2.pdf"
echo "== Готово"
