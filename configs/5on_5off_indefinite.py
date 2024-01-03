pond_settings_from_file = {

    # note: we are assuming no internet connection, so everything is based off the relative RPi clock time (not global/correct time)

    # minutes until the first flood (decimals are acceptable)
    'minutes_till_first_flood':0,

    # the 'flood duration' (in MINUTES) that the solenoid valve is OPEN and water FLOWS
    'flood_duration':5,

    # the 'drought duration' (in MINUTES) that the solenoid valve is CLOSED and NO flow
    'drought_duration':5,

    # the 'total_program_runtime' (in MINUTES) kills the program after this duration (use 0 for infinite runtime)
    'total_program_runtime':0,

    # would you like the pond to automatically start back up after being powered off? good idea if you expect power outages
    # 1 means 'yes', 0 means 'no'
    'pond_autorestart_after_outage':0

}