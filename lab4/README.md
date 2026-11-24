# ЛР4 АПКС — 3D-моделювання та підготовка до 3D-друку

**Студент:** Процак Максим Степанович, КІ-402 → цифра **«2»**

Цифра «2» 90 × 130 × 8 мм із ПІБ:

| Текст | Тип | AutoCAD | Fusion 360 |
|-------|-----|---------|------------|
| Процак | опуклий +2 мм | EXTRUDE + UNION | Extrude Join |
| Максим | увігнутий −2 мм | EXTRUDE + SUBTRACT | Extrude Cut |
| Степанович | наскрізний | EXTRUDE 10 мм + SUBTRACT | Extrude Cut 10 мм |

## Структура

| Шлях | Вміст |
|------|-------|
| `autocad/lab4_digit2.lsp`, `lab4_run.scr` | AutoLISP-скрипт моделі (AutoCAD 2027, потрібні Express Tools) |
| `fusion/Lab4Digit2/` | скрипт Fusion 360 API (Python) |
| `stl/` | `digit2_autocad.stl`, `digit2_fusion.stl` |
| `gcode/digit2_fusion.gcode` | G-code (Cura 5.14, Creality Ender-3) |
| `img/` | скріншоти AutoCAD, Fusion, Cura |
| `АПКС_Процак_Ki-402_lab4.docx/.pdf` | звіт |
| `scripts/make_report.py` | генератор звіту (HTML → Word) |

## Запуск

- **AutoCAD:** скопіювати `autocad/*` у `%USERPROFILE%\lab4_cad\`, New → `SCRIPT` → `lab4_run.scr`.
  Результат (STL, PNG) з'явиться в `%USERPROFILE%\lab4_out\`.
- **Fusion 360:** `Shift+S` → Scripts → «+» → тека `fusion/Lab4Digit2` → Run.

## Cura

Шар 0.2 мм, заповнення 20 % (Cubic), Brim, без підтримок (немає навислих частин):
**4 год 42 хв, ≈36 г PLA (11.95 м)**, 50 шарів.
