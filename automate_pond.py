# Pond Automation Code, v0.1
# to use this script, see the manual at https://github.com/PhilParisi/PondAutomation


# Import the configuration set by the user in the /configs folder as a dictionary
import sys
import os
import csv
import time
import argparse
import importlib.util
import smbus
import RPi.GPIO as GPIO
from datetime import datetime
from configs.pond_settings import pond_settings_from_file # define the flood/drought params [unused currently]
from configs.rpi_connections import rpi_connections  # define the pins on RPi to use
from functions.pond_functions import *


# define the main function (call it at end of this file)
def main():

    # parse the --config argument (users no longer prompted for inputs)
    parser = argparse.ArgumentParser(description='Automate pond based on configuration file')
    parser.add_argument('--config', help='Path to the configuration file', required=True)
    args = parser.parse_args()

    config_file_path = args.config
    pond_settings_config_style = correct_pond_settings(load_config(config_file_path))


    # System Setup before Control Loop
    print("\n*** STARTING POND AUTOMATION ***\n")
    
    # Setup I2C w/ Relay
    bus = smbus.SMBus(rpi_connections['device_bus'])
    
    # turn OFF solenoid (0x00 is 0 min) [close it --> no flow] (this is a precaution)
    bus.write_byte_data(rpi_connections['relay_addr'], rpi_connections['device_bus'], 0x00)
    print("- solenoid closed")
    

    print("\n*** POND AUTOMATION PARAMETERS ***\n")

    #pond_settings = get_user_pond_settings()
    #pond = Pond(pond_settings_from_file)
    pond = Pond(pond_settings_config_style)
    pond.set_config_file_used(config_file_path)
    print("- user inputs loaded from ", pond.get_config_file_used())
    
    # output pond settings, kill script if modifications are needed
    print("- see below settings (note: times are in minutes)")
    print_pond_settings(pond)
    #ask_user_about_settings(pond)

    if pond.get_error_status() == True:
        # the pond has an error, so end script
        print('\n*** ENDING SCRIPT ***\n')
        sys.exit()

    # write settings to CSV (create folder, write file)
    create_folder(pond.get_name_for_output_folder())
    write_dict_to_csv(pond.get_settings(), pond.get_name_for_output_settings_csv())
    print("- the pond settings and data are writing to folder:", pond.get_name_for_output_folder())


    # Setup Core Timers
        # TODO one timer controls the rate we write each line to a CSV
        # TODO one timer controls the rate we finish a given CSV and start a new one
        # times should be in minutes
    
    pond.add_timer('drought', pond.get_setting('drought_duration'))
    pond.add_timer('flood', pond.get_setting('flood_duration'))
    pond.add_timer('first_drought', pond.get_setting('minutes_till_first_flood'))
    pond.add_timer('initialization', 0.05)
    pond.add_timer('program_runtime', pond.get_setting('total_program_runtime'))
    pond.add_timer('heartbeat', 0.5) # frequent outputs and logging

    # Setup GPIO Pins (RPi pins)
    GPIO.setmode(GPIO.BCM) # set to use the GPIOXX (not the physical pin#)
    GPIO.setwarnings(False)

    GPIO.setup(rpi_connections["red_LED"],GPIO.OUT)
    GPIO.setup(rpi_connections["blue_LED"],GPIO.OUT)
    GPIO.setup(rpi_connections["green_LED"],GPIO.OUT)


    # Main Control Loop
    print("\n*** STARTING POND AUTOMATION LOOP ***\n")

    # prep for power outage!
    print('- prep for outage')
    pond.update_pond_with_outage_settings() # won't affect next_state unless autorestart is set in outage.csv
    #pond.set_next_state(0) start off in initialization mode, and pond.set_command(0) are default in Pond class

    print("- running loop, use CTRL+C to stop execution anytime")
    while (pond.get_error_status() == False):

        # check if it's time to end the program
        if (datetime.now() - pond.get_timer_current_time('program_runtime')).total_seconds() > pond.get_timer_duration('program_runtime'):
            pond.set_command('shutdown') # go to system shutdown

        # update the state variable
        pond.set_state(pond.get_next_state())


        # Move between states (go to current state)
        
        # state 0 [initialization]
        if pond.get_state() == 0:

            # do this once
            if pond.get_state0_entry() == False: # if not in state, get into it

                print_w_time('- entered state 0: initialization')
                
                # turn on all lights
                GPIO.output(rpi_connections["red_LED"],GPIO.HIGH)
                GPIO.output(rpi_connections["blue_LED"],GPIO.HIGH)
                GPIO.output(rpi_connections["green_LED"],GPIO.HIGH)
                
                # TODO other initial checks??? Need a way to transition out of state
                
                # SHUT the solenoid and stop flow
                bus.write_byte_data(rpi_connections['relay_addr'], rpi_connections['device_bus'], 0x00)
                print_w_time("- solenoid closed")

                pond.reset_timer('initialization') # update timer to current RPi time
                pond.set_state0_entry(True)

            # leave state

            #if checks are successful, exit the state [for now, 2 seconds]
            if (datetime.now() - pond.get_timer_current_time('initialization')).total_seconds() > pond.get_timer_duration('initialization'):
                
                # turn lights off
                GPIO.output(rpi_connections["red_LED"],GPIO.LOW)
                GPIO.output(rpi_connections["blue_LED"],GPIO.LOW)
                GPIO.output(rpi_connections["green_LED"],GPIO.LOW)
                
                pond.set_state0_entry(False) # exit state cleanly
                pond.set_next_state(5) # go to first drought

            # shutdown command
            if pond.get_command() == 'shutdown':
                
                # turn lights off
                GPIO.output(rpi_connections["red_LED"],GPIO.LOW)
                GPIO.output(rpi_connections["blue_LED"],GPIO.LOW)
                GPIO.output(rpi_connections["green_LED"],GPIO.LOW)
                
                pond.set_state0_entry(False) # exit state cleanly
                pond.set_next_state(99) # go to first drought

        # state 5 [first drought] 
        elif pond.get_state() == 5: 

            # do this once
            if pond.get_state5_entry() == False: # if not in state, get into it
                    
                print_w_time('- entered state 5: first drought')
                
                # shut solenoid
                bus.write_byte_data(rpi_connections['relay_addr'], rpi_connections['device_bus'], 0x00)
                print_w_time("- solenoid closed")
                
                pond.reset_timer('first_drought')
                pond.set_state5_entry(True)

            # leave state
            
            # timer based
            if (datetime.now() - pond.get_timer_current_time('first_drought')).total_seconds() > pond.get_timer_duration('first_drought'): 

                pond.set_state5_entry(False)
                GPIO.output(rpi_connections["green_LED"],GPIO.LOW) # turn off green light
                pond.set_next_state(20) # go to flood

            # shutdown command
            if pond.get_command() == 'shutdown':

                pond.set_state5_entry(False) # exit state cleanly
                GPIO.output(rpi_connections["green_LED"],GPIO.LOW) # turn off green light
                pond.set_next_state(99) # go to first drought


        # state 10 [drought] 
        elif pond.get_state() == 10: 

            # do this once
            if pond.get_state10_entry() == False: # if not in state, get into it

                print_w_time('- entered state 10: drought')

                # shut solenoid
                bus.write_byte_data(rpi_connections['relay_addr'], rpi_connections['device_bus'], 0x00)
                print_w_time("- solenoid closed")
                
                pond.reset_timer('drought') # update drought timer to current RPi time
                pond.set_state10_entry(True)
                
                GPIO.output(rpi_connections["green_LED"],GPIO.HIGH) # turn green light on

            # leave state

            # timer based
            if (datetime.now() - pond.get_timer_current_time('drought')).total_seconds() > pond.get_timer_duration('drought'):
                
                pond.set_state10_entry(False)
                GPIO.output(rpi_connections["green_LED"],GPIO.LOW) # turn green light off
                pond.set_next_state(20) # go to flood

            # shutdown command
            if pond.get_command() == 'shutdown':

                GPIO.output(rpi_connections["green_LED"],GPIO.LOW) # turn green light off
                pond.set_state10_entry(False) # exit state cleanly
                pond.set_next_state(99) # go to first drought


        # state 20 [flood]
        elif pond.get_state() == 20:

            # do this once
            if pond.get_state20_entry() == False: # get into state

                print_w_time('- entered state 20: flood')
                
                # OPEN the solenoid to begin flow
                bus.write_byte_data(rpi_connections['relay_addr'], rpi_connections['device_bus'], 0xFF)
                print_w_time("- solenoid open")

                pond.reset_timer('flood') # update flood timer to current RPi time
                pond.set_state20_entry(True)
                
                GPIO.output(rpi_connections["blue_LED"],GPIO.HIGH) # turn on blue light
                

            # leave state

            # timer based
            if (datetime.now() - pond.get_timer_current_time('flood')).total_seconds() > pond.get_timer_duration('flood'):
                
                # shut solenoid
                #bus.write_byte_data(rpi_connections['relay_addr'], rpi_connections['device_bus'], 0x00)
                #print_w_time("- solenoid closed")
                
                GPIO.output(rpi_connections["blue_LED"],GPIO.LOW) # turn off blue light
                pond.set_state20_entry(False)
                pond.set_next_state(10) # go to regular drought

            # shutdown command
            if pond.get_command() == 'shutdown':
                
                GPIO.output(rpi_connections["blue_LED"],GPIO.LOW) # turn off blue light
                pond.set_state20_entry(False) # exit state cleanly
                pond.set_next_state(99) # go to first drought


        # state 99 [shutdown - stop functions and kill script]
        else:

            if pond.get_state99_entry() == False: # get into state

                print_w_time("- entered state 99: shutdown, shutting down system and killing script")

                shutdown_pond(rpi_connections) # turns off lights, closes solenoid
                pond.set_state99_entry(True)
                time.sleep(0.5)
                sys.exit() # kill program



        # HEARTBEAT (triggered by time or if the next_state != current_state)
                
        if (datetime.now() - pond.get_timer_current_time('heartbeat')).total_seconds() > pond.get_timer_duration('heartbeat') or pond.get_state_just_switched() == 1:
            
            # print heart beat
            print_w_time("- heartbeat (script is still running)")
            pond.reset_timer('heartbeat')

            # update power outage csv with current_state and time_in_state (regardless of autorestart)
            pond.update_outage_csv()


        # update if state just switched
        if (pond.get_state() != pond.get_next_state()):
            pond.set_state_just_switched(1)
        else:
            pond.set_state_just_switched(0)


        # TODO: write sensor data to csv, based on timer with sampling-freq user input??




# wrap everything in a keyboard interrupt exception
if __name__ == "__main__":
    try:
        main() # run the above script
        
    except KeyboardInterrupt:
        print_w_time("\nUser shut down program with CTRL+C")
            
    finally: # clean up code

        # turn off all the electronic components
        shutdown_pond(rpi_connections)

        # remove outage.csv file, so next time we run we start fresh
        # why remove? because a human is ending the program, which means a human has to start a new one
        if os.path.exists("configs/outage.csv"):
            os.remove("configs/outage.csv")
            print_w_time('removed outage.csv')

        print("Pond has been shut down")
        
                
        