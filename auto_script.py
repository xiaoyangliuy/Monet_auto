from Auto_tomo_class import tomo_auto
from epics import caput, caget
import os
import numpy as np
import time

#for MONET experiment
os.chdir("/home/beams/7BMB/Desktop/monet/Monet_auto/")
config_file = "auto_monet.json"
logpath = "log_auto_tomo_20251030.txt"
dry_run = False
tomo = tomo_auto(config_file, logpath, dry_run=dry_run)
#Y_motors_names = tomo.pv_input["Robot_Y_mount"]["pv"] #list of pv names: Hexapod Y and hexabase Y
#Y_motors_vals = tomo.pv_input["Robot_Y_mount"]["value"]
#rest_motors_names = tomo.pv_input["Robot_mount_rest_motors"]["pv"] #list of pv names: Hexapod X, sample x,z, theta
#rest_motors_vals = tomo.pv_input["Robot_mount_rest_motors"]["value"]
scan_locs = ["Sample_bottom", "Sample_middle", "Sample_top"] #more locations, then need more in json file

for i in range(len(tomo.sample_names)):
    _,rob_pos = tomo.current_sample(i) #check if robot and sample position match, return robot position as a string
#    tomo.log_event(f"Robot will mount {rob_pos}")#robot mount sample
    #place holder for robot mounting sample, which will check/move mounting position and mount robot
#    caput("MONET:SampleToMount", f"Core_{rob_pos}")
#    time.sleep(1)
#    caput("MONET:MountSample", 1)
#    time.sleep(3)

#    current_sample = caget("MONET:CurrentSample")

#    while current_sample != f"Core_{rob_pos}":
#        current_sample = caget("MONET:CurrentSample")
#        time.sleep(1) 

    for s in scan_locs:
        if rob_pos == 17 and s == "Sample_top":
            pass
        elif rob_pos == 18 and s == "Sample_bottom":
            pass
        else:
            fn = tomo.get_fn(scanloc=s)
            tomo.change_str_pv(tomo.pv_input["filename_entry"]["pv"], fn, wt=2) #change file name pv
            tomo.log_event(f"Start location {s}")
            c_vals = tomo.get_pv_value(tomo.pv_input[s]["pv"])
            #target_vals = [c_val + r_val for c_val, r_val in zip(c_vals, tomo.pv_input[s]["value"])]
            target_vals = c_vals + tomo.pv_input[s]["value"]
            tomo.move_motor_pv(tomo.pv_input[s]["pv"],target_vals) #move motors and check motors
            time.sleep(0.1)
            tomo.run_tomo()     
#    tomo.log_event('robot unmount/exchange')#robot sample exchange
    #place holder for robot unmounting sample, which will check/move to mounting position and unmount
#    caput("MONET:DismountSample",1)
#    time.sleep(3)
    
#    sample_dismounted = caget("MONET:CurrentSample")

#    while sample_dismounted != "None":
#        sample_dismounted =  caget("MONET:CurrentSample")
#        time.sleep(1)
#    time.sleep(5)

    tomo.save_log()
tomo.log_event("All scans completed.")
'''
#for Ken experiment
os.chdir("C:/Research/OneDrive - Argonne National Laboratory/anl/github/Monet_auto/Monet_auto")
config_file = "auto_monet.json"
logpath = "log_auto_tomo.txt"
dry_run = True
tomo = tomo_auto(config_file, logpath, dry_run=dry_run)
y_step = tomo.pv_input["sample_move_step"]["value"]  #step size of y movement between each scan
y_motor = tomo.pv_input["sample_move_step"]["pv"]
#if same start/end for all samples
start = 0 #absolute hex base Y position
end = 100  #absolute hex base Y position
scan_pos = np.arange(start, end+1, y_step)
#if different start/end for each samples


for i in range(len(tomo.sample_names)):
    _,rob_pos = tomo.current_sample(i) #check if robot and sample position match, return robot position as a string
    tomo.log_event(f"Robot mounts {rob_pos}")#robot mount sample
    #place holder for robot mounting sample, which will check/move mounting position and mount robot
    fn = tomo.get_fn(motor="Ybase",scanloc=s)
    tomo.change_str_pv(tomo.pv_input["filename_entry"]["pv"], fn, wt=2) #change file name pv
    for s in scan_pos:
        tomo.log_event(f"Start scan at Y hex base location {s}")  
        tomo.run_tomo()
    tomo.log_event('robot unmount/exchange')#robot sample exchange
    #place holder for robot unmounting sample, which will check/move to mounting position and unmount
    tomo.save_log()
tomo.log_event("All scans completed.")
'''
