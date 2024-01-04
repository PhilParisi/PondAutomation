import sys
import os
import csv
import argparse
import importlib.util
import smbus
import RPi.GPIO as GPIO
from datetime import datetime, timedelta


def update_pond_settings(settings):
    for key, value in settings.items():
        print(f"Current setting for {key}: {value}")
        user_input = input(f"Do you agree with this setting? (y/n): ").lower()
        
        if user_input in ['n', "no", "N", "No", "NO"]:
            new_value = input(f"Enter a new value for {key}: ")
            settings[key] = new_value
            print(f"Setting updated to: {new_value}")
        elif user_input != ['y', "yes", "Y", "Yes", "YES"]:
            print("Invalid input. Defaulting to current setting.")


def ask_user_about_settings(pond):

    pond_settings = pond.get_settings()

    # show user the key:value pairs of the dictionary for their approval
    for key, value in pond_settings.items():
        print(f"Current setting for {key}: {value}")
    
    user_input = input(f"Do you agree with these settings? (y/n): ").lower()

    # if don't approve, end script
    if user_input in ['n', 'no']:
        print("- please re-run this script, and be sure to update the settings")
        pond.set_error_status(True)

    # if approve, sys_status = True and script continues
    elif user_input in ['y', 'yes']:
        print('- user accepted settings')

    # if invalid input, end script
    else:    
        print("- invalid input, please re-run script")
        pond.set_error_status(True)


def print_pond_settings(pond):

    pond_settings = pond.get_settings()

    # show user the key:value pairs of the dictionary for their approval
    for key, value in pond_settings.items():
        print(f"Current setting for {key}: {value}")    


def create_folder(folder_name):
    try:
        # create a new folder with the specified name
        os.makedirs(folder_name)

        # print a success message
        print(f"- folder '{folder_name}' created successfully")

    except OSError as e:
        # handle the case where the folder already exists or there's an error
        print(f"Error creating folder '{folder_name}': {e}")


def get_user_pond_settings():
    user_input1 = float(input("How many MINUTES until the first flood?: "))
    user_input2 = float(input("What is the FLOOD duration in MINUTES?: "))
    user_input3 = float(input("What is the DROUGHT duration in MINUTES?: "))
    user_input4 = float(input("How many MINUTES do you want to run the program for? (type 0 for 'infinite' runtime): " ))

    if user_input4 == 0: # i input, no program ending
        total_program_runtime = float('inf')
    else: # if it's not a string, assume it's a number and use that
        total_program_runtime = user_input4

    pond_settings = {
        "minutes_till_first_flood": user_input1,
        "flood_duration": user_input2,
        "drought_duration": user_input3,
        "total_program_runtime": total_program_runtime
    }

    return pond_settings


def correct_pond_settings(pond_settings):

    if pond_settings["total_program_runtime"] == 0: # no program ending
        pond_settings["total_program_runtime"] = float('inf')

    return pond_settings


def write_dict_to_csv(dictionary, file_path):

    with open(file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # write each key-value pair to a new row
        for key, value in dictionary.items():
            writer.writerow([key, value])


class Pond:

    # constructor, called when creating an instance of the class
    def __init__(self, settings):

        # pond_settings.py stored inside Pond
        self.settings = settings

        # has_error used to kill script (has_error = TRUE means kill script, has_error = False means no errors keep running)
        self.has_error = False

        # pull in datetime to use for output data location
        self.name_for_output_folder = os.path.join('data',datetime.now().strftime("%d-%b-%Y %H:%M:%S").replace(" ", "_"))

        # name for output settings file
        self.name_for_output_settings_csv = os.path.join(self.name_for_output_folder,"pond_settings_used.csv")

        # name for output data files
        self.name_for_output_data_file = os.path.join(self.name_for_output_folder,"pond_data.csv")

        # CONTROL STATE VARIABLES
        # all states start off as False, and switch to True when getting into that state
        # general 'state' is used for switching between states in the control loop
        self.state = 0
        self.state_name = None # the textual name given to a state
        self.next_state = 0
        self.command = 0

        self.state0_entry = False # initialization [start in this state]
        self.state5_entry = False # first drought [waiting, no flow]
        self.state10_entry = False # regular drought [waiting, no flow]
        self.state20_entry = False # regular flood [filling tank, solenoid open]
        self.state99_entry = False # shutdown/error state [throw system errors to here, program runtime exceeded]

        # timers
        self.timers = {}       # timers is a dictionary that stores each new timer as another dictionary
                                    # the 'sub-dictionary' stores
                                        # -  DURATIONS in MINUTES (e.g every 40 minutes we have a drought)
                                        # -  the current time that was present when resetting the time (e.g. the time a flood starts, so we can use this as a baseline to count the duration off of)

        # power outage
        self.power_outage_filename = "configs/outage.csv"
        self.config_file_used = None
        self.state_just_switched = 0


    # GETTERS and SETTERS
    
    def get_settings(self):
        return self.settings

    def set_settings(self, settings):
        self.settings = settings

    def get_error_status(self):
        return self.has_error

    def set_error_status(self, status):
        self.has_error = status

    #def get_pond_state(self):
    #    return self.pond_state
    
    #def set_pond_state(self, state):
    #    self.pond_state = state

    def get_name_for_output_folder(self):
        return self.name_for_output_folder

    def set_name_for_output_folder(self, name):
        self.name_for_output_folder = name

    def get_name_for_output_settings_csv(self):
        return self.name_for_output_settings_csv

    def set_name_for_output_settings_csv(self, name):
        self.name_for_output_settings_csv = name

    def get_name_for_output_data_file(self):
        return self.name_for_output_data_file

    def set_name_for_output_data_file(self, name):
        self.name_for_output_data_file = name

    def get_setting(self, key):
        return self.settings.get(key, None)
    
    def get_power_outage_filename(self):
        return self.power_outage_filename
    
    def set_power_ouage_filename(self, filename):
        self.power_outage_filename = filename

    def get_config_file_used(self):
        return self.config_file_used

    def set_config_file_used(self, config_used):
        self.config_file_used = config_used


    # CONTROL STATE FUNCTIONS

    def get_state(self):
        return self.state
    
    def set_state(self, state):
        self.state = state
        self.set_state_name() # setter for set_state_name embedded here
    
    def get_state_name(self):
        return self.state_name

    def get_next_state(self):
        return self.next_state

    def set_next_state(self, next_state):
        self.next_state = next_state

    def get_command(self):
        return self.command
    
    def set_command(self, command):
        self.command = command

    def get_state_just_switched(self):
        return self.state_just_switched
    
    def set_state_just_switched(self, val):
        self.state_just_switched = val

    def get_state0_entry(self):
        return self.state0_entry
    
    def set_state0_entry(self, entered):
        self.state0_entry = entered

    def get_state5_entry(self):
        return self.state5_entry
    
    def set_state5_entry(self, entered):
        self.state5_entry = entered

    def get_state10_entry(self):
        return self.state0_entry
    
    def set_state10_entry(self, entered):
        self.state0_entry = entered

    def get_state20_entry(self):
        return self.state0_entry
    
    def set_state20_entry(self, entered):
        self.state0_entry = entered

    def get_state99_entry(self):
        return self.state0_entry
    
    def set_state99_entry(self, entered):
        self.state0_entry = entered


    def set_state_name(self):
        
        if self.state == 0:
            self.state_name = "initialization"
        if self.state == 5:
            self.state_name = "first_drought"
        if self.state == 10:
            self.state_name = "drought"
        if self.state == 20:
            self.state_name = "flood"
        if self.state == 99:
            self.state_name = "shutdown"



    # TIMER FUNCTIONS

    # self.timers is a dictionary, that holds {'duration': xx, 'current_time': xx} dicts

    # add_timer() allows a new timer to be created within the pond class
        # it takes in a name and duration in MINUTES
        # it creates a new timer within the dictionary timer timer_durations (converted to SECONDS) and sets the current time to timer_current_time

    def add_timer(self, timer_name, duration):

        if timer_name in self.timers: # check if already exists
            print(f"- timer '{timer_name}' already exists, skipping timer creation in add_timer()")
        else:
            time_to_store = datetime.now()
            self.timers[timer_name] = {'duration': (duration*60), 'current_time': time_to_store} # store the inputted duration and the current_time
            #print(f"- timer '{timer_name}' added")

    # reset_timer() allows the user to reset the timer to the current time. This should be done when switching into a new state that needs to be timed
    def reset_timer(self, timer_name):

        if timer_name in self.timers: # ensure the timer exists
            self.timers[timer_name]['current_time'] = datetime.now() # update the current_time with the RPi's time
            #print(f"- timer '{timer_name}' reset successfully")
        else:
            print(f"- timer '{timer_name}' does not exist, skipping reset_timer() function")

    # get_timer_duration() simply outputs the duration of the timer requested
    def get_timer_duration(self, timer_name):
        
        if timer_name in self.timers: # ensure existance
            return self.timers[timer_name]['duration']
        else:
            print(f"- timer '{timer_name}' does not exist, skipping get_timer_duration() function")

    # get_timer_current_time() simply outputs the current_time of the timer, likely for usage in logic statements (e.g. if (datetime.now() - get_timer_current_time()) > get_timer_duration() )
    def get_timer_current_time(self, timer_name):

        if timer_name in self.timers: #ensure existance
            return self.timers[timer_name]['current_time']
        else:
            print(f"- timer '{timer_name}' does not exist, skipping get_timer_current_time() function")

    # set_timer_current_time() is used for continuing the script after outages. this is equivalent to reset_timer() but using an inputted time instead of timenow()
    def set_timer_current_time(self, timer_name, new_time):

        if timer_name in self.timers: # ensure the timer exists
            self.timers[timer_name]['current_time'] = new_time # update the current_time with inputted time
 
        else:
            print(f"- timer '{timer_name}' does not exist, skipping reset_timer() function")      


    # POWER OUTAGE FUNCTIONS
    def update_pond_with_outage_settings(self):

        # only if there is a outage.csv will we attempt to read it
        if os.path.exists(self.get_power_outage_filename()):

            print('abc')

            # pull in old outage csv
            outage_dict = csv_to_dict(self.get_power_outage_filename())

            print(outage_dict["autostart"])
            print(int(outage_dict["autostart"]))

            print(outage_dict["mins_in_state"])
            print(float(outage_dict["mins_in_state"]))

            # check if autorestart is set (1 means yes autostart, 0 means don't autostart and go normally)
            if int(outage_dict["autostart"]) == 1:

                # when autorestarting, we want to update the next_state, the current state timer, and the total runtime
                print_w_time("\n***CONTINUING FROM POWER OUTAGE/CYCLE***\n")

                # assign next state (pickup up in the same state as stated in file)
                self.set_next_state(outage_dict["state"]) # the actual pond.state attribute gets set in the loop)
        
                # update state timer (we've already been in state, and timer holds time when we got INTO state, so do datetime - mins_in_state)
                    # note: timers are in seconds, csv are in minutes
                self.set_timer_current_time(datetime.now() - timedelta(float(outage_dict["mins_in_state"])*60))

                # update total runtime timer
                self.set_timer_current_time(datetime.now() - timedelta(float(outage_dict["mins_total_runtime"])*60))

        # then prep_for_power_outage (delete old csv, make new one), regardles of autorestart
        self.prep_for_power_outage()


    def prep_for_power_outage(self):

        # remove any old outage.csv files, get filename first
        file_path = self.get_power_outage_filename()

        # check if the file exists before attempting to delete
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Old '{file_path}' deleted successfully.")
        else:
            print(f"Old '{file_path}' does not exist.")

        # create a new outage.csv
        #if self.settings["pond_autorestart_after_outage"] == 1:
        self.create_outage_csv_file(self.get_power_outage_filename())
        print(f'New "{self.get_power_outage_filename()}" created for outages')


    def create_outage_csv_file(self, filename):
        
        # define the data to be written to the csv file
        data = [
            ['autostart', self.settings["pond_autorestart_after_outage"]],
            ['config', self.get_config_file_used()],
            ['state', "None"],
            ['mins_in_state', "None"],
            ['mins_total_runtime', "None"],
            ['last_updated', datetime.now()]
        ]

        # Open the file in write mode and create a CSV writer
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write the data to the csv file
            writer.writerows(data)

        #print(f"CSV file '{filename}' updated")
            

    def update_outage_csv(self):    

        # check if the power outage file exists before attempting to add to it
        if os.path.exists(self.get_power_outage_filename()):
            
            data = [
                ['state', self.get_state()],
                ['mins_in_state', round(((datetime.now() - self.get_timer_current_time(self.get_state_name())).total_seconds() / 60), 3)],
                ['mins_total_runtime', round(((datetime.now() - self.get_timer_current_time('program_runtime')).total_seconds() / 60), 3)],
                ['last_updated', datetime.now()]
            ]

            # Path to the CSV file
            csv_file_path = self.get_power_outage_filename()

            # Read existing CSV content
            with open(csv_file_path, 'r', newline='') as file:
                reader = csv.reader(file)
                lines = list(reader)

                # Overwrite data in lines (rows 3, 4, 5 in csv)
                lines[2:6] = data

            # Write updated content back to the CSV file
            with open(csv_file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(lines)

        else: # file does not exist
            return


# kill at the connections the raspberrypi pas
def shutdown_pond(rpi_connections):
    
    # setup the pins again, in order to prevent error messages
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(rpi_connections["red_LED"],GPIO.OUT)
    GPIO.setup(rpi_connections["blue_LED"],GPIO.OUT)
    GPIO.setup(rpi_connections["green_LED"],GPIO.OUT)

    # turn LEDs off
    shutdown_lights(rpi_connections)

    # turn solenoid off
    shutdown_solenoid(rpi_connections)
    
    
def shutdown_lights(rpi_connections):
    GPIO.output(rpi_connections["red_LED"],GPIO.LOW)
    GPIO.output(rpi_connections["blue_LED"],GPIO.LOW)
    GPIO.output(rpi_connections["green_LED"],GPIO.LOW)


def shutdown_solenoid(rpi_connections):
    
    # Setup I2C w/ Relay
    bus = smbus.SMBus(rpi_connections['device_bus'])
    
    # shut solenoid
    bus.write_byte_data(rpi_connections['relay_addr'], rpi_connections['device_bus'], 0x00)
    print("- solenoid closed")

    
# this function is similar to the print() function, except it prints messages with a timestamp in front 
def print_w_time(message):
    
    # Get the current date and time
    current_time = datetime.now()

    # Format the time to include only two decimal places
    formatted_time = current_time.strftime("- %Y-%m-%d %H:%M:%S.%f")[:-5]

    # Combine the formatted time and the message
    result = f"{formatted_time} // {message}"

    # Print the result
    print(result)


def load_config(file_path):
    spec = importlib.util.spec_from_file_location("pond_settings", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.pond_settings_from_file


def csv_to_dict(csv_file):
    result_dict = {}

    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            # Assuming the CSV has at least two columns
            if len(row) >= 2:
                key = row[0]
                value = row[1]
                result_dict[key] = value

    return result_dict