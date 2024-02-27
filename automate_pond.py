# Pond Automation Code, v0.1
# to use this script, see the manual at https://github.com/PhilParisi/PondAutomation


# Import the configuration set by the user in the /configs folder as a dictionary
import sys
import os
import csv
import time
import serial
import argparse
import importlib.util
import smbus
import RPi.GPIO as GPIO
from datetime import datetime
from configs.pond_settings import pond_settings_from_file # define the flood/drought params [unused currently]
from configs.rpi_connections import rpi_connections  # define the pins on RPi to use
from functions.pond_functions import *
from arduino.rpi_serial_functions import * # read the arduino serial data

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
    pond.add_timer('drought', pond.get_setting('drought_duration'))
    pond.add_timer('flood', pond.get_setting('flood_duration'))
    pond.add_timer('first_drought', pond.get_setting('minutes_till_first_flood'))
    pond.add_timer('initialization', 0.05)
    pond.add_timer('program_runtime', pond.get_setting('total_program_runtime'))
    pond.add_timer('heartbeat', 30/60) # frequent outputs and logging every 30 seconds
    pond.add_timer('write_data_csv', 20/60) # write to CSV every 20 seconds
    pond.add_timer('close_and_open_new_csv', 4*60) # stop writing to a given csv, start writing to a new one every 4 hours


    # Setup GPIO Pins (RPi pins)
    GPIO.setmode(GPIO.BCM) # set to use the GPIOXX (not the physical pin#)
    GPIO.setwarnings(False)

    GPIO.setup(rpi_connections["red_LED"],GPIO.OUT)
    GPIO.setup(rpi_connections["blue_LED"],GPIO.OUT)
    GPIO.setup(rpi_connections["green_LED"],GPIO.OUT)

    # prep for power outage!
    print('- prep for outage')
    pond.update_pond_with_outage_settings() # won't affect next_state unless autorestart is set in outage.csv
    #pond.set_next_state(0) start off in initialization mode, and pond.set_command(0) is default in Pond class

    # Main Control Loop
    print("\n*** STARTING POND AUTOMATION LOOP ***\n")
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
                
                if pond.get_state5_reset_timer() == True:
                    pond.reset_timer('first_drought')

                pond.set_state5_entry(True)

            # leave state
            
            # timer based
            if (datetime.now() - pond.get_timer_current_time('first_drought')).total_seconds() > pond.get_timer_duration('first_drought'): 

                pond.set_state5_entry(False)
                pond.set_state5_reset_timer(True)
                GPIO.output(rpi_connections["green_LED"],GPIO.LOW) # turn off green light
                pond.set_next_state(20) # go to flood

            # shutdown command
            if pond.get_command() == 'shutdown':

                pond.set_state5_entry(False) # exit state cleanly
                pond.set_state5_reset_timer(True)
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
                
                if pond.get_state10_reset_timer() == True:
                    pond.reset_timer('drought') # update drought timer to current RPi time
                pond.set_state10_entry(True)
                
                GPIO.output(rpi_connections["green_LED"],GPIO.HIGH) # turn green light on

            # leave state

            # timer based
            if (datetime.now() - pond.get_timer_current_time('drought')).total_seconds() > pond.get_timer_duration('drought'):
                
                pond.set_state10_entry(False)
                pond.set_state10_reset_timer(True)
                GPIO.output(rpi_connections["green_LED"],GPIO.LOW) # turn green light off
                pond.set_next_state(20) # go to flood

            # shutdown command
            if pond.get_command() == 'shutdown':

                pond.set_state10_entry(False) # exit state cleanly
                pond.set_state10_reset_timer(True)
                GPIO.output(rpi_connections["green_LED"],GPIO.LOW) # turn green light off
                pond.set_next_state(99) # go to first drought


        # state 20 [flood]
        elif pond.get_state() == 20:

            # do this once
            if pond.get_state20_entry() == False: # get into state

                print_w_time('- entered state 20: flood')
                
                # OPEN the solenoid to begin flow
                bus.write_byte_data(rpi_connections['relay_addr'], rpi_connections['device_bus'], 0xFF)
                print_w_time("- solenoid open")

                if pond.get_state20_reset_timer() == True:
                    pond.reset_timer('flood') # update flood timer to current RPi time
                pond.set_state20_entry(True)
                
                GPIO.output(rpi_connections["blue_LED"],GPIO.HIGH) # turn on blue light
                

            # leave state

            # timer based
            # TODO Song Gao you can add in checking values of sensing data to move between states. Start with the state-transition diagram.
            if (datetime.now() - pond.get_timer_current_time('flood')).total_seconds() > pond.get_timer_duration('flood'):
                             
                GPIO.output(rpi_connections["blue_LED"],GPIO.LOW) # turn off blue light
                pond.set_state20_entry(False)
                pond.set_state20_reset_timer(True)
                pond.set_next_state(10) # go to regular drought

            # shutdown command
            if pond.get_command() == 'shutdown':
                
                GPIO.output(rpi_connections["blue_LED"],GPIO.LOW) # turn off blue light
                pond.set_state20_entry(False) # exit state cleanly
                pond.set_state20_reset_timer(True)
                pond.set_next_state(99) # go to first drought


        # state 99 [shutdown - stop functions and kill script]
        else:

            if pond.get_state99_entry() == False: # get into state

                print_w_time("- entered state 99: shutdown, shutting down system and killing script")

                shutdown_pond(rpi_connections) # turns off lights, closes solenoid
                pond.set_state99_entry(True)
                time.sleep(0.5)
                sys.exit() # kill program


        ######## SYSTEM CHECKS AND UPDATES ########
        
        # update heartbeat timing
        if (datetime.now() - pond.get_timer_current_time('heartbeat')).total_seconds() > pond.get_timer_duration('heartbeat'):
            pond.set_trigger_heartbeat(True) 


        # HEARTBEAT (triggered by time, if the next_state != current_state, after the first loop, other events)
                
        if pond.get_trigger_heartbeat() == True:

            # print heart beat
            print_w_time("- heartbeat (script is still running)")
            pond.reset_timer('heartbeat')

            # update power outage csv with current_state and time_in_state (regardless of autorestart)
            pond.update_outage_csv()

            # set the trigger back to false
            pond.set_trigger_heartbeat(False)


        # update if state just switched (this should happen AFTER the heartbeat functions)
        if (pond.get_state() != pond.get_next_state()):
            pond.set_state_just_switched(True)
            pond.set_trigger_heartbeat(True)
        else:
            pond.set_state_just_switched(False)

                                                   


        #### READ SENSORS (from Arduino) and WRITE TO CSV
        if (datetime.now() - pond.get_timer_current_time('write_data_csv')).total_seconds() > pond.get_timer_duration('write_data_csv'):
                
                # read the arduino serial data
                arduino_data = read_ino_serial(rpi_connections)

                if arduino_data == None:
                    print_w_time("No data received from Arduino")
                else:
                    # update csv with arduino data                
                    amend_dict_to_data_csv(arduino_data, pond.name_for_output_data_file)
                    print_w_time("Arduino data received! Logged to csv.")

                # reset timer
                pond.reset_timer('write_data_csv')


        # change the name (write a new) csv file every X hours            
        if (datetime.now() - pond.get_timer_current_time('close_and_open_new_csv')).total_seconds() > pond.get_timer_duration('close_and_open_new_csv'):

            # update pond sensor data filename, so the next time we go write arduino data it starts a new file
            pond.name_for_output_settings_csv = os.path.join(pond.name_for_output_folder,
                                                        datetime.now().strftime("%d-%b-%Y %H:%M:%S").replace(" ", "_") + "pond_settings_used.csv")

            # reset timer
            pond.reset_timer('close_and_open_new_csv')





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
        #if os.path.exists("configs/outage.csv"):
        #    os.remove("configs/outage.csv")
        #    print_w_time('removed outage.csv')

        print("Pond has been shut down")
        
                
        