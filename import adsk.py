import adsk.core
import adsk.fusion
import traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get the active design
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        if not design:
            ui.messageBox("No active Fusion 360 design found.")
            return

        # Get the root component
        root_comp = design.rootComponent

        # Create a new sketch on the XY plane
        sketches = root_comp.sketches
        xy_plane = root_comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)

        # Draw a 50mm x 50mm rectangle starting at the origin
        lines = sketch.sketchCurves.sketchLines
        # Fusion 360 uses centimeters internally, so 50mm = 5cm
        size = 5.0  # 5 cm = 50 mm

        rect = lines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(size, size, 0)
        )

        # Get the profile from the sketch
        prof = sketch.profiles.item(0)

        # Extrude the profile by 50mm (5cm) to create the cube
        extrudes = root_comp.features.extrudeFeatures
        ext_input = extrudes.createInput(
            prof,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )

        # Set the extrusion distance to 50mm
        distance = adsk.core.ValueInput.createByReal(size)
        ext_input.setDistanceExtent(False, distance)

        # Execute the extrusion
        extrudes.add(ext_input)

        ui.messageBox("50mm x 50mm x 50mm cube created successfully!")

    except Exception:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))