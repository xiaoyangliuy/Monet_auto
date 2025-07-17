import json
from epics import caget, caput
import time
import sys
import subprocess

#load pvs and valeus
with open("auto_monet.json", "r") as f:
    pv_input = json.load(f)

#loop among cores (based on position in robot tray)


#check mounting position for all pvs
if pv_input["name"] == 'Hexapod X':
    if abs(caget(pv_input["pv"]) - 0.0) > 1e-3:   
        print("Hexapod X not 0")
        sys.exit(1)

if pv_input["name"] == 'Robot mount':
    for pv, val in zip(pv_input["pv"], pv_input["value"]):
        caput(pv, val, wait=True, timeout=10)
        print(f"{pv} moved to robot mount position at {val} mm")
        time.sleep(0.5)
        if abs(caget(pv) - val) > 1e-3:
            print(f"{pv} not at mount position after caput")
            sys.exit(1)
    
if pv_input["name"] == 'Sample Theta':
    if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
        print("Sample Theta not 0")
        sys.exit(1)
if pv_input["name"] == 'Center 0 Deg':
    if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
        print("Center 0 Deg not 0")
        sys.exit(1)
if pv_input["name"] == 'Center 90 Deg':
    if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
        print("Center 90 Deg not 0")
        sys.exit(1)

time.wait(1)
#robot mount sample
if caget("MONET:CurrentSample") != 'None':
    print("ERROR: Cannot mount new sample.")
    sys.exit(1)


caput("MONET:SampleToMount", "Core_18")
time.sleep(1)   
caput("MONET:MountSample", 1)

if caget("MONET:CurrentSample") != 'Core_18':
    print("ERROR: Could not update CurrentSample PV")
    sys.exit(1)

#move to bottom position (50 mm away)
if pv_input["name"] == 'Sample bottom':
    c_hexbasey = caget(pv_input["pv"])
    target_bottom = c_hexbasey + pv_input["value"]
    caput(pv_input["pv"], target_bottom, wait=True, timeout=10)
    print(f"Hex Base Y moved to bottom position relatively {pv_input['value']} mm")
    if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
        print("Hex Base Y not at bottom position after caput")
        sys.exit(1)
time.sleep(5)
#do tomoscan

#move to middle position (55 mm away)
if pv_input["name"] == 'Sample middle':
    c_hexbasey = caget(pv_input["pv"])
    target_middle = c_hexbasey + pv_input["value"]
    caput(pv_input["pv"], target_middle, wait=True, timeout=10)
    print(f"Hex Base Y moved to bottom position relatively {pv_input['value']} mm")
    if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
        print("Hex Base Y not at middle position after caput")
        sys.exit(1)
time.sleep(5)

#move to top position (45 mm away)
if pv_input["name"] == 'Sample top':
    for pv, val in zip(pv_input["pv"], pv_input["value"]):
        c_pv = caget(pv)
        target_top = c_pv + val
        caput(pv, target_top, wait=True, timeout=10)
        print(f"{pv} moved to top position relatively {val} mm")
        time.sleep(0.5)
        if abs(caget(pv) - 0.0) > 1e-3:
            print(f"{pv} not at top position after caput")
            sys.exit(1) 
time.sleep(5)

#do tomoscan

#move to mount position for sample unmount
if pv_input["name"] == 'Hexapod X':
    if abs(caget(pv_input["pv"]) - 0.0) > 1e-3:   
        caput(pv_input["pv"], 0.0, wait=True, timeout=10)
        print("Hexapod X moved to mount position at 0.0 mm")
        if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
            print("Hexapod X not at mount position after caput")
            sys.exit(1)

if pv_input["name"] == 'Robot mount':
    for pv, val in zip(pv_input["pv"], pv_input["value"]):
        caput(pv, val, wait=True, timeout=10)
        print(f"{pv} moved to robot mount position at {val} mm")
        time.sleep(0.5)
        if abs(caget(pv) - val) > 1e-3:
            print(f"{pv} not at mount position after caput")
            sys.exit(1)
    
if pv_input["name"] == 'Sample Theta':
    if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
        caput(pv_input["pv"], 0.0, wait=True, timeout=10)
        print("Sample Theta moved to mount position at 0.0 deg")
        if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
            print("Sample Theta not at mount position after caput")
            sys.exit(1)

if pv_input["name"] == 'Center 0 Deg':
    if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
        caput(pv_input["pv"], 0.0, wait=True, timeout=10)
        print("Center 0 Deg moved to mount position at 0.0 deg")
        if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
            print("Center 0 Deg not at mount position after caput")
            sys.exit(1)

if pv_input["name"] == 'Center 90 Deg':
    if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
        caput(pv_input["pv"], 0.0, wait=True, timeout=10)
        print("Center 90 Deg moved to mount position at 0.0 deg")
        if abs(caget(pv_input["pv"]) - 0.0) > 1e-3: 
            print("Center 90 Deg not at mount position after caput")
            sys.exit(1)
time.wait(1)

#robot mount sample
if caget("MONET:CurrentSample") == 'None':
    print("ERROR: No Sample Mounted.")
    sys.exit(1)

time.sleep(1)   
caput("MONET:DismountSample", 1)

if caget("MONET:CurrentSample") != 'None':
    print("ERROR: Could not update CurrentSample PV")
    sys.exit(1)

