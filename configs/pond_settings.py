pond_settings_from_file = {

    # note: we are assuming no internet connection, so everything is based off the relative RPi clock time (not global/correct time)

    # minutes until the first flood (decimals are acceptable)
    'minutes_till_first_flood':0.25,

    # the 'flood duration' (in MINUTES) that the solenoid valve is OPEN and water FLOWS
    'flood_duration':10,

    # the 'drought duration' (in MINUTES) that the solenoid valve is CLOSED and NO flow
    'drought_duration':50,

    # the 'total_program_runtime' (in MINUTES) kills the program after this duration
    'total_program_runtime':60*24*4

}