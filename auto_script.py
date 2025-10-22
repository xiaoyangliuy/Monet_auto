from Auto_tomo_class import tomo_auto
import os
os.chdir("C:/Research/OneDrive - Argonne National Laboratory/anl/github/Monet_auto/Monet_auto")
config_file = "auto_monet.json"
logpath = "log_auto_tomo.txt"
dry_run = True
tomo = tomo_auto(config_file, logpath, dry_run=dry_run)
Y_motors_names = tomo.pv_input["Robot_Y_mount"]["pv"] #list of pv names: Hexapod Y and hexabase Y
Y_motors_vals = tomo.pv_input["Robot_Y_mount"]["value"]
rest_motors_names = tomo.pv_input["Robot_mount_rest_motors"]["pv"] #list of pv names: Hexapod X, sample x,z, theta
rest_motors_vals = tomo.pv_input["Robot_mount_rest_motors"]["value"]
scan_locs = ["Sample_bottom", "Sample_top", "Sample_middle"] #more locations, then need more in json file

for i in range(len(tomo.sample_names)):
    _,rob_pos = tomo.current_sample(i) #check if robot and sample position match, return robot position as a string
    tomo.log_event(f"Robot will mount {rob_pos}")#robot mount sample
    #place holder for robot mounting sample, which will check/move mounting position and mount robot
    for s in scan_locs:
        tomo.log_event(f"Start location {s}")
        c_vals = tomo.get_pv_value(tomo.pv_input[s]["pv"])
        target_vals = [c_val + r_val for c_val, r_val in zip(c_vals, tomo.pv_input[s]["value"])]
        fn = tomo.get_fn(scanloc=s) #generate file name
        tomo.change_str_pv(tomo.pv_input["filename_entry"]["pv"], fn, wt=2) #change file name pv
        tomo.run_tomo()     
    tomo.log_event('robot unmount/exchange')#robot sample exchange
    #place holder for robot unmounting sample, which will check/move to mounting position and unmount
    tomo.save_log()
tomo.log_event("All scans completed.")