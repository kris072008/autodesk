
# car.py
# Fusion 360 script — creates a simple car at the origin (chassis + 4 wheels)

import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)

        root = design.rootComponent
        comps = root.occurrences

        # Create a new component for the car
        transform = adsk.core.Matrix3D.create()
        occ = comps.addNewComponent(transform)
        comp = adsk.fusion.Component.cast(occ.component)
        comp.name = 'SimpleCar'

        # Parameters (all units in cm)
        chassis_length = 10.0
        chassis_width  = 4.5
        chassis_height = 1.2
        wheel_radius   = 1.0
        wheel_thickness = 0.6
        wheel_offset_x = 3.2  # distance from center to wheel along X
        wheel_offset_y = (chassis_width/2.0) + (wheel_thickness/2.0) - 0.05
        wheel_z = - (chassis_height/2.0) - wheel_radius + 0.05  # place wheels slightly below chassis

        # Create chassis (box) via sketch rectangle and extrude
        sketches = comp.sketches
        xyPlane = comp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        rect_points = sketch.sketchCurves.sketchLines
        half_len = chassis_length/2.0
        half_wid = chassis_width/2.0
        rect_points.addTwoPointRectangle(
            adsk.core.Point3D.create(-half_len, -half_wid, 0),
            adsk.core.Point3D.create(half_len, half_wid, 0)
        )
        prof = sketch.profiles.item(0)
        extrudes = comp.features.extrudeFeatures
        ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(chassis_height)
        ext_input.setDistanceExtent(False, distance)
        ext = extrudes.add(ext_input)
        chassis_body = ext.bodies.item(0)
        chassis_body.name = 'Chassis'
        # Move chassis up so origin at center of chassis
        move_feats = comp.features.moveFeatures
        vector = adsk.core.Vector3D.create(0, 0, chassis_height/2.0)
        move_input = move_feats.createInput(adsk.core.ObjectCollection.create(), adsk.core.Matrix3D.create())
        col = adsk.core.ObjectCollection.create()
        col.add(chassis_body)
        move_input = move_feats.createInput(col, adsk.core.Matrix3D.create())
        mat = adsk.core.Matrix3D.create()
        mat.translation = vector
        move_input.transform = mat
        move_feats.add(move_input)

        # Function to create a wheel (cylinder) at given position
        def create_wheel(center_x, center_y, center_z, name):
            sketches = comp.sketches
            # create sketch on XZ plane rotating coordinates: easier to create cylinder by revolve or extrude from circle on YZ plane
            yzPlane = comp.yZConstructionPlane
            sk = sketches.add(yzPlane)
            sk.isComputeDeferred = True
            sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, center_y, 0), wheel_radius)
            sk.isComputeDeferred = False
            prof = sk.profiles.item(0)
            extrudes = comp.features.extrudeFeatures
            ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            thickness = adsk.core.ValueInput.createByReal(wheel_thickness)
            ext_input.setDistanceExtent(False, thickness)
            # set extrusion direction so thickness projects along X (to place thickness across)
            # create a transform to position sketch at correct X and Z
            # We'll create the extrusion and then move it into place
            ext = extrudes.add(ext_input)
            wheel_body = ext.bodies.item(0)
            wheel_body.name = name
            # Move wheel to desired center
            col = adsk.core.ObjectCollection.create()
            col.add(wheel_body)
            mat = adsk.core.Matrix3D.create()
            mat.translation = adsk.core.Vector3D.create(center_x, 0, center_z)
            # rotate about Z to align extrusion thickness along Y: already aligned, but ensure correct orientation
            move_input = comp.features.moveFeatures.createInput(col, mat)
            comp.features.moveFeatures.add(move_input)
            return wheel_body

        # Create 4 wheels
        wheels = []
        wheel_positions = [
            ( wheel_offset_x,  wheel_offset_y, wheel_z),
            ( wheel_offset_x, -wheel_offset_y, wheel_z),
            (-wheel_offset_x,  wheel_offset_y, wheel_z),
            (-wheel_offset_x, -wheel_offset_y, wheel_z),
        ]
        for i, pos in enumerate(wheel_positions):
            w = create_wheel(pos[0], pos[1], pos[2], f'Wheel_{i+1}')
            wheels.append(w)

        ui.messageBox('Simple car created at origin.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    adsk.terminate()
