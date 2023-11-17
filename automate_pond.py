# Pond Automation Code, v0.1
# to use this script, see the manual at https://github.com/PhilParisi/PondAutomation


# Import the configuration set by the user in the /configs folder as a dictionary
import sys
import os
import csv
import time
from datetime import datetime
from configs.pond_settings import pond_settings_from_file # define the flood/drought params [unused currently]
from configs.rpi_connections import rpi_connections  # define the pins on RPi to use
from functions.pond_functions import *


# Calling the main function
if __name__ == "__main__":


    # System Setup before Control Loop

    print("*** STARTING POND AUTOMATION ***")
    print("- user inputs loaded from configs/pond_settings.py")

    # obtain user inputs, create an instance of the pond class
    pond_settings = get_user_pond_settings()
    pond = Pond(pond_settings)

    # check if the pond settings are correct, kill script if modifications are needed
    print("- see below settings (note: times are in minutes)")
    ask_user_about_settings(pond)

    if pond.get_error_status() == True:
        # the pond has an error, so end script
        print('*** ENDING SCRIPT ***')
        sys.exit()

    # write settings to CSV (create folder, write file)
    create_folder(pond.get_name_for_output_folder())
    write_dict_to_csv(pond.get_settings(), pond.get_name_for_output_settings_csv())
    print("- the pond settings and data are writing to folder:", pond.get_name_for_output_folder())


    # Setup Core Timers
        # TODO one timer controls the rate we write each line to a CSV
        # TODO one timer controls the rate we finish a given CSV and start a new one
        # - one timer counts the drought (and first drought)
        # - one timer tracks the flood
        # times should be in minutes
    
    pond.add_timer('drought', pond.get_setting('drought_duration'))
    pond.add_timer('flood', pond.get_setting('flood_duration'))
    pond.add_timer('first_drought', pond.get_setting('minutes_till_first_flood'))
    pond.add_timer('initialization', 0.05)
    pond.add_timer('program_runtime', pond.get_setting('total_program_runtime'))


    # Main Control Loop
    print("- running script, use CTRL+C to stop execution anytime")
    loop_num = 1
    next_state = 0 # start off in initialization mode (?)
    command = 0 # use this to trigger state transitions

    while (pond.get_error_status() == False):

        # check if it's time to end the program
        if (datetime.now() - pond.get_timer_current_time('program_runtime')).total_seconds() > pond.get_timer_duration('program_runtime'):
            command = 'shutdown' # go to system shutdown

        # update the state variable
        pond.set_state(next_state)


        # Move between states (go to current state)
        
        # state 0 [initialization]
        if pond.get_state() == 0:

            # do this once
            if pond.get_state0_entry() == False: # if not in state, get into it

                # TODO: turn on red light (check state transition diagram)
                # TODO other initial checks??? Need a way to transition out of state
                # TODO SHUT the solenoid and stop flow

                pond.reset_timer('initialization') # update timer to current RPi time
                pond.set_state0_entry(True)
                print('- entered state 0: initialization')

            # leave state

            #if checks are successful, exit the state [for now, 2 seconds]
            if (datetime.now() - pond.get_timer_current_time('initialization')).total_seconds() > pond.get_timer_duration('initialization'):
                # TODO turn light off
                pond.set_state0_entry(False) # exit state cleanly
                next_state = 5 # go to first drought

            # shutdown command
            if command == 'shutdown':
                # TODO turn light off
                pond.set_state0_entry(False) # exit state cleanly
                next_state = 99 # go to first drought

        # state 5 [first drought] 
        elif pond.get_state() == 5: 

            # do this once
            if pond.get_state5_entry() == False: # if not in state, get into it

                # TODO: turn on proper light
                # TODO: SHUT the solenoid and stop flow
                pond.reset_timer('first_drought')
                pond.set_state5_entry(True)
                print('- entered state 5: first drought')

            # leave state
            
            # timer based
            if (datetime.now() - pond.get_timer_current_time('first_drought')).total_seconds() > pond.get_timer_duration('first_drought'): 
                # TODO turn light off
                pond.set_state5_entry(False)
                next_state = 20 # go to flood

            # shutdown command
            if command == 'shutdown':
                # TODO turn light off
                pond.set_state5_entry(False) # exit state cleanly
                next_state = 99 # go to first drought


        # state 10 [drought] 
        elif pond.get_state() == 10: 

            # do this once
            if pond.get_state10_entry() == False: # if not in state, get into it

                # TODO: turn on proper light
                # TODO SHUT the solenoid and stop flow
                pond.reset_timer('drought') # update drought timer to current RPi time
                pond.set_state10_entry(True)
                print('- entered state 10: drought')

            # leave state

            # timer based
            if (datetime.now() - pond.get_timer_current_time('drought')).total_seconds() > pond.get_timer_duration('drought'):
                # TODO turn light off
                pond.set_state10_entry(False)
                next_state = 20 # go to flood

            # shutdown command
            if command == 'shutdown':
                # TODO turn light off
                pond.set_state10_entry(False) # exit state cleanly
                next_state = 99 # go to first drought


        # state 20 [flood]
        elif pond.get_state() == 20:

            # do this once
            if pond.get_state20_entry() == False: # get into state

                # TODO: turn on proper light
                # TODO OPEN the solenoid to begin flow

                pond.reset_timer('flood') # update flood timer to current RPi time
                pond.set_state20_entry(True)
                print('- entered state 20: flood')

            # leave state

            # timer based
            if (datetime.now() - pond.get_timer_current_time('flood')).total_seconds() > pond.get_timer_duration('flood'):
                # TODO turn light off
                pond.set_state20_entry(False)
                next_state = 10 # go to regular drought

            # shutdown command
            if command == 'shutdown':
                # TODO turn light off
                pond.set_state20_entry(False) # exit state cleanly
                next_state = 99 # go to first drought


        # state 99 [shutdown - stop functions and kill script]
        else:

            if pond.get_state99_entry() == False: # get into state

                # TODO: lights all off
                # TODO close solenoid
                
                pond.set_state99_entry(True)
                print("- entered state 99: shutdown, shutting down system and killing script")
                time.sleep(0.5)
                sys.exit() # kill program



        # TODO: write sensor data to csv, based on timer with sampling-freq user input??

        #print("loop: ", loop_num)
        #time.sleep(1)
        #loop_num += 1


        