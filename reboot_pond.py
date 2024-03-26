# this script is run AUTOMATICALLY when the RPi is powered on (rebooted)
# we check if there exists an outage.csv (if not, do nothing)
# if there is an outage.csv, and the autostart row has a '1', then run automate_pond.py with config

import os
import subprocess
from functions.pond_functions import *


def main():
    
    # hardcoded outage filename (THIS MUST BE UPDATED FOR YOUR DEVICE!!! provide the explicit, not relative, filepath)
    filename = "/home/pond/PondAutomation/configs/outage.csv"

    print(f"Using the filepath {filename} for the outage.csv file. If this is incorrect, please update the filename in reboot_pond.py\n")

    # only if there is a outage.csv will we attempt to read it
    if os.path.exists(filename):

        print('outage file exists')

        # pull in old outage csv
        outage_dict = csv_to_dict(filename)

        # check if autorestart is set (1 means yes autostart, 0 means don't autostart and go normally)
        if int(outage_dict.get("autostart", 0)) == 1: # type cast to integer, default val is 0 is the dict key doesn't exist

            # execute the autopond script in a new detached tmux session named autopond_reboot with proper configs
            #command = "tmux new-session -d 'python3 automate_pond.py --config "
            #command += outage_dict["config"]
            #command += "'" # essential ending ' to the shell command
            config_path = outage_dict["config"]

            # check if the auto_pond.py configuration file exists
            if os.path.exists(config_path):

                command = f"tmux new-session -d -s pond_reboot 'python3 ~/PondAutomation/automate_pond.py --config {config_path}'"

                # run the command using subprocess as a shell command
                print(command)
                subprocess.run(command, shell=True)

                print('autostart set to 1, pond is restarting where it left off previously...')

            else:
                print("configuration path did not exist, this likely caused issues with launching the tmux session")

    # else, we don't start the pond after boot.
    else:
        print('no outage file exists, pond is not autorestarting')
            #there's no outage.csv (or if there is, autostart == 0) from the previous automate_pond.py so the settings didn't specify rebooting automatically


if __name__ == "__main__":
    try:
        main() # run the above script
        
    except KeyboardInterrupt:
        print("\nUser shut down program with CTRL+C.")
    finally: 

        print("reboot_pond.py finished. check to see if tmux is running with --> tmux list-sessions")
        
            