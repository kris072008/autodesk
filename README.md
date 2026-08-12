# autodesk

Fusion 360 Python API scripts that generate parametric models directly inside Autodesk Fusion, together with the dimension sheet behind the keyboard design.

## What is in here

**keyboard.py** builds a simplified five-row QWERTY keyboard at the world origin: a staggered key grid (function row, number row, QWERTY, ASDF, ZXCV, and a bottom row with a 6.25U spacebar), filleted keycaps, and a padded base. Key size, keycap height, gap, fillet radius, and base padding are constants at the top of the file, so the whole model rebuilds from a handful of parameters.

**wheel.py** (and its earlier copy, "# car.py") creates a SimpleCar component: a rectangular chassis extruded from a sketch on the XY plane, with four cylindrical wheels placed from wheel radius, thickness, and axle offsets.

**"-- Layout.lua"** is a reference sheet rather than a program. It holds the dimensions for a full custom mechanical keyboard build: MX key pitch and plate cutouts, stabiliser spacing, case geometry and typing angle, internal clearances for PCB, plate, foam, and keycaps, and hardware sizes for M3 screws, heat-set inserts, gaskets, USB-C, knob, OLED, and battery.

## Running a script

Open Fusion, then go to Utilities, Add-Ins, Scripts and Add-Ins (Shift+S). On the Scripts tab, click the plus beside My Scripts, point it at the folder holding the .py file, select the script, and press Run. Each script opens a new design document and builds its model at the world origin.

## Units

The internal unit in Fusion is the centimetre, so every numeric value in the Python scripts is in cm. The Lua layout sheet is written in millimetres, matching how keyboard hardware is normally specified.
