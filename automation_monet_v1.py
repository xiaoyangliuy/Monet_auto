import json
from epics import caget, caput
import time
import sys
import subprocess
import numpy as np
#load pvs and valeus
with open("auto_monet.json", "r") as f:
    pv_input = json.load(f)
cores_pre = 'Core_'
pos = np.arange(16,19)
start_pos = 0.0
cmd = ["tomoscan",
       "--scan-type","single",
       "--tomoscan-prefix", "7bmtomo:TomoScan:"
       ]
end_name = 'real_test'
#loop among cores (based on position in robot tray)
for p in pos:
    caput("7bma1:rShtrA:Open", 1, wait=True, timeout=20)
    #check mounting position for all pvs
    print(f"start {cores_pre}{p} now") 
    if "Hexapod X" in pv_input:
        caput(pv_input["Hexapod X"]["pv"], start_pos, wait=True, timeout=20)
        time.sleep(0.2)
        if abs(caget(pv_input["Hexapod X"]["pv"]) - start_pos) > 1e-3:
            print(f"Hexapod X not at mount position after caput")
            sys.exit(1)

    if "Robot mount" in pv_input:
        for pv, val in zip(pv_input["Robot mount"]["pv"], pv_input["Robot mount"]["value"]):
            if abs(caget(pv) - val) > 1e-3:
                if pv == "7bmb1:m26":
                    caput(pv, val, wait=True, timeout=240)
                else:
                    caput(pv, val, wait=True, timeout=20)
            time.sleep(0.2)
            if abs(caget(pv) - val) > 1e-3:
                print(f"{pv} not at mount position after caput")
                sys.exit(1)

    if "Sample Theta" in pv_input:
        caput(pv_input["Sample Theta"]["pv"], start_pos, wait=True, timeout=20)
        time.sleep(0.2)
        if abs(caget(pv_input["Sample Theta"]["pv"]) - start_pos) > 1e-3: 
            print("Sample Theta not at mount position after caput")
            sys.exit(1)   

    if "Center 0 Deg" in pv_input:
        caput(pv_input["Center 0 Deg"]["pv"], start_pos, wait=True, timeout=20)
        time.sleep(0.2)
        if abs(caget(pv_input["Center 0 Deg"]["pv"]) - start_pos) > 1e-3: 
            print("Center 0 Deg not at mount position after caput")
            sys.exit(1)

    if "Center 90 Deg" in pv_input:
        caput(pv_input["Center 90 Deg"]["pv"], start_pos, wait=True, timeout=20)
        time.sleep(0.2)
        if abs(caget(pv_input["Center 90 Deg"]["pv"]) - start_pos) > 1e-3: 
            print("Center 90 Deg not at mount position after caput")
            sys.exit(1)
    print(f"Mounting position for all pvs checked for {cores_pre}{p}")
    time.sleep(2)

    #robot mount sample
    caput("MONET:SampleToMount", f"{cores_pre}{p}")
    print(f"Set Sample to Mount!")
    time.sleep(1)   
    print("Waiting before mount move")
    caput("MONET:MountSample", 1, wait=True, timeout=30)

    time.sleep(2)

    wait_time = 60
    wait_time_complete = 0
    while caget("MONET:MovementStatus", use_monitor=False) != "Idle":
        time.sleep(1)
        wait_time_complete += 1
        if wait_time_complete > wait_time:
            print("ERROR: Mount Sample did not complete in time")
            sys.exit(1)

    time.sleep(2)

    if caget("MONET:CurrentSample", use_monitor=False) != f"{cores_pre}{p}":
        print("ERROR 1: Could not update CurrentSample PV")
        #sys.exit(1)
    print(f"Sample {cores_pre}{p} mounted successfully")
    #move to bottom position (50 mm away)
    if "Sample bottom" in pv_input:
        c_hexbasey = caget(pv_input['Sample bottom']['pv'])
        target_bottom = c_hexbasey + pv_input["Sample bottom"]["value"]
        caput(pv_input["Sample bottom"]["pv"], target_bottom, wait=True, timeout=150)
        time.sleep(0.2)
        print(f"Hex Base Y moved to bottom position relatively {pv_input["Sample bottom"]["value"]} mm")
        if abs(caget(pv_input["Sample bottom"]["pv"]) - target_bottom) > 1e-3: 
            print("Hex Base Y not at bottom position after caput")
            sys.exit(1)
        time.sleep(0.5)
        caput("7bma1:rShtrA:Close", 1, wait=True, timeout=20)
        print("shutter closed for scan")
        time.sleep(5)

    	#do tomoscan
        fn = f"{cores_pre}{p}_bottom_{end_name}"
        caput("7bmtomo:TomoScan:FileName",fn, wait=True, timeout=30)
        input_name = caget("7bmtomo:TomoScan:FileName")
        if isinstance(input_name, (list, tuple)) or hasattr(input_name, '__iter__'):
            value = ''.join(chr(c) for c in input_name if c !=0).strip()
        else:
            value=str(input_name).strip()

        if value != fn:
            print("filename not in")
            sys.exit(1)

        result = subprocess.run(cmd)

        if result.returncode == 0:
            print(f"✅ TomoScan {fn} completed.\n")
        else:
            print(f"❌ Error in scan {fn}:\n{result.stderr}\n")
        time.sleep(50) #time to do FDT

    #move to middle position (55 mm away)
    if "Sample middle" in pv_input:
        c_hexbasey = caget(pv_input['Sample middle']['pv'])
        target_middle = c_hexbasey + pv_input["Sample middle"]["value"]
        caput(pv_input["Sample middle"]["pv"], target_middle, wait=True, timeout=150)
        time.sleep(0.2)
        print(f"Hex Base Y moved to middle position relatively {pv_input["Sample middle"]["value"]} mm")
        if abs(caget(pv_input["Sample middle"]["pv"]) - target_middle) > 1e-3: 
            print("Hex Base Y not at middle position after caput")
            sys.exit(1)
        time.sleep(0.5)
        #do tomoscan
        fn = f"{cores_pre}{p}_middle_{end_name}"
        caput("7bmtomo:TomoScan:FileName",fn, wait=True, timeout=30)

        input_name = caget("7bmtomo:TomoScan:FileName")
        if isinstance(input_name, (list, tuple)) or hasattr(input_name, '__iter__'):
            value = ''.join(chr(c) for c in input_name if c !=0).strip()
        else:
            value=str(input_name).strip()

        if value != fn:
            print("filename not in")
            sys.exit(1)

        result = subprocess.run(cmd)

        if result.returncode == 0:
            print(f"✅ TomoScan {fn} completed.\n")
        else:
            print(f"❌ Error in scan {fn}:\n{result.stderr}\n")
        time.sleep(30) #wait for FDT

    #move to top position (45 mm away)
    if "Sample top" in pv_input:
        for pv, val in zip(pv_input["Sample top"]["pv"], pv_input["Sample top"]["value"]):
            c_pos = caget(pv)
            target_top = c_pos + val
            if pv == "7bmb1:m26":
                caput(pv, target_top, wait=True, timeout=240)
            else:
                caput(pv, target_top, wait=True, timeout=30)
            time.sleep(0.2)
            print(f"{pv} moved to top position relatively {val} mm")
            if abs(caget(pv) - target_top) > 1e-3:
                print(f"Sample top {pv} not at top position after caput")
                sys.exit(1)
        time.sleep(0.5)
        #do tomoscan
        fn = f"{cores_pre}{p}_top_{end_name}"
        caput("7bmtomo:TomoScan:FileName",fn, wait=True, timeout=30)

        input_name = caget("7bmtomo:TomoScan:FileName")
        if isinstance(input_name, (list, tuple)) or hasattr(input_name, '__iter__'):
            value = ''.join(chr(c) for c in input_name if c !=0).strip()
        else:
            value=str(input_name).strip()

        if value != fn:
            print("filename not in")
            sys.exit(1)

        result = subprocess.run(cmd)

        if result.returncode == 0:
            print(f"✅ TomoScan {fn} completed.\n")
        else:
            print(f"❌ Error in scan {fn}:\n{result.stderr}\n")
        time.sleep(30) #wait for FDT

    #move to mount position for sample unmount
    if "Hexapod X" in pv_input:
        caput(pv_input["Hexapod X"]["pv"], start_pos, wait=True, timeout=20)
        time.sleep(0.2)
        if abs(caget(pv_input["Hexapod X"]["pv"]) - start_pos) > 1e-3:
            print(f"Hexapod X not at mount position after caput")
            sys.exit(1)

    if "Robot mount" in pv_input:
        for pv, val in zip(pv_input["Robot mount"]["pv"], pv_input["Robot mount"]["value"]):
            if pv == "7bmb1:m26":
                caput(pv, val, wait=True, timeout=240)
            else:
                caput(pv, val, wait=True, timeout=20)
            time.sleep(0.2)
            if abs(caget(pv) - val) > 1e-3:
                print(f"Robot mount {pv} not at mount position after caput")
                sys.exit(1)

    if "Sample Theta" in pv_input:
        caput(pv_input["Sample Theta"]["pv"], start_pos, wait=True, timeout=20)
        time.sleep(0.2)
        if abs(caget(pv_input["Sample Theta"]["pv"]) - start_pos) > 1e-3: 
            print("Sample Theta not at mount position after caput")
            sys.exit(1)

    if "Center 0 Deg" in pv_input:
        caput(pv_input["Center 0 Deg"]["pv"], start_pos, wait=True, timeout=20)
        time.sleep(0.2)
        if abs(caget(pv_input["Center 0 Deg"]["pv"]) - start_pos) > 1e-3:
            print("Center 0 Deg not at mount position after caput")
            sys.exit(1)

    if "Center 90 Deg" in pv_input:
        caput(pv_input["Center 90 Deg"]["pv"], start_pos, wait=True, timeout=20)
        time.sleep(0.2)
        if abs(caget(pv_input["Center 90 Deg"]["pv"]) - start_pos) > 1e-3:
            print("Center 90 Deg not at mount position after caput")
            sys.exit(1)
    time.sleep(1)
    caput("7bma1:rShtrA:Open", 1, wait=True, timeout=20)
    print("shutter open for mount")

    #robot mount sample
    if caget("MONET:CurrentSample") == 'None':
        print("ERROR: No Sample Mounted.")
        sys.exit(1)

    time.sleep(1)
    caput("MONET:DismountSample", 1)
    time.sleep(2)

    while caget("MONET:MovementStatus") != "Idle":
        time.sleep(1)
        wait_time_complete += 1
        if wait_time_complete > wait_time:
            print("ERROR: Dismount Sample did not complete in time")
            sys.exit(1)


    if caget("MONET:CurrentSample") != 'None':
        print("ERROR 2: Could not update CurrentSample PV")
        #sys.exit(1)

    print(f"Sample {cores_pre}{p} dismounted successfully")
    print(f"✅ Success {cores_pre}{p} ✅")

print("finish the loop")
