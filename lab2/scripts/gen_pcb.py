"""
Генерує плату kicad/lab2.kicad_pcb (KiCad Python / pcbnew):
  - контур кредитної картки 85.6 x 53.98 мм з радіусом кутів 3.18 мм (ISO/IEC 7810 ID-1);
  - футпринти з kicad/lab2.pretty, прив'язані до символів схеми;
  - кола (net) за GUID; розміщення "більше зв'язків — ближче";
  - J1 (вільні піни) біля лівої, меншої сторони плати;
  - експорт Specctra DSN для автотрасувальника Freerouting.
Режими:
  python gen_pcb.py            -> створити плату і lab2.dsn
  python gen_pcb.py import     -> імпортувати lab2.ses (результат трасування) і зберегти плату
"""
import json
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design  # noqa: E402

KDIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kicad"))
PCB = os.path.join(KDIR, "lab2.kicad_pcb")
MM = pcbnew.FromMM

W, H, R = 85.6, 53.98, 3.18          # кредитна картка
X0, Y0 = 100.0, 100.0                 # лівий верхній кут плати

# розміщення (мм, координати плати): U5 має зв'язки з усіма -> у центрі кластера,
# U2 і U4 мають вільні піни -> ближче до J1 біля лівої короткої сторони.
PLACE = {
    "J1": (X0 + 4.0, Y0 + H / 2, 0),
    "U2": (X0 + 15.0, Y0 + 19.0, 0),
    "U4": (X0 + 15.0, Y0 + 35.0, 0),
    "U5": (X0 + 31.0, Y0 + H / 2, 0),
    "U1": (X0 + 31.0, Y0 + 11.0, 0),
    "U3": (X0 + 31.0, Y0 + 43.5, 0),
}


def seg(board, a, b, layer=pcbnew.Edge_Cuts, width=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
    s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
    s.SetLayer(layer)
    s.SetWidth(MM(width))
    board.Add(s)


def arc(board, start, mid, end, layer=pcbnew.Edge_Cuts, width=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(pcbnew.VECTOR2I(MM(start[0]), MM(start[1])),
                     pcbnew.VECTOR2I(MM(mid[0]), MM(mid[1])),
                     pcbnew.VECTOR2I(MM(end[0]), MM(end[1])))
    s.SetLayer(layer)
    s.SetWidth(MM(width))
    board.Add(s)


def outline(board):
    x1, y1, x2, y2 = X0, Y0, X0 + W, Y0 + H
    k = R * (1 - 0.70710678)
    seg(board, (x1 + R, y1), (x2 - R, y1))
    seg(board, (x2, y1 + R), (x2, y2 - R))
    seg(board, (x2 - R, y2), (x1 + R, y2))
    seg(board, (x1, y2 - R), (x1, y1 + R))
    arc(board, (x2 - R, y1), (x2 - k, y1 + k), (x2, y1 + R))
    arc(board, (x2, y2 - R), (x2 - k, y2 - k), (x2 - R, y2))
    arc(board, (x1 + R, y2), (x1 + k, y2 - k), (x1, y2 - R))
    arc(board, (x1, y1 + R), (x1 + k, y1 + k), (x1 + R, y1))


def text(board, s, x, y, size=1.2, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(size * 0.15))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(t)


def create():
    links = json.load(open(os.path.join(KDIR, "sch_links.json"), encoding="utf-8"))
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(MM(0.2))
    nc.SetTrackWidth(MM(0.3))
    nc.SetViaDiameter(MM(0.7))
    nc.SetViaDrill(MM(0.35))

    # кола
    netobj = {}
    all_nets, _ = design.nets()
    names = list(all_nets) + [j["net"] for j in design.connector_pins()]
    for n in names:
        ni = pcbnew.NETINFO_ITEM(board, "/" + n)  # як у схемі: /<мітка>
        board.Add(ni)
        netobj[n] = ni

    lib = os.path.join(KDIR, "lab2.pretty")
    for ref, (x, y, rot) in PLACE.items():
        fpname = links["footprints"][ref].split(":")[1]
        fp = pcbnew.FootprintLoad(lib, fpname)
        fp.SetReference(ref)
        fp.SetValue(links["values"][ref])
        fp.SetFPID(pcbnew.LIB_ID("lab2", fpname))
        fp.SetPath(pcbnew.KIID_PATH("/" + links["symbols"][ref]))
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetOrientationDegrees(rot)
        board.Add(fp)
        for pad in fp.Pads():
            num = int(pad.GetNumber())
            if ref == "J1":
                net = design.connector_pins()[num - 1]["net"]
            else:
                net = design.pin_net(ref, num)
            pad.SetNet(netobj[net])

    outline(board)
    text(board, "402CSAD15  ЛР2 АПКС", X0 + 48, Y0 + 8, 1.5)
    text(board, "Процак М.С., КІ-402", X0 + 48, Y0 + 11.5, 1.2)
    text(board, "GUID 026d6220-80f6-", X0 + 48, Y0 + 44, 1.0)
    text(board, "5b5d-ac5d-0a5dfb622ab7", X0 + 48, Y0 + 46.5, 1.0)
    for j in design.connector_pins():
        text(board, j["net"].replace("FREE_", ""), X0 + 6.2, Y0 + H / 2 + (j["num"] - 2) * 2.54 + 0.4, 0.9)

    board.Save(PCB)
    pcbnew.ExportSpecctraDSN(board, os.path.join(KDIR, "lab2.dsn"))
    print("PCB + DSN written")


def import_ses():
    board = pcbnew.LoadBoard(PCB)
    ok = pcbnew.ImportSpecctraSES(board, os.path.join(KDIR, "lab2.ses"))
    print("SES import:", ok)
    board.Save(PCB)
    tracks = [t for t in board.GetTracks()]
    vias = [t for t in tracks if t.GetClass() == "PCB_VIA"]
    length = sum(pcbnew.ToMM(t.GetLength()) for t in tracks if t.GetClass() == "PCB_TRACK")
    print(f"tracks: {len(tracks) - len(vias)}, vias: {len(vias)}, total length: {length:.1f} mm")


if __name__ == "__main__":
    import_ses() if len(sys.argv) > 1 and sys.argv[1] == "import" else create()
