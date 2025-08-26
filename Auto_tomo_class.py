import json
#from epics import caget, caput
import time
import sys
import subprocess
import numpy as np
import logging
import os
from datetime import datetime


class tomo_auto():
    def __init__(self, config_file, logpath, dry_run=False, exp = None):
        """Initialize the tomo_auto class with configuration file and log path
        config_file: path to the json configuration file
        logpath: path to save the log file
        dry_run: if True, do not execute commands, just log them
        """
        with open(config_file, 'r') as f:
            self.pv_input = json.load(f)
        self.dry_run = dry_run
        if not logpath:
            os.mkdirs(f'{logpath}', exist_ok=True)
        self._logpath = logpath
        self.log = []
        self.start_pos = 0.0
        self.tol = 1e-3  # tolerance for position checking
        self.fn = None  # filename for tomo scan
        self.cmd = self.pv_input["tomoscan_cmd"]["value"]  # command to run tomo scan
        
        #["tomoscan",
        #            "--scan-type", "single",
        #            "--tomoscan-prefix", "7bmtomo:TomoScan:"]
        self.pre_name = self.pv_input["scan_name_pre"]["value"]
        self.end_name = self.pv_input["scan_name_end"]["value"]
        self.sample_names, self.robs = self.read_sample()
        self.exp = None
        self.sample = None
        self.robpos = None

    def read_sample(self, check=False):
        """read sample name and robot position from a pre-defined csv file,
           return two lists: sample_name, rot_pos
        """
        self.sample_pos = np.genfromtxt(self.pv_input["sample_file"]["value"], delimiter=',', dtype=None, names=True, encoding=None)
        sample_names = self.sample_pos['sample'].tolist()
        rot_poss = self.sample_pos['robot_pos'].tolist() 
        if len(sample_names) != len(rot_poss):
            raise ValueError("Sample names and robot positions length mismatch, check the csv file")
        if check:
            print("Sample names and robot positions:")
            for name, pos in zip(sample_names, rot_poss):
                print(f"{name}: {pos}")
        return sample_names, rot_poss
    
    def current_sample(self, i=None):
        if i != None:
            self.sample = self.sample_names[i]
            self.robpos = self.robs[i]
        if self.sample is None or self.robpos is None:
            raise ValueError("No sample name or robot position name")
        self.log.append(f"✅Match sample {self.sample} and robot position {self.robpos}")
        return self.sample, self.robpos
    
    def get_pv_value(self,pv_name):
        """get the value of a pv"""
        if self.dry_run:
            self.log_event(f"Dry run: would get value of {pv_name}")
            return None
        value = caget(pv_name,wait=True, timeout=30)
        print(f"{pv_name} is at {value}")
        self.log_event(f"{pv_name} is at {value}")
        return value
    
    def log_event(self, event):
        """log an event with timestamp
            input: event string"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} | {event}"
        self.log.append(log_entry)
        print(log_entry)

    def save_log(self):
        """save the log to a file and clear the log list"""
        with open(f'{self._logpath}', 'w') as f_log:
            json.dump(self.log, f_log, indent=4)
            for line in self.log:
                f_log.write(f"{line}\n")
            print(f"part log saved")
        self.log.clear()
    
    def move_motor_pv(self, pv_name, target_value, scanloc=None):
        """move a motor pv to target value
        check if the motor pv is at target value within tolerance"""
        if self.dry_run:
            self.log_event(f"Dry run: would move {pv_name} to {target_value}")
            return True
        caput(pv_name, target_value, wait=True, timeout=30)
        print(f"moving {pv_name} to {target_value}.")
        self.log_event(f"moving {pv_name} to {target_value}")
        time.sleep(1) #wait for the pv to update
        self.check_motor_pv(pv_name, target_value)
        if scanloc != None:
            self.fn = f"{self.pre_name}{self.sample}_robpos{self.robpos}_{scanloc}{self.end_name}"
            return self.fn

    def check_motor_pv(self, pv_name, target_value):
        """check if the motor pv is at target value within tolerance"""
        if self.dry_run:
            self.log_event(f"Dry run: would check {pv_name} for {target_value}")
            return True
        current_value = caget(pv_name)
        if abs(current_value - target_value) > self.tol:
            print(f"{pv_name} is not at target value.")
            self.log_event(f"❌{pv_name} is at {current_value}, target is {target_value}, not at target")
            self.save_log()
            sys.exit(1)
        else:
            print(f"{pv_name} is at target value.")
            self.log_event(f"✅{pv_name} is at {current_value}, target is {target_value}, at target")
            return True

    def move_check_mult_mtrs(self, name, val, wt=None): 
        """move and check multiple motors given a list of names, values and optional wait times"""
        if len(name) != len(val):
            raise ValueError("Motor names and values length mismatch")
        if wt != None:
            if len(wt) != len(name):
                raise ValueError("Motor names and wait times length mismatch")
        self.log_event("Begin check multiple motor positions")
        for i,nm in enumerate(name):
            self.move_motor_pv(nm, val[i])
            time.sleep(wt[i]) if wt != None else time.sleep(1)
            self.check_motor_pv(nm, val[i])
        self.log_event("All required motors were moved to target positions")

    def change_str_pv(self, pv_name, target_str, wt=1):
        """change a string pv to target string"""
        if self.dry_run:
            self.log_event(f"Dry run: would change {pv_name} to {target_str}")
            return True
        caput(pv_name, target_str, wait=True, timeout=30)
        time.sleep(wt) #wait for the pv str to update
        print(f"move {pv_name} to {target_str}.")
        self.log_event(f"move {pv_name} to {target_str}")
        self.check_str_pv(pv_name, target_str)
        return True

    def check_str_pv(self, pv_name, target_str):
        """check if a string pv is at target string"""
        if self.dry_run:
            self.log_event(f"Dry run: would check {pv_name} for {target_str}")
            return True
        input_str = caget(pv_name)
        if isinstance(input_str, (list, tuple)) or hasattr(input_str, '__iter__'):
            value = ''.join(chr(c) for c in input_str if c !=0).strip()
        else:
            value=str(input_str).strip()
        if value != target_str:
            print("❌Input str for {pv_name} is not at target str.")
            self.log_event(f"❌{pv_name} is at {value}, target is {target_str}, not at target")
            self.save_log()
            sys.exit(1)
        return True

    def run_tomo(self):
        """run tomo scan command"""
        if self.dry_run:
            self.log_event(f"Dry run: would run command {self.cmd}")
        result = subprocess.run(self.cmd)
        if result.returncode == 9:
            print(f"✅ TomoScan {self.fn} completed.")
            self.log_event(f"✅ TomoScan {self.fn} completed.")
            time.sleep(30) #wait for FDT to finish
        else:
            print(f"❌ TomoScan {self.fn} failed with return code {result.returncode}.")
            self.log_event(f"❌ TomoScan {self.fn} failed with return code {result.returncode}.")
            self.save_log()
            sys.exit(1)
        return True

if __name__ == "__main__":
    os.chdir("C:/Research/OneDrive - Argonne National Laboratory/anl/github/Monet_auto/Monet_auto")
    config_file = "auto_monet.json"
    logpath = "log_auto_tomo.txt"
    dry_run = True
    tomo = tomo_auto(config_file, logpath, dry_run=dry_run)
    Y_motors_names = tomo.pv_input["Robot Y mount"]["pv"] #list of pv names: Hexapod Y and hexabase Y
    Y_motors_vals = tomo.pv_input["Robot Y mount"]["value"]
    if len(Y_motors_names) != len(Y_motors_vals):
        raise ValueError("Mount Y stages names and values length mismatch, check the json file")
    rest_motors_names = tomo.pv_input["Robot mount rest motors"]["pv"] #list of pv names: Hexapod X, sample x,z
    rest_motors_vals = tomo.pv_input["Robot mount rest motors"]["value"]
    if len(rest_motors_names) != len(rest_motors_vals):
        raise ValueError("Mount rest stages names and values length mismatch, check the json file")
    scan_locs = ["bottom", "top", "center"]

    for i in range(len(tomo.sample_names)):
        tomo.current_sample(i)
        #check all pvs at mounting position
        tomo.move_check_mult_mtrs(Y_motors_names, Y_motors_vals)
        tomo.move_check_mult_mtrs(rest_motors_names, rest_motors_vals)
        #robot mount sample
        #place holder
        #move Hexapod Y to first sample position (bottom), relative value
        for s in scan_locs:
            c_val = tomo.get_pv_value(tomo.pv_input[s]["pv"])
            target_val = c_val + tomo.pv_input[s]["value"]
            fn = tomo.move_motor_pv(tomo.pv_input[s]["pv"], target_val, scanloc=s) #move stage and get filename
            tomo.change_str_pv(tomo.pv_input["file_name_pv"]["pv"], fn, wt=1) #change file name pv
            tomo.run_tomo()





        tomo.check_mount_pvs(normtime=1, hexay=2, basey=60)
        #robot sample exchange
        #place holder
        #move robot to different scan positions
        tomo.move_motor_pv(tomo.pv_input["robot_pv"]["value"], tomo.robs[i])
        tomo.change_str_pv(tomo.pv_input["file_name_pv"]["value"], fn)
        tomo.run_tomo(tomo.cmd)
        tomo.save_log()
    print("All scans completed.")
'''
            
