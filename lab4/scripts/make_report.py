"""
Формує HTML-звіт ЛР4 (report/report.html); Word конвертує його у docx/pdf (scripts/report_to_docx.ps1).
Розділ AutoCAD підхоплює скріншоти img/autocad_*.png, коли вони з'являться.
Запуск: python scripts/make_report.py
"""
import html
import os
import re
import struct

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "report")
IMG = os.path.join(ROOT, "img")
e = html.escape


def img(name, width):
    path = os.path.join(IMG, name) if not name.startswith("logo") else os.path.join(OUT, name)
    src = name if name.startswith("logo") else "../img/" + name
    with open(path, "rb") as fh:
        head = fh.read(64 * 1024)
    w = h = None
    if head[1:4] == b"PNG":
        w, h = struct.unpack(">II", head[16:24])
    elif head[:2] == b"\xff\xd8":                      # JPEG: шукаємо маркер SOF
        i = 2
        while i < len(head) - 9:
            if head[i] != 0xFF:
                i += 1
                continue
            marker = head[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", head[i + 5:i + 9])
                break
            i += 2 + struct.unpack(">H", head[i + 2:i + 4])[0]
    if not w:
        return f'<img src="{src}" width="{width}">'
    return f'<img src="{src}" width="{width}" height="{round(width * h / w)}">'


def have(name):
    return os.path.exists(os.path.join(IMG, name))


def listing(text):
    lines = [e(l).replace("  ", "&nbsp;&nbsp;") or "&nbsp;" for l in text.rstrip().splitlines()]
    return '<p class="lst">' + "<br>".join(lines) + "</p>"


# дані G-code
gc = open(os.path.join(ROOT, "gcode", "digit2_fusion.gcode"), encoding="utf-8", errors="replace").read(200000)
t_s = int(re.search(r";TIME:(\d+)", gc).group(1))
fil_m = float(re.search(r";Filament used: ([\d.]+)m", gc).group(1))
layers = int(re.search(r";LAYER_COUNT:(\d+)", gc).group(1))
machine = re.search(r";TARGET_MACHINE.NAME:(.+)", gc).group(1).strip()
mass_g = 3.14159265 * (0.175 / 2) ** 2 * fil_m * 100 * 1.24     # PLA 1.24 г/см³, філамент 1.75 мм
t_str = f"{t_s // 3600} год {t_s % 3600 // 60} хв"

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
.code { font-family: 'Consolas'; font-size: 11pt; }
p.lst { font-family: 'Consolas'; font-size: 8.5pt; line-height: 100%; text-align: left; margin: 2pt 0 8pt 0; }
.cap { text-align: center; font-size: 12pt; margin-bottom: 10pt; }
.todo { color: #b00; font-weight: bold; }
"""

P = []
A = P.append
fig = [0]


def figure(name, width, cap):
    fig[0] += 1
    A('<p class="c">' + img(name, width) + '</p>')
    A(f'<p class="cap">Рис. {fig[0]}. {e(cap)}</p>')


for t in ["МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ", "НАЦІОНАЛЬНИЙ УНІВЕРСИТЕТ «ЛЬВІВСЬКА ПОЛІТЕХНІКА»",
          "Інститут комп’ютерних технологій, автоматики та метрології", "кафедра “Електронних обчислювальних машин”"]:
    A(f'<p class="c">{t}</p>')
A('<p class="c">' + img("logo.jpeg", 220) + '</p>')
A('<p class="c" style="font-size:20pt;font-weight:bold;margin-top:18pt">Звіт</p>')
A('<p class="c">з лабораторної роботи №4</p>')
A('<p class="c">з дисципліни «Автоматизація проєктування комп\'ютерних систем»</p>')
A('<p class="c">на тему: «3D-моделювання та підготовка до 3D-друку об’єкта»</p>')
A('<p class="c">Варіант: група КІ-402, цифра «2»</p>')
A('<p style="margin-top:60pt;margin-left:9.5cm;text-align:left">Виконав:<br>студент групи КІ-402<br>Процак М.С.</p>')
A('<p style="margin-left:9.5cm;text-align:left">Перевірив:<br>Шпіцер А.С.</p>')
A('<p class="c" style="margin-top:120pt">Львів – 2026</p>')
A('<br clear="all" style="page-break-before:always">')

A('<h1>ЛАБОРАТОРНА РОБОТА №4<br>3D-моделювання та підготовка до 3D-друку об’єкта</h1>')
A('<p><b>Мета роботи:</b> набути практичних навичок 3D-моделювання з використанням різних САПР та освоїти процес '
  'підготовки моделі до адитивного виробництва (3D-друку) за допомогою слайсера.</p>')
A('<h2>1. Варіант і параметри моделі</h2>')
A('<p>Група КІ-402 → базова цифра <b>«2»</b>. На цифрі розміщено прізвище, ім\'я та по батькові студента '
  '(Процак Максим Степанович) трьома типами контурів.</p>')
A('<table><tr><th>Елемент</th><th>Розмір / розміщення</th><th>Тип контуру</th><th>AutoCAD</th><th>Fusion 360</th></tr>'
  '<tr><td>Цифра «2»</td><td>90 × 130 мм, ширина сегмента 24 мм, товщина 8 мм</td><td>базове тіло</td>'
  '<td>PLINE → REGION → EXTRUDE</td><td>Sketch → Extrude (New Body)</td></tr>'
  '<tr><td>«Процак»</td><td>верхня смуга, висота шрифту 12 мм</td><td>опуклий, +2 мм</td>'
  '<td>EXTRUDE + UNION</td><td>Extrude <b>Join</b></td></tr>'
  '<tr><td>«Максим»</td><td>середня смуга, 12 мм</td><td>увігнутий, −2 мм</td>'
  '<td>EXTRUDE + SUBTRACT</td><td>Extrude <b>Cut</b> 2 мм</td></tr>'
  '<tr><td>«Степанович»</td><td>нижня смуга, 10 мм</td><td>наскрізний</td>'
  '<td>EXTRUDE 10 мм + SUBTRACT</td><td>Extrude <b>Cut</b> 10 мм (&gt; 8 мм)</td></tr></table>')
A('<p>Цифру виконано в «семисегментному» стилі: три горизонтальні смуги (верхня, середня, нижня) мають ширину, '
  'достатню для розміщення кожного з трьох текстів, а правий верхній і лівий нижній сегменти з\'єднують їх у форму «2». '
  'Шрифт — Arial Bold. Обидві моделі побудовано вбудованими засобами автоматизації САПР '
  '(AutoLISP-скрипт для AutoCAD і Python API для Fusion 360), що забезпечує однакову геометрію в обох системах.</p>')

# ---------------------------------------------------------------- AutoCAD
A('<h2>2. Моделювання в AutoCAD</h2>')
A('<table><tr><th>Крок</th><th>Команда</th><th>Дія</th></tr>'
  '<tr><td>1</td><td class="code">TEXT, TXTEXP</td><td>тексти ПІБ (стиль Arial Bold); TXTEXP розкладає текст на замкнені полілінії</td></tr>'
  '<tr><td>2</td><td class="code">REGION, SUBTRACT</td><td>контури букв перетворюються на області; внутрішні контури (о, а, р, е, в) віднімаються від зовнішніх</td></tr>'
  '<tr><td>3</td><td class="code">PLINE, REGION</td><td>2D-контур цифри «2» → замкнена область</td></tr>'
  '<tr><td>4</td><td class="code">EXTRUDE</td><td>область цифри видавлюється на 8 мм (3D-робочий простір)</td></tr>'
  '<tr><td>5</td><td class="code">MOVE, EXTRUDE, UNION</td><td>прізвище піднімається на верхню грань, видавлюється на +2 мм і об\'єднується з цифрою</td></tr>'
  '<tr><td>6</td><td class="code">EXTRUDE, SUBTRACT</td><td>ім\'я видавлюється з верхньої грані на −2 мм і вирізається</td></tr>'
  '<tr><td>7</td><td class="code">EXTRUDE, SUBTRACT</td><td>по батькові видавлюється на 10 мм (більше за товщину 8 мм) і вирізається наскрізь</td></tr>'
  '<tr><td>8</td><td class="code">-VIEW SEISO, STLOUT</td><td>ізометричний вид і експорт у STL</td></tr></table>')
if have("autocad_window.jpg"):
    figure("autocad_window.jpg", 640, "Фінальна модель у вікні AutoCAD 2027 (SE Isometric, Conceptual)")
if have("autocad_iso.png"):
    figure("autocad_iso.png", 560, "Модель AutoCAD: опуклий «Процак», увігнутий «Максим», наскрізний «Степанович» (PNGOUT)")
if not (have("autocad_window.jpg") or have("autocad_iso.png")):
    A('<p class="todo">[Скріншот моделі AutoCAD буде додано після запуску скрипта.]</p>')
A('<p>Під час першого запуску TXTEXP не прийняв вибір <span class="code">!lab4-ss</span> з повідомленням '
  '«Can\'t reenter LISP»: команда TXTEXP сама написана на AutoLISP, тому вираз LISP під час її роботи не '
  'обчислюється. Сценарій виправлено — тексти вибираються опцією <span class="code">_ALL</span> (на кресленні '
  'на цьому етапі є лише три тексти). Модель експортовано в digit2_autocad.stl.</p>')
A('<h3>Скрипт AutoLISP (lab4_digit2.lsp)</h3>')
A(listing(open(os.path.join(ROOT, "autocad", "lab4_digit2.lsp"), encoding="utf-8").read()))

# ---------------------------------------------------------------- Fusion
A('<h2>3. Моделювання в Autodesk Fusion 360</h2>')
A('<table><tr><th>Крок</th><th>Операція</th><th>Дія</th></tr>'
  '<tr><td>1</td><td>New Component</td><td>компонент Digit_2</td></tr>'
  '<tr><td>2</td><td>Sketch (XY) → Extrude, New Body</td><td>контур «2» з ліній, видавлювання на 8 мм</td></tr>'
  '<tr><td>3</td><td>Sketch on face → Text</td><td>ескіз на верхній грані, три тексти (Arial, Bold) у межах смуг</td></tr>'
  '<tr><td>4</td><td>Extrude <b>Join</b> +2 мм</td><td>опуклий текст «Процак»</td></tr>'
  '<tr><td>5</td><td>Extrude <b>Cut</b> 2 мм</td><td>увігнутий текст «Максим»</td></tr>'
  '<tr><td>6</td><td>Extrude <b>Cut</b> 10 мм</td><td>наскрізний текст «Степанович» (глибина більша за товщину)</td></tr>'
  '<tr><td>7</td><td>Save as STL</td><td>експорт тіла, сітка High</td></tr></table>')
figure("fusion_window.png", 640, "Fusion 360: модель і хронологія операцій (Timeline) внизу вікна")
figure("fusion_iso.png", 560, "Фінальна модель Fusion 360: опуклий, увігнутий і наскрізний текст")
A('<p>Наскрізний виріз відділяє внутрішні «острівці» букв із замкненими контурами (о, а, е, в у слові «Степанович») '
  'в окремі тіла — як у трафареті. Для друку експортується основне тіло цифри.</p>')
A('<h3>Скрипт Fusion 360 API (Lab4Digit2.py)</h3>')
A(listing(open(os.path.join(ROOT, "fusion", "Lab4Digit2", "Lab4Digit2.py"), encoding="utf-8").read()))

# ---------------------------------------------------------------- порівняння
A('<h2>4. Порівняльний аналіз САПР</h2>')
A('<table><tr><th>Критерій</th><th>AutoCAD (2D-екструзія)</th><th>Fusion 360 (параметричне моделювання)</th></tr>'
  '<tr><td>Текст як профіль</td><td>текст не є замкненим контуром — потрібні TXTEXP (Express Tools), REGION і ручне '
  'віднімання внутрішніх контурів букв</td><td>текст ескізу одразу є профілем для Extrude</td></tr>'
  '<tr><td>Булеві операції</td><td>окремі команди UNION / SUBTRACT після кожного EXTRUDE</td>'
  '<td>вбудовані в Extrude: Join / Cut / New Body</td></tr>'
  '<tr><td>Історія та зміни</td><td>немає дерева побудови: щоб змінити товщину чи текст, тіло треба будувати заново</td>'
  '<td>Timeline: зміна параметра (товщина, глибина, текст) перераховує модель</td></tr>'
  '<tr><td>Прив\'язка до граней</td><td>робота в UCS, ручне переміщення (MOVE) профілів на рівень грані</td>'
  '<td>ескіз створюється безпосередньо на грані тіла</td></tr>'
  '<tr><td>Експорт STL</td><td>STLOUT (лише 3D-тіла)</td><td>Save as STL з налаштуванням якості сітки</td></tr>'
  '<tr><td>Сильні сторони</td><td>точне 2D-креслення, звична командна робота, креслярська документація</td>'
  '<td>твердотільне моделювання, швидкі ітерації, підготовка до виробництва</td></tr></table>')
A('<p>Для цієї задачі <b>зручнішим є Fusion 360</b>: модель описується меншою кількістю операцій (5 проти ~12 команд), '
  'текст не потребує перетворення на контури, тип операції (Join/Cut) задається одразу під час видавлювання, а '
  'параметричне дерево дозволяє змінити будь-який розмір без перебудови. AutoCAD орієнтований насамперед на 2D-креслення: '
  '3D-тіло отримується екструзією окремих областей з подальшими булевими операціями, що придатно для простих '
  'призматичних деталей, але трудомістко для тексту з внутрішніми контурами.</p>')

# ---------------------------------------------------------------- Cura
A('<h2>5. Підготовка до друку в UltiMaker Cura</h2>')
A(f'<table><tr><th>Параметр</th><th>Значення</th></tr>'
  f'<tr><td>Принтер / сопло / матеріал</td><td>{e(machine)}, 0.4 мм, Generic PLA (1.75 мм)</td></tr>'
  '<tr><td>Модель</td><td>digit2_fusion.stl (Fusion 360), 90 × 130 × 10 мм, лежить на столі тильною стороною</td></tr>'
  '<tr><td>Висота шару (Layer Height)</td><td>0.2 мм</td></tr>'
  '<tr><td>Заповнення (Infill Density)</td><td>20 %, візерунок Cubic</td></tr>'
  '<tr><td>Підтримки (Support)</td><td>вимкнено — у моделі немає навислих частин: опуклий текст стоїть на верхній грані, '
  'вирізи відкриті догори</td></tr>'
  '<tr><td>Адгезія (Build Plate Adhesion)</td><td>Brim (обрис)</td></tr></table>')
figure("cura_settings.jpg", 640, "Вікно Cura: модель на столі Creality Ender-3, профіль Standard Quality 0.2 мм, підсумок нарізки")
figure("cura_panel.jpg", 380, "Cura: заповнення 20 % (Cubic), Auto-Support вимкнено, Adhesion увімкнено")
figure("cura_brim_crop.png", 380, "Cura (Custom): Build Plate Adhesion Type = Brim")
figure("cura_summary.jpg", 300, "Підсумок нарізки: час друку і витрата матеріалу")
A('<h3>Результати нарізки</h3>')
A(f'<table><tr><th>Показник</th><th>Значення</th></tr>'
  f'<tr><td>Час друку</td><td><b>{t_str}</b> ({t_s} с)</td></tr>'
  f'<tr><td>Матеріал</td><td><b>≈ {mass_g:.0f} г</b> PLA, {fil_m:.2f} м філаменту</td></tr>'
  f'<tr><td>Кількість шарів</td><td>{layers}</td></tr>'
  '<tr><td>G-code</td><td>Marlin, digit2_fusion.gcode</td></tr></table>')
A('<h3>Аналіз G-code (пошаровий перегляд)</h3>')
figure("cura_preview.jpg", 640, "Preview (Layer view): уся модель, блакитним — Brim")
figure("cura_layer20.jpg", 520, "Шар ≈ 20 (z ≈ 4 мм): заповнення Cubic (помаранчеве), стінки навколо наскрізних букв")
figure("cura_layer38.jpg", 520, "Шар 38 (z = 7.6 мм): верхня обшивка; увігнуте ім'я і наскрізне по батькові — порожнини")
A('<table><tr><th>Шари</th><th>Висота z</th><th>Що друкується</th></tr>'
  '<tr><td>1</td><td>0–0.2 мм</td><td>перший шар цифри і Brim навколо контуру</td></tr>'
  '<tr><td>1–30</td><td>0–6 мм</td><td>тіло цифри: стінки, нижня обшивка, заповнення 20 %; букви «Степанович» — '
  'отвори з власними стінками (наскрізний контур)</td></tr>'
  '<tr><td>31–40</td><td>6–8 мм</td><td>верхня обшивка цифри; з\'являються порожнини букв «Максим» (увігнутий контур, '
  'під ними слайсер друкує суцільне «дно»); «Степанович» лишається отвором</td></tr>'
  '<tr><td>41–50</td><td>8–10 мм</td><td>лише букви «Процак» (опуклий контур): стінки і суцільне заповнення '
  'тонких елементів</td></tr></table>')
A('<p>Отже, слайсер обробляє опуклий контур як окремі «острівці» над верхньою гранню, увігнутий — як порожнину з '
  'суцільним дном у верхніх шарах, а наскрізний — як отвір, що проходить через усі шари тіла й обрамлений стінками.</p>')

A('<h2>Висновок</h2>')
A(f'<p>У роботі побудовано 3D-модель цифри «2» (група КІ-402) з прізвищем, ім\'ям і по батькові трьома типами '
  'контурів — опуклим (Join/UNION), увігнутим і наскрізним (Cut/SUBTRACT) — у двох САПР: AutoCAD (екструзія 2D-областей '
  'з булевими операціями) і Fusion 360 (твердотільне параметричне моделювання). Fusion 360 виявився зручнішим для '
  'задачі завдяки тексту-профілю, вбудованим булевим операціям і хронології побудови. Модель підготовлено до друку в '
  f'UltiMaker Cura з параметрами шар 0.2 мм, заповнення 20 %, Brim, без підтримок: орієнтовний час друку — {t_str}, '
  f'витрата матеріалу — близько {mass_g:.0f} г PLA ({fil_m:.2f} м). Засвоєно навички 3D-моделювання, експорту STL, '
  'налаштування слайсера та аналізу G-code.</p>')

doc = ('<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">'
       f'<head><meta charset="utf-8"><title>ЛР4 АПКС</title><style>{CSS}</style></head>'
       '<body><div class="Section1">' + "\n".join(P) + '</div></body></html>')
with open(os.path.join(OUT, "report.html"), "w", encoding="utf-8") as fh:
    fh.write(doc)
print(f"report.html written; time {t_str}, mass {mass_g:.1f} g, layers {layers}")
