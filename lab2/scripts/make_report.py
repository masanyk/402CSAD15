"""
Формує HTML-звіт ЛР2 (report/report.html) з даних проєкту; Word конвертує його у docx/pdf
(scripts/report_to_docx.ps1).
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
K = os.path.join(ROOT, "kicad")
OUT = os.path.join(ROOT, "report")
os.makedirs(OUT, exist_ok=True)

e = html.escape


def img(src, width):
    """<img> з явною висотою за пропорціями (Word інакше спотворює зображення)."""
    import struct
    path = os.path.normpath(os.path.join(OUT, src))
    with open(path, "rb") as fh:
        head = fh.read(32)
    if head[1:4] == b"PNG":
        w, h = struct.unpack(">II", head[16:24])
    else:
        return f'<img src="{src}" width="{width}">'
    return f'<img src="{src}" width="{width}" height="{round(width * h / w)}">'
comps = design.components()
nets, free = design.nets()
conn = design.connector_pins()

drc = open(os.path.join(K, "drc.rpt"), encoding="utf-8").read()
erc = open(os.path.join(K, "erc.rpt"), encoding="utf-8").read()
route = open(os.path.join(K, "freerouting.log"), encoding="utf-8", errors="replace").read()
gerbers = sorted(os.listdir(os.path.join(ROOT, "gerber")))


def route_stat(key):
    m = re.search(r'"%s":\s*\{(.*?)\}' % key, route, re.S)
    return dict(re.findall(r'"(\w+)":\s*([\d.]+)', m.group(1))) if m else {}


bends = route_stat("bends")
vias = route_stat("vias")

import subprocess  # noqa: E402
kpy = os.path.join(os.path.dirname(sys.executable), "python.exe")
stats = json.loads(subprocess.check_output([kpy, "-c", r"""
import pcbnew, json, collections
b = pcbnew.LoadBoard(r'%s')
l = collections.Counter(); n = collections.Counter()
for t in b.GetTracks():
    if t.GetClass() == 'PCB_TRACK':
        l[t.GetLayerName()] += pcbnew.ToMM(t.GetLength()); n[t.GetLayerName()] += 1
vias = sum(1 for t in b.GetTracks() if t.GetClass() == 'PCB_VIA')
fps = {f.GetReference(): [round(pcbnew.ToMM(f.GetPosition().x) - 100, 1), round(pcbnew.ToMM(f.GetPosition().y) - 100, 1)] for f in b.GetFootprints()}
print(json.dumps({'len': l, 'n': n, 'vias': vias, 'fps': fps}))
""" % os.path.join(K, "lab2.kicad_pcb")]).decode())
total_len = sum(stats["len"].values())

CSS = """
@page Section1 { size: 21.0cm 29.7cm; margin: 2.0cm 1.25cm 1.5cm 1.75cm; }
div.Section1 { page: Section1; }
body { font-family: 'Times New Roman'; font-size: 14pt; }
p { margin: 0 0 6pt 0; text-align: justify; line-height: 115%; }
p.c { text-align: center; }
h1 { font-size: 14pt; text-align: center; margin: 12pt 0 6pt 0; }
h2 { font-size: 14pt; margin: 12pt 0 6pt 0; }
h3 { font-size: 14pt; font-style: italic; margin: 10pt 0 4pt 0; }
table { border-collapse: collapse; margin: 4pt 0 8pt 0; }
td, th { border: 1px solid #000; padding: 2pt 5pt; font-size: 12pt; vertical-align: top; }
th { background: #e8e8e8; }
pre, .code { font-family: 'Consolas'; font-size: 10pt; line-height: 110%; margin: 4pt 0 8pt 0; }
.cap { text-align: center; font-size: 12pt; margin-bottom: 10pt; }
"""

parts = []
A = parts.append

# ---------------------------------------------------------------- титульний лист
A('<p class="c">МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ</p>')
A('<p class="c">НАЦІОНАЛЬНИЙ УНІВЕРСИТЕТ «ЛЬВІВСЬКА ПОЛІТЕХНІКА»</p>')
A('<p class="c">Інститут комп’ютерних технологій, автоматики та метрології</p>')
A('<p class="c">кафедра “Електронних обчислювальних машин”</p>')
A('<p class="c">' + img("logo.jpeg", 220) + '</p>')
A('<p class="c" style="font-size:20pt;font-weight:bold;margin-top:18pt">Звіт</p>')
A('<p class="c">з лабораторної роботи №2</p>')
A('<p class="c">з дисципліни «Автоматизація проєктування комп\'ютерних систем»</p>')
A('<p class="c">на тему: «Проєктування та топологія друкованої плати»</p>')
A('<p class="c">Варіант 15</p>')
A('<p style="margin-top:60pt;margin-left:9.5cm;text-align:left">Виконав:<br>студент групи КІ-402<br>Процак М.С.</p>')
A('<p style="margin-left:9.5cm;text-align:left">Перевірив:<br>Шпіцер А.С.</p>')
A('<p class="c" style="margin-top:120pt">Львів – 2026</p>')
A('<br clear="all" style="page-break-before:always">')

# ---------------------------------------------------------------- 1. мета і ТЗ
A('<h1>ЛАБОРАТОРНА РОБОТА №2<br>Проєктування та топологія друкованої плати</h1>')
A('<p><b>Мета роботи:</b> набути практичних навичок проєктування друкованих плат у САПР, '
  'дотримуючись жорстких конструктивних обмежень, та застосувати навички роботи з нестандартним '
  'технічним завданням, що базується на алгоритмічній генерації параметрів.</p>')
A('<h2>1. Технічне завдання</h2>')
A('<ol>'
  '<li>Згенерувати GUID на основі хешування повного імені (Прізвище, Ім\'я, По батькові).</li>'
  '<li>Кожна група GUID — квадратний компонент U1…U5; довжина групи — сторона в мм; кожен символ — пін; '
  'однакові символи — рівнозначні піни.</li>'
  '<li>Створити символи та футпринти U1…U5, з\'єднати однакові піни; вільні піни вивести на край '
  'однієї меншої сторони плати.</li>'
  '<li>Плата не більше 85.6 × 53.98 мм (кредитна картка); розміщення «більше зв\'язків — ближче»; '
  'двошарове трасування без гострих кутів з мінімальною довжиною доріжок.</li>'
  '<li>Виконати DRC та сформувати комплект Gerber RS-274X.</li></ol>')
A('<p><b>САПР:</b> KiCad 10.0.8 (методичка допускає EasyEDA, Altium Designer або KiCad). '
  'Автотрасувальник — Freerouting 2.1.0 (формат обміну Specctra DSN/SES). Усі етапи відтворюються '
  'скриптами (<span class="code">scripts/build.sh</span>): генерація бібліотеки та схеми, ERC, плата, '
  'трасування, DRC з перевіркою відповідності схемі, Gerber і зображення.</p>')

# ---------------------------------------------------------------- 2. GUID
A('<h2>2. Генерація GUID і розрахунок розмірів елементів</h2>')
A('<p>GUID отримано детерміновано як UUID версії 5 (RFC 4122): SHA-1 хеш повного імені в просторі '
  'імен <span class="code">NAMESPACE_DNS</span>. Повторний запуск завжди дає той самий результат:</p>')
A('<pre>import uuid\nFULL_NAME = "Процак Максим Степанович"\nGUID = str(uuid.uuid5(uuid.NAMESPACE_DNS, FULL_NAME))\n'
  f'# -&gt; {design.GUID}</pre>')
A(f'<p class="c" style="font-size:16pt"><b>GUID: {design.GUID}</b></p>')
A('<table><tr><th>Компонент</th><th>Група GUID</th><th>Довжина групи</th><th>Розмір, мм</th>'
  '<th>Піни (№: символ)</th><th>Футпринт</th></tr>')
for c in comps:
    pins = ", ".join(f'{p["num"]}:{p["char"]}' for p in c["pins"])
    A(f'<tr><td>{c["ref"]}</td><td class="code">{c["group"]}</td><td>{c["size_mm"]} символів</td>'
      f'<td>{c["size_mm"]} × {c["size_mm"]}</td><td class="code">{pins}</td><td>SQ{c["size_mm"]}</td></tr>')
A('</table>')
A('<p>Отже: U1 — 8 × 8 мм (8 пінів), U2, U3, U4 — по 4 × 4 мм (4 піни), U5 — 12 × 12 мм (12 пінів); '
  'усього 32 піни. Розміри збігаються для будь-якого GUID (формат 8-4-4-4-12), а унікальним для варіанта '
  'є набір символів, тобто з\'єднання.</p>')

# ---------------------------------------------------------------- 3. з'єднання
A('<h2>3. Таблиця з\'єднань</h2>')
A('<p>Правило: усі піни з однаковим символом GUID утворюють одне коло <span class="code">N_&lt;символ&gt;</span>. '
  'Якщо символ повторюється в межах одного компонента (наприклад «0» у U1 на пінах 1 і 8), це рівнозначні '
  'піни, які також з\'єднуються. Символи, що трапляються лише один раз, — вільні піни.</p>')
A('<table><tr><th>Коло</th><th>Символ</th><th>Піни</th><th>Обґрунтування (входження символу)</th></tr>')
for name, members in nets.items():
    ch = name[2:]
    groups = []
    for c in comps:
        idx = [str(p["num"]) for p in c["pins"] if p["char"] == ch]
        if idx:
            groups.append(f'{c["ref"]} («{c["group"]}», поз. {", ".join(idx)})')
    A(f'<tr><td class="code">{name}</td><td class="code">{ch}</td>'
      f'<td class="code">{", ".join(f"{r}.{p}" for r, p, _ in members)}</td><td>{"; ".join(groups)}</td></tr>')
A('</table>')
A('<p>Вільні піни (символ зустрічається один раз) виведені на роз\'єм J1 (1×3, крок 2.54 мм), розміщений '
  'біля лівої, меншої (53.98 мм) сторони плати:</p>')
A('<table><tr><th>Пін J1</th><th>Коло</th><th>Звідки</th><th>Символ</th></tr>')
for j in conn:
    A(f'<tr><td>J1.{j["num"]}</td><td class="code">{j["net"]}</td><td>{j["to"][0]}.{j["to"][1]}</td>'
      f'<td class="code">{j["to"][2]}</td></tr>')
A('</table>')

# ---------------------------------------------------------------- 4. бібліотека і схема
A('<h2>4. Бібліотечні елементи та принципова схема</h2>')
A('<p>Для кожного компонента створено символ (бібліотека <span class="code">lab2.kicad_sym</span>, назви '
  'пінів — символи GUID) і футпринт (<span class="code">lab2.pretty</span>):</p>')
A('<table><tr><th>Футпринт</th><th>Корпус</th><th>Розташування пінів</th><th>Контактні площадки</th></tr>'
  '<tr><td>SQ4</td><td>4 × 4 мм</td><td>по 1 піну на сторону</td><td rowspan="3">THT, Ø1.0 мм, '
  'отвір 0.5 мм; пін 1 — квадратна площадка; нумерація проти годинникової стрілки від лівої сторони</td></tr>'
  '<tr><td>SQ8</td><td>8 × 8 мм</td><td>по 2 піни на сторону, крок 3.5 мм</td></tr>'
  '<tr><td>SQ12</td><td>12 × 12 мм</td><td>по 3 піни на сторону, крок 3.75 мм</td></tr>'
  '<tr><td>CONN3</td><td>2.54 × 7.62 мм</td><td>1 × 3, крок 2.54 мм</td><td>THT, Ø1.7 мм, отвір 1.0 мм</td></tr>'
  '</table>')
A('<p>З\'єднання на схемі виконано мітками кіл (однакова назва мітки = електричне з\'єднання). '
  'Перевірка ERC: <b>0 помилок, 0 попереджень</b>. Список кіл, експортований зі схеми, автоматично '
  'порівняно з розрахованим за GUID — збіг 11 з 11 кіл.</p>')
A('<p class="c">' + img("../img/schematic.png", 580) + '</p>')
A('<p class="cap">Рис. 1. Принципова схема з усіма з\'єднаннями (KiCad Eeschema)</p>')

# ---------------------------------------------------------------- 5. топологія
A('<h2>5. Топологія друкованої плати</h2>')
A('<p><b>Форм-фактор:</b> контур 85.6 × 53.98 мм із радіусом кутів 3.18 мм — розмір кредитної картки '
  'ISO/IEC 7810 ID-1, тобто рівно гранично допустимий. Плата двошарова (F.Cu, B.Cu).</p>')
A('<p><b>Розміщення</b> за правилом «більше зв\'язків — ближче»: U5 має спільні кола з усіма іншими '
  'компонентами (з U1 — 4 кола, з U2, U3, U4 — по 3), тому стоїть у центрі кластера; U1 і U3 — над і під U5; '
  'U2 і U4 мають вільні піни, тому розміщені між U5 і роз\'ємом J1 біля лівої короткої сторони.</p>')
A('<table><tr><th>Елемент</th><th>X, мм</th><th>Y, мм</th></tr>')
for ref in ["J1", "U1", "U2", "U3", "U4", "U5"]:
    x, y = stats["fps"][ref]
    A(f'<tr><td>{ref}</td><td>{x}</td><td>{y}</td></tr>')
A('</table><p style="font-size:12pt">Координати центрів відносно лівого верхнього кута плати.</p>')
A(f'<p><b>Трасування:</b> ширина доріжок 0.3 мм, зазор 0.2 мм. Автотрасувальник Freerouting прокладає '
  f'доріжки лише під кутами 45° (злам 90° — {bends.get("90_degree_count", "0")}, '
  f'45° — {bends.get("45_degree_count", "?")}), тож гострих кутів немає. Загальна довжина доріжок — '
  f'{total_len:.1f} мм (F.Cu — {stats["len"].get("F.Cu", 0):.1f} мм, B.Cu — {stats["len"].get("B.Cu", 0):.1f} мм), '
  f'перехідних отворів — {stats["vias"]}: двосторонні THT-площадки дозволяють переходити між шарами без via.</p>')
A('<p class="c">' + img("../img/pcb_layout.png", 580) + '</p>')
A('<p class="cap">Рис. 2. Топологія плати: контур кредитної картки, розміщені компоненти, '
  'доріжки F.Cu (червоні) і B.Cu (сині)</p>')
A('<p class="c">' + img("../img/render_top_c.png", 430) + '</p>')
A('<p class="cap">Рис. 3. 3D-вигляд плати зверху (kicad-cli pcb render)</p>')
A('<p class="c">' + img("../img/render_bottom_c.png", 430) + '</p>')
A('<p class="cap">Рис. 4. 3D-вигляд плати знизу</p>')

# ---------------------------------------------------------------- 6. DRC
A('<h2>6. Звіт DRC</h2>')
A('<p>DRC виконано командою <span class="code">kicad-cli pcb drc --schematic-parity --severity-all</span>, '
  'яка перевіряє зазори, короткі замикання, непідключені піни та відповідність плати схемі. '
  'Результат: <b>0 порушень, 0 непідключених пінів, 0 розбіжностей зі схемою</b>.</p>')
A(f'<pre>{e(drc.strip())}</pre>')
A('<h3>Звіт ERC (схема)</h3>')
A(f'<pre>{e(erc.strip())}</pre>')

# ---------------------------------------------------------------- 7. Gerber
A('<h2>7. Виробничі файли Gerber RS-274X</h2>')
A('<p>Сформовано комплект Gerber RS-274X (розширення X2, одиниці мм, формат 4.6) і файл свердління '
  'Excellon; архів <span class="code">lab2_gerber.zip</span> придатний для замовлення плати у виробника.</p>')
desc = {"F_Cu": "мідь, верхній шар", "B_Cu": "мідь, нижній шар", "F_Mask": "паяльна маска, верх",
        "B_Mask": "паяльна маска, низ", "F_Silkscreen": "шовкографія, верх", "B_Silkscreen": "шовкографія, низ",
        "Edge_Cuts": "контур плати", "job": "опис комплекту (Gerber job)", ".drl": "свердління (Excellon)"}
A('<table><tr><th>Файл</th><th>Призначення</th></tr>')
for g in gerbers:
    d = next((v for k, v in desc.items() if k in g), "")
    A(f'<tr><td class="code">{g}</td><td>{d}</td></tr>')
A('</table>')

# ---------------------------------------------------------------- 8. висновок
A('<h2>Висновок</h2>')
A(f'<p>За GUID <span class="code">{design.GUID}</span>, отриманим з ПІБ, визначено 5 квадратних компонентів '
  '(8, 4, 4, 4 і 12 мм), 8 кіл з\'єднань і 3 вільні піни. У KiCad створено бібліотечні символи та футпринти, '
  'принципову схему (ERC без помилок) і двошарову плату у форм-факторі кредитної картки 85.6 × 53.98 мм. '
  'Компоненти розміщено за кількістю зв\'язків, вільні піни виведено на роз\'єм біля меншої сторони. '
  f'Трасування виконано без гострих кутів (лише 45°), загальна довжина доріжок {total_len:.1f} мм без '
  'перехідних отворів. DRC підтвердив відсутність коротких замикань, порушень зазорів і непідключених '
  'пінів, а також повну відповідність плати схемі. Сформовано комплект Gerber RS-274X, тож плата готова '
  'до виробництва та відповідає жорсткому обмеженню форм-фактора.</p>')

doc = ('<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">'
       f'<head><meta charset="utf-8"><title>ЛР2 АПКС</title><style>{CSS}</style></head>'
       '<body><div class="Section1">' + "\n".join(parts) + '</div></body></html>')
with open(os.path.join(OUT, "report.html"), "w", encoding="utf-8") as fh:
    fh.write(doc)
print("report.html written")
