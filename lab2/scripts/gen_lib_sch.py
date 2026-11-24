"""
Генерує бібліотеки і принципову схему KiCad:
  kicad/lab2.pretty/SQ4|SQ8|SQ12|CONN3.kicad_mod  — футпринти
  kicad/lab2.kicad_sym                            — символи U1..U5, J1
  kicad/lab2.kicad_sch                            — схема (з'єднання мітками кіл)
  kicad/lab2.kicad_pro, sym-lib-table, fp-lib-table
Запуск: python scripts/gen_lib_sch.py
"""
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kicad")
OUT = os.path.abspath(OUT)
NS = uuid.UUID("6b1f3c2e-1d40-4a55-9a1e-402c5ad15000")  # стабільні UUID між перезапусками


def uid(*parts):
    return str(uuid.uuid5(NS, "/".join(str(p) for p in parts)))


def f(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- footprints
PAD_D, PAD_DRILL = 1.0, 0.5


def pad_positions(size):
    """Піни по периметру квадрата (проти годинникової стрілки, від лівої сторони зверху).
    Повертає список (x, y) у мм відносно центру; кількість = size."""
    k = size // 4
    inset = 0.75
    edge = size / 2 - inset
    if k == 1:
        offs = [0.0]
    else:
        pitch = (size - 2 * 2.25) / (k - 1)
        offs = [(i - (k - 1) / 2) * pitch for i in range(k)]
    pts = []
    pts += [(-edge, o) for o in offs]            # ліва сторона, зверху вниз
    pts += [(o, edge) for o in offs]             # низ, зліва направо
    pts += [(edge, -o) for o in offs]            # права сторона, знизу вгору
    pts += [(-o, -edge) for o in offs]           # верх, справа наліво
    return pts


def footprint_sq(size):
    name = f"SQ{size}"
    h = size / 2
    lines = [
        f'(footprint "{name}" (version 20240108) (generator "lab2_gen") (layer "F.Cu")',
        f'  (descr "Квадратний компонент {size}x{size} мм, {size} пінів (ЛР2 АПКС, GUID)")',
        '  (attr through_hole)',
        f'  (property "Reference" "REF**" (at 0 {f(-h - 1.4)} 0) (layer "F.SilkS") (uuid "{uid(name, "ref")}")',
        '    (effects (font (size 1 1) (thickness 0.15))))',
        f'  (property "Value" "{name}" (at 0 {f(h + 1.4)} 0) (layer "F.Fab") (uuid "{uid(name, "val")}")',
        '    (effects (font (size 1 1) (thickness 0.15))))',
        f'  (fp_rect (start {f(-h - 0.15)} {f(-h - 0.15)}) (end {f(h + 0.15)} {f(h + 0.15)})'
        f' (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS") (uuid "{uid(name, "silk")}"))',
        f'  (fp_circle (center {f(-h - 0.7)} {f(-h - 0.7)}) (end {f(-h - 0.45)} {f(-h - 0.7)})'
        f' (stroke (width 0.12) (type solid)) (fill solid) (layer "F.SilkS") (uuid "{uid(name, "pin1")}"))',
        f'  (fp_rect (start {f(-h)} {f(-h)}) (end {f(h)} {f(h)})'
        f' (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab") (uuid "{uid(name, "fab")}"))',
        f'  (fp_rect (start {f(-h - 0.5)} {f(-h - 0.5)}) (end {f(h + 0.5)} {f(h + 0.5)})'
        f' (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd") (uuid "{uid(name, "crt")}"))',
    ]
    for n, (x, y) in enumerate(pad_positions(size), start=1):
        shape = "rect" if n == 1 else "circle"
        lines.append(f'  (pad "{n}" thru_hole {shape} (at {f(x)} {f(y)}) (size {PAD_D} {PAD_D}) (drill {PAD_DRILL})'
                     f' (layers "*.Cu" "*.Mask") (uuid "{uid(name, "pad", n)}"))')
    lines.append(")")
    return name, "\n".join(lines) + "\n"


def footprint_conn(n_pins):
    name = f"CONN{n_pins}"
    pitch = 2.54
    y0 = -(n_pins - 1) / 2 * pitch
    h = n_pins * pitch / 2
    lines = [
        f'(footprint "{name}" (version 20240108) (generator "lab2_gen") (layer "F.Cu")',
        f'  (descr "Роз\'єм для вільних пінів, 1x{n_pins}, крок 2.54 мм")',
        '  (attr through_hole)',
        f'  (property "Reference" "REF**" (at 0 {f(-h - 1.2)} 0) (layer "F.SilkS") (uuid "{uid(name, "ref")}")',
        '    (effects (font (size 1 1) (thickness 0.15))))',
        f'  (property "Value" "{name}" (at 0 {f(h + 1.2)} 0) (layer "F.Fab") (uuid "{uid(name, "val")}")',
        '    (effects (font (size 1 1) (thickness 0.15))))',
        f'  (fp_rect (start -1.4 {f(-h - 0.15)}) (end 1.4 {f(h + 0.15)})'
        f' (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS") (uuid "{uid(name, "silk")}"))',
        f'  (fp_rect (start -1.27 {f(-h)}) (end 1.27 {f(h)})'
        f' (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab") (uuid "{uid(name, "fab")}"))',
        f'  (fp_rect (start -1.8 {f(-h - 0.5)}) (end 1.8 {f(h + 0.5)})'
        f' (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd") (uuid "{uid(name, "crt")}"))',
    ]
    for i in range(n_pins):
        shape = "rect" if i == 0 else "circle"
        lines.append(f'  (pad "{i + 1}" thru_hole {shape} (at 0 {f(y0 + i * pitch)}) (size 1.7 1.7) (drill 1.0)'
                     f' (layers "*.Cu" "*.Mask") (uuid "{uid(name, "pad", i)}"))')
    lines.append(")")
    return name, "\n".join(lines) + "\n"


# ---------------------------------------------------------------- symbols
G = 2.54


def sym_geometry(n_pins, all_right=False):
    """Піни символу: ліва сторона 1..n/2 зверху вниз, права n/2+1..n знизу вгору (як DIP).
    Повертає (half_w, half_h, [(num, x, y, angle)]) у координатах бібліотеки (Y вгору)."""
    if all_right:   # роз'єм: усі піни праворуч, зверху вниз
        half_w, half_h = 5.08, (n_pins + 1) * G / 2
        top = (n_pins - 1) * G / 2
        return half_w, half_h, [(i + 1, half_w + G, top - i * G, 180) for i in range(n_pins)]
    half = (n_pins + 1) // 2
    half_w = 7.62
    half_h = (half + 1) * G / 2
    top = (half - 1) * G / 2
    pins = []
    for i in range(half):
        pins.append((i + 1, -half_w - G, top - i * G, 0))
    for i in range(n_pins - half):
        pins.append((half + i + 1, half_w + G, -top + i * G, 180))
    return half_w, half_h, pins


def symbol_def(lib_name, ref_prefix, pin_names, value, footprint, descr, all_right=False):
    n = len(pin_names)
    hw, hh, pins = sym_geometry(n, all_right)
    out = [
        f'  (symbol "{lib_name}" (pin_names (offset 0.762)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
        f'    (property "Reference" "{ref_prefix}" (at 0 {f(hh + 1.27)} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "{value}" (at 0 {f(-hh - 1.27)} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Footprint" "{footprint}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        '    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        f'    (property "Description" "{descr}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        f'    (symbol "{lib_name}_0_1"',
        f'      (rectangle (start {f(-hw)} {f(hh)}) (end {f(hw)} {f(-hh)})'
        ' (stroke (width 0.254) (type default)) (fill (type background))))',
        f'    (symbol "{lib_name}_1_1"',
    ]
    for (num, x, y, ang), pname in zip(pins, pin_names):
        out.append(f'      (pin passive line (at {f(x)} {f(y)} {ang}) (length {G})'
                   f' (name "{pname}" (effects (font (size 1.27 1.27))))'
                   f' (number "{num}" (effects (font (size 1.27 1.27)))))')
    out.append("    )")
    out.append("  )")
    return "\n".join(out)


# ---------------------------------------------------------------- schematic
def build():
    os.makedirs(os.path.join(OUT, "lab2.pretty"), exist_ok=True)
    comps = design.components()
    conn = design.connector_pins()
    nets, _ = design.nets()

    fp_of = {}
    for size in sorted({c["size_mm"] for c in comps}):
        name, text = footprint_sq(size)
        with open(os.path.join(OUT, "lab2.pretty", name + ".kicad_mod"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    cname, ctext = footprint_conn(len(conn))
    with open(os.path.join(OUT, "lab2.pretty", cname + ".kicad_mod"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(ctext)
    for c in comps:
        fp_of[c["ref"]] = f"lab2:SQ{c['size_mm']}"
    fp_of["J1"] = f"lab2:{cname}"

    # символи: окремий для кожного U (назви пінів = символи GUID)
    syms = {}
    for c in comps:
        syms[c["ref"]] = symbol_def(
            f"{c['ref']}_{c['group']}", "U", [p["char"] for p in c["pins"]],
            c["group"], fp_of[c["ref"]],
            f"Компонент {c['size_mm']}x{c['size_mm']} мм з групи GUID {c['group']}")
    syms["J1"] = symbol_def("J_FREE", "J", [j["net"].replace("FREE_", "") for j in conn],
                            "FREE", fp_of["J1"], "Роз'єм вільних пінів", all_right=True)
    lib_names = {c["ref"]: f"{c['ref']}_{c['group']}" for c in comps}
    lib_names["J1"] = "J_FREE"

    with open(os.path.join(OUT, "lab2.kicad_sym"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write('(kicad_symbol_lib (version 20231120) (generator "lab2_gen")\n')
        fh.write("\n".join(syms.values()) + "\n)\n")

    root = uid("root")
    # розміщення символів на аркуші A4 (мм, кратно 1.27); J1 — біля лівого краю аркуша
    place = {"J1": (25.4, 101.6), "U2": (76.2, 63.5), "U4": (76.2, 139.7),
             "U1": (139.7, 63.5), "U5": (139.7, 116.84), "U3": (215.9, 101.6)}

    body = []
    lib_block = []
    for ref, text in syms.items():
        # у схемі lib_id має префікс бібліотеки
        lib_block.append(text.replace(f'(symbol "{lib_names[ref]}"', f'(symbol "lab2:{lib_names[ref]}"', 1))

    pin_lists = {c["ref"]: [p["num"] for p in c["pins"]] for c in comps}
    pin_lists["J1"] = [j["num"] for j in conn]
    values = {c["ref"]: c["group"] for c in comps}
    values["J1"] = "FREE"

    for ref in ["J1", "U1", "U2", "U3", "U4", "U5"]:
        X, Y = place[ref]
        n = len(pin_lists[ref])
        hw, hh, pins = sym_geometry(n, all_right=(ref == "J1"))
        su = uid("sym", ref)
        body.append(
            f'  (symbol (lib_id "lab2:{lib_names[ref]}") (at {f(X)} {f(Y)} 0) (unit 1)'
            f' (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{su}")\n'
            f'    (property "Reference" "{ref}" (at {f(X)} {f(Y - hh - 1.27)} 0) (effects (font (size 1.27 1.27))))\n'
            f'    (property "Value" "{values[ref]}" (at {f(X)} {f(Y + hh + 1.27)} 0) (effects (font (size 1.27 1.27))))\n'
            f'    (property "Footprint" "{fp_of[ref]}" (at {f(X)} {f(Y)} 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'    (property "Datasheet" "" (at {f(X)} {f(Y)} 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'    (property "Description" "" (at {f(X)} {f(Y)} 0) (effects (font (size 1.27 1.27)) hide))\n'
            + "".join(f'    (pin "{num}" (uuid "{uid("pin", ref, num)}"))\n' for num, *_ in pins)
            + f'    (instances (project "lab2" (path "/{root}" (reference "{ref}") (unit 1))))\n  )')
        # дроти від кінця піна назовні + мітка кола
        for num, x, y, ang in pins:
            px, py = X + x, Y - y
            net = design.pin_net(ref, num) if ref != "J1" else conn[num - 1]["net"]
            if ang == 0:      # пін зліва, дріт вліво
                ex, lang, just = px - 5.08, 180, "right bottom"
            else:             # пін справа, дріт вправо
                ex, lang, just = px + 5.08, 0, "left bottom"
            body.append(f'  (wire (pts (xy {f(px)} {f(py)}) (xy {f(ex)} {f(py)}))'
                        f' (stroke (width 0) (type default)) (uuid "{uid("w", ref, num)}"))')
            body.append(f'  (label "{net}" (at {f(ex)} {f(py)} {lang}) (fields_autoplaced yes)'
                        f' (effects (font (size 1.27 1.27)) (justify {just})) (uuid "{uid("l", ref, num)}"))')

    title = (f'  (title_block (title "ЛР2 АПКС: плата за GUID") (date "2026-11-24") (rev "1")'
             f' (company "НУ \\"Львівська політехніка\\", КІ-402")'
             f' (comment 1 "Процак М.С., варіант 15") (comment 2 "GUID {design.GUID}"))')
    texts = [f'  (text "Вільні піни (FREE_*) виведені на роз\'єм J1 біля меншої сторони плати"'
             f' (exclude_from_sim no) (at 12.7 177.8 0) (effects (font (size 1.524 1.524)) (justify left bottom))'
             f' (uuid "{uid("txt1")}"))']
    sch = ("(kicad_sch (version 20231120) (generator \"eeschema\") (generator_version \"8.0\")\n"
           f'  (uuid "{root}")\n  (paper "A4")\n{title}\n'
           "  (lib_symbols\n" + "\n".join(lib_block) + "\n  )\n"
           + "\n".join(body) + "\n" + "\n".join(texts) + "\n"
           '  (sheet_instances (path "/" (page "1")))\n)\n')
    with open(os.path.join(OUT, "lab2.kicad_sch"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(sch)

    with open(os.path.join(OUT, "sym-lib-table"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write('(sym_lib_table\n  (version 7)\n  (lib (name "lab2")(type "KiCad")(uri "${KIPRJMOD}/lab2.kicad_sym")(options "")(descr "ЛР2"))\n)\n')
    with open(os.path.join(OUT, "fp-lib-table"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write('(fp_lib_table\n  (version 7)\n  (lib (name "lab2")(type "KiCad")(uri "${KIPRJMOD}/lab2.pretty")(options "")(descr "ЛР2"))\n)\n')
    pro = os.path.join(OUT, "lab2.kicad_pro")
    if not os.path.exists(pro):
        with open(pro, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"meta": {"filename": "lab2.kicad_pro", "version": 1}}, fh, indent=2)
    # UUID символів потрібні платі для зв'язку футпринтів зі схемою
    with open(os.path.join(OUT, "sch_links.json"), "w", encoding="utf-8") as fh:
        json.dump({"root": root, "symbols": {r: uid("sym", r) for r in place},
                   "footprints": fp_of, "values": values}, fh, indent=2)
    print("Library + schematic generated in", OUT)


if __name__ == "__main__":
    build()
