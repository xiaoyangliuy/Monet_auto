#for Ken experiment
from Auto_tomo_class import tomo_auto
from epics import caput, caget
import os
import numpy as np
import time

os.chdir("C:/Research/OneDrive - Argonne National Laboratory/anl/github/Monet_auto/Monet_auto")
config_file = "auto_monet.json"
logpath = "/data2/2025-10-/log_auto_tomo.txt"
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
    caput("MONET:SampleToMount", f"Core_{rob_pos}")
    time.sleep(1)
    caput("MONET:MountSample", 1)
    time.sleep(3)

    current_sample = caget("MONET:CurrentSample")

    while current_sample != f"Core_{rob_pos}":
        current_sample = caget("MONET:CurrentSample")
        time.sleep(1) 

    fn = tomo.get_fn(motor="Ybase",scanloc=s)
    tomo.change_str_pv(tomo.pv_input["filename_entry"]["pv"], fn, wt=2) #change file name pv
    for s in scan_pos:
        tomo.log_event(f"Start scan at Y hex base location {s}")  
        tomo.run_tomo()
    tomo.log_event('robot unmount/exchange')#robot sample exchange
    #place holder for robot unmounting sample, which will check/move to mounting position and unmount
    time.sleep(3)
    
    sample_dismounted = caget("MONET:CurrentSample")

    while sample_dismounted != "None":
        sample_dismounted =  caget("MONET:CurrentSample")
        time.sleep(1)
    time.sleep(5)

    tomo.save_log()
tomo.log_event("All scans completed.")
