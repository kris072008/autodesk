"""
Fusion 360 Python Script – Keyboard Generator
Creates a simplified QWERTY keyboard model at the world origin.

Layout  : 5 rows (Function, Number, QWERTY, ASDF, ZXCV + Space)
Units   : all values in centimetres (Fusion 360 internal unit = cm)
Run via : Tools > Add-Ins > Scripts and Add-Ins > (select file) > Run
"""

import adsk.core
import adsk.fusion
import traceback

# ── Keyboard parameters ────────────────────────────────────────────────────────
KEY_SIZE      = 1.6    # width & depth of a standard key (cm)
KEY_HEIGHT    = 0.4    # height of a keycap (cm)
KEY_GAP       = 0.2    # gap between keys (cm)
KEY_RADIUS    = 0.15   # fillet radius on keycap top edges (cm)

BASE_PADDING  = 0.8    # padding around key grid inside the base (cm)
BASE_HEIGHT   = 0.6    # total height of the keyboard base (cm)
BASE_RADIUS   = 0.3    # corner fillet radius on the base (cm)

STEP          = KEY_SIZE + KEY_GAP   # centre-to-centre spacing (cm)

# ── Row definitions  (label, col_offset, key_count) ───────────────────────────
# col_offset is a fractional column shift so rows look staggered like a real kbd
ROWS = [
    # row 0 – Function row  (Esc + F1-F12)
    [
        (0.00, 1),   # Esc
        (1.30, 1), (2.00, 1), (2.70, 1), (3.40, 1),   # F1-F4
        (4.30, 1), (5.00, 1), (5.70, 1), (6.40, 1),   # F5-F8
        (7.30, 1), (8.00, 1), (8.70, 1), (9.40, 1),   # F9-F12
    ],
    # row 1 – Number row  (` 1-0 - = Backspace)
    [(i * 1.0, 1) for i in range(13)] +
    [(13.0, 2)],     # Backspace is 2U wide
    # row 2 – QWERTY  (Tab + 13 keys)
    [(0.0, 1.5)] +   # Tab is 1.5U
    [(1.5 + i * 1.0, 1) for i in range(13)],
    # row 3 – ASDF  (CapsLock + 11 keys + Enter)
    [(0.0, 1.75)] +  # CapsLock
    [(1.75 + i * 1.0, 1) for i in range(11)] +
    [(12.75, 2.25)], # Enter is 2.25U
    # row 4 – ZXCV  (LShift + 10 keys + RShift)
    [(0.0, 2.25)] +  # LShift
    [(2.25 + i * 1.0, 1) for i in range(10)] +
    [(12.25, 2.75)], # RShift
    # row 5 – Bottom row  (Ctrl Alt Space …)
    [
        (0.00, 1.25), (1.25, 1.25), (2.50, 1.25),     # Ctrl, Win, Alt
        (3.75, 6.25),                                   # Spacebar 6.25U
        (10.00, 1.25), (11.25, 1.25),                  # Alt, Fn
        (12.50, 1.25), (13.75, 1.25),                  # Menu, Ctrl
    ],
]

# Row Y positions (front-to-back, row 5 at front)
ROW_Y = [r * STEP for r in [5, 4, 3, 2, 1, 0]]


def create_box(comp, sketch_plane, x, y, w, d, h):
    """Extrude a rectangle from sketch_plane upward by h."""
    sketches = comp.sketches
    sk = sketches.add(sketch_plane)
    lines = sk.sketchCurves.sketchLines
    lines.addTwoPointRectangle(
        adsk.core.Point3D.create(x, y, 0),
        adsk.core.Point3D.create(x + w, y + d, 0)
    )
    prof = sk.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(
        prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    ext_input.setDistanceExtent(
        False, adsk.core.ValueInput.createByReal(h)
    )
    return extrudes.add(ext_input).bodies.item(0)


def fillet_body(comp, body, radius):
    """Apply a fillet to all edges of a body."""
    edges = adsk.core.ObjectCollection.create()
    for edge in body.edges:
        edges.add(edge)
    fillet_input = comp.features.filletFeatures.createInput()
    fillet_input.addConstantRadiusEdgeSet(
        edges, adsk.core.ValueInput.createByReal(radius), True
    )
    try:
        comp.features.filletFeatures.add(fillet_input)
    except Exception:
        pass   # skip if fillet fails on tiny geometry


def run(context):
    ui = None
    try:
        app  = adsk.core.Application.get()
        ui   = app.userInterface
        doc  = app.documents.add(
            adsk.core.DocumentTypes.FusionDesignDocumentType
        )
        design = app.activeProduct
        root   = design.rootComponent

        # ── Work on a single component ────────────────────────────────────────
        occ   = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp  = occ.component
        comp.name = "Keyboard"
        xy    = root.xYConstructionPlane

        # ── Keyboard base ─────────────────────────────────────────────────────
        # Determine overall key-grid bounding box
        all_x = [x * STEP for row in ROWS for (x, _) in row]
        all_w = [w * STEP for row in ROWS for (_, w) in row]
        grid_w = max(x + w for x, w in zip(all_x, all_w))
        grid_d = ROW_Y[0] + STEP   # tallest Y extent

        base_x = -BASE_PADDING
        base_y = -BASE_PADDING
        base_w = grid_w + 2 * BASE_PADDING
        base_d = grid_d + 2 * BASE_PADDING

        base_body = create_box(
            comp, xy,
            base_x, base_y,
            base_w, base_d,
            BASE_HEIGHT
        )
        base_body.name = "Keyboard_Base"
        fillet_body(comp, base_body, BASE_RADIUS)

        # ── Keycaps ───────────────────────────────────────────────────────────
        # Build a temporary sketch plane at the top of the base
        offset_planes = comp.constructionPlanes
        plane_input   = offset_planes.createInput()
        plane_input.setByOffset(
            xy, adsk.core.ValueInput.createByReal(BASE_HEIGHT)
        )
        key_plane = offset_planes.add(plane_input)

        key_index = 0
        for row_i, row in enumerate(ROWS):
            y_pos = ROW_Y[row_i]
            for (col_offset, key_width) in row:
                x_pos = col_offset * STEP
                w     = key_width * KEY_SIZE + (key_width - 1) * KEY_GAP
                gap   = KEY_GAP * 0.5

                key_body = create_box(
                    comp, key_plane,
                    x_pos + gap, y_pos + gap,
                    w - KEY_GAP, KEY_SIZE - KEY_GAP,
                    KEY_HEIGHT
                )
                key_body.name = f"Key_{key_index:03d}"
                fillet_body(comp, key_body, KEY_RADIUS)
                key_index += 1

        # ── Fit view ──────────────────────────────────────────────────────────
        app.activeViewport.fit()

        ui.messageBox(
            f"✅  Keyboard created!\n"
            f"    {key_index} keycaps  +  base\n\n"
            f"    Base size: {base_w:.1f} cm × {base_d:.1f} cm",
            "Keyboard Generator"
        )

    except Exception:
        if ui:
            ui.messageBox("Script failed:\n" + traceback.format_exc())