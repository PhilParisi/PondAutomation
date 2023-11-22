import sys
import os
import csv
from datetime import datetime


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


    # GETTERS and SETTERS
    
    def get_settings(self):
        return self.settings

    def set_settings(self, settings):
        self.settings = settings

    def get_error_status(self):
        return self.has_error

    def set_error_status(self, status):
        self.has_error = status

    def get_pond_state(self):
        return self.pond_state
    
    def set_pond_state(self, state):
        self.pond_state = state

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


    # CONTROL STATE FUNCTIONS

    def get_state(self):
        return self.state
    
    def set_state(self, state):
        self.state = state

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

