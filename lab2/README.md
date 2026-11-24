# ЛР2 АПКС — проєктування та топологія друкованої плати

**Студент:** Процак Максим Степанович, КІ-402, варіант 15
**GUID:** `026d6220-80f6-5b5d-ac5d-0a5dfb622ab7` (UUID v5 від ПІБ, `scripts/design.py`)
**САПР:** KiCad 10.0.8, автотрасування — Freerouting 2.1.0

## Що де лежить

| Шлях | Вміст |
|------|-------|
| `АПКС_Процак_Ki-402_lab2.docx` / `.pdf` | звіт |
| `kicad/lab2.kicad_pro` | проєкт KiCad (відкрити двоклацом) |
| `kicad/lab2.kicad_sch` | принципова схема |
| `kicad/lab2.kicad_pcb` | плата 85.6 × 53.98 мм, розведена |
| `kicad/lab2.kicad_sym`, `kicad/lab2.pretty/` | символи та футпринти U1–U5, J1 |
| `kicad/drc.rpt`, `kicad/erc.rpt` | звіти DRC / ERC (0 помилок) |
| `gerber/`, `lab2_gerber.zip` | Gerber RS-274X + свердління Excellon |
| `img/` | зображення схеми й плати для звіту |
| `scripts/` | генератори: усе відтворюється однією командою |

## Відтворення

```bash
bash scripts/build.sh
```

Кроки: GUID і таблиця з'єднань → бібліотека та схема → ERC → плата і DSN →
Freerouting → імпорт трас → DRC з перевіркою відповідності схемі → Gerber → зображення → звіт.

Шляхи до KiCad і Freerouting задаються змінними `KICAD` і `FREEROUTING`
(за замовчуванням `%LOCALAPPDATA%\Programs\KiCad\10.0\bin` і `C:\Users\maksp\tools\freerouting\freerouting-2.1.0.jar`).
Freerouting 2.1.0 обрано, бо новіші версії потребують Java 25, а встановлена Java 21.
