"""
ЛР4 АПКС — Fusion 360 (твердотільне параметричне моделювання).
Процак Максим Степанович, КІ-402 -> цифра «2».

Скрипт будує модель і зберігає результати в теку Лаб4:
  1. Новий компонент Digit_2, ескіз контуру цифри «2» на площині XY.
  2. Extrude (New Body) на товщину T -> базове тіло.
  3. Ескіз на верхній грані цифри, три тексти:
       «Процак»     -> Extrude Join +RAISE мм      (опуклий)
       «Максим»     -> Extrude Cut  -ENGRAVE мм    (увігнутий)
       «Степанович» -> Extrude Cut  through all    (наскрізний)
  4. Експорт STL (тіло цифри) і скріншоти видового екрана.
Запуск: Utilities -> Add-Ins -> Scripts and Add-Ins -> «+» (Script from my computer) ->
вибрати теку Lab4Digit2 -> Run.
"""
import os
import traceback

import adsk.core
import adsk.fusion

# ---------------------------------------------------------------- параметри (мм)
W, H, S = 90.0, 130.0, 24.0       # ширина, висота цифри, ширина «сегмента»
T = 8.0                           # товщина цифри
RAISE, ENGRAVE = 2.0, 2.0         # висота опуклого / глибина увігнутого тексту
TEXT_H = {"top": 12.0, "mid": 12.0, "bot": 10.0}
FONT = "Arial"

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
STL_DIR = os.path.join(OUT_DIR, "stl")
IMG_DIR = os.path.join(OUT_DIR, "img")


def cm(v):                        # API Fusion працює в сантиметрах
    return v / 10.0


def P(x, y, z=0.0):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))


def digit2_outline():
    """Контур «2» (семисегментний стиль): верхня, середня, нижня смуги,
    правий верхній і лівий нижній сегменти. Проти годинникової стрілки."""
    m0, m1 = H / 2 - S / 2, H / 2 + S / 2
    return [(0, 0), (W, 0), (W, S), (S, S), (S, m0), (W, m0), (W, H),
            (0, H), (0, H - S), (W - S, H - S), (W - S, m1), (0, m1)]


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        os.makedirs(STL_DIR, exist_ok=True)
        os.makedirs(IMG_DIR, exist_ok=True)

        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent

        # 1. новий компонент
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = occ.component
        comp.name = "Digit_2"

        # 2. ескіз контуру і базове тіло
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = "Digit2_outline"
        pts = digit2_outline()
        lines = sk.sketchCurves.sketchLines
        for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
            lines.addByTwoPoints(P(x1, y1), P(x2, y2))
        prof = sk.profiles.item(0)

        ext = comp.features.extrudeFeatures
        ei = ext.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ei.setDistanceExtent(False, adsk.core.ValueInput.createByString(f"{T} mm"))
        base = ext.add(ei)
        base.name = "Extrude_Digit"
        body = base.bodies.item(0)
        body.name = "Digit2"
        top_face = base.endFaces.item(0)

        # 3. тексти на верхній грані
        sk2 = comp.sketches.add(top_face)
        sk2.name = "Texts_FIO"

        def add_text(s, cx, cy, h, box_w):
            ti = sk2.sketchTexts.createInput2(s, cm(h))
            c1 = sk2.modelToSketchSpace(P(cx - box_w / 2, cy - S / 2 + 1, T))
            c2 = sk2.modelToSketchSpace(P(cx + box_w / 2, cy + S / 2 - 1, T))
            ti.setAsMultiLine(c1, c2,
                              adsk.core.HorizontalAlignments.CenterHorizontalAlignment,
                              adsk.core.VerticalAlignments.MiddleVerticalAlignment, 0)
            ti.fontName = FONT
            ti.textStyle = adsk.fusion.TextStyles.TextStyleBold
            return sk2.sketchTexts.add(ti)

        t_last = add_text("Процак", W / 2, H - S / 2, TEXT_H["top"], W - 6)
        t_first = add_text("Максим", W / 2, H / 2, TEXT_H["mid"], W - 6)
        t_middle = add_text("Степанович", W / 2, S / 2, TEXT_H["bot"], W - 6)

        neg = adsk.fusion.ExtentDirections.NegativeExtentDirection

        # опуклий: Join назовні
        ji = ext.createInput(t_last, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        ji.setDistanceExtent(False, adsk.core.ValueInput.createByString(f"{RAISE} mm"))
        ji.participantBodies = [body]
        ext.add(ji).name = "Join_Surname"

        # увігнутий: Cut всередину на ENGRAVE
        ci = ext.createInput(t_first, adsk.fusion.FeatureOperations.CutFeatureOperation)
        ci.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByString(f"{ENGRAVE} mm")), neg)
        ci.participantBodies = [body]
        ext.add(ci).name = "Cut_Name"

        # наскрізний: Cut на глибину, більшу за товщину
        ti = ext.createInput(t_middle, adsk.fusion.FeatureOperations.CutFeatureOperation)
        ti.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByString(f"{T + 2} mm")), neg)
        ti.participantBodies = [body]
        ext.add(ti).name = "ThruCut_Patronymic"

        # Наскрізний виріз відділяє «острівці» всередині букв (о, а, е, в) в окремі тіла.
        bodies = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
        main = max(bodies, key=lambda b: b.volume)
        main.name = "Digit2"
        for b in bodies:
            if b != main:
                b.name = "Island_" + b.name

        # 4. експорт STL (основне тіло) і скріншоти
        em = design.exportManager
        so = em.createSTLExportOptions(main, os.path.join(STL_DIR, "digit2_fusion.stl"))
        so.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        so.isBinaryFormat = True
        em.execute(so)

        vp = app.activeViewport
        for name, orient in (("fusion_iso", adsk.core.ViewOrientations.IsoTopRightViewOrientation),
                             ("fusion_top", adsk.core.ViewOrientations.TopViewOrientation)):
            cam = vp.camera
            cam.viewOrientation = orient
            cam.isFitView = True
            vp.camera = cam
            vp.refresh()
            adsk.doEvents()
            vp.saveAsImageFile(os.path.join(IMG_DIR, name + ".png"), 1600, 1000)

        ui.messageBox(
            "Модель «2» побудовано.\n\n"
            f"Тіл у компоненті: {len(bodies)} (основне + острівці букв наскрізного тексту)\n"
            f"Об'єм основного тіла: {main.volume * 1000:.0f} мм³\n\n"
            f"STL: {os.path.join(STL_DIR, 'digit2_fusion.stl')}\n"
            f"Скріншоти: {IMG_DIR}")
    except Exception:
        if ui:
            ui.messageBox("Помилка:\n{}".format(traceback.format_exc()))
