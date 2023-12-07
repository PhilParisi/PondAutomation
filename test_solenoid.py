# this script is for testing the solenoid exclusively
# this script can only be run on a raspberryPi
# keep in mind the solenoid won't flow without a bit of pressure (blowing heavily can simulate flow)
# pay attention to the arrow on the top of the solenoid for the direction of flow

# wiring guide
    # + end from the wall outlet should go into the NC
    # a wire should connect the COM to one of the solenoid terminals
    # GND from the wall outlet should go to the other solenoid terminal 

import time
import smbus


# setup device variables
device_bus = 1 #this is set with the physical switches on the relay, 1 is default)
relay_addr = 0x10 #this is the number of the relay to actuate (0x10, 0x20, 0x30, or 0x40)
bus = smbus.SMBus(device_bus)

# 5 loops of each light
print('turning the solenoid every 5 seconds, sequentially 5 times')
print('observe the flow and see if it matches the outputted text')

try: 
    for i in range(5):
        
        # turn ON (0xFF is 256 max)
        bus.write_byte_data(relay_addr, device_bus, 0xFF)
        print("solenoid open")
    
        # delay
        time.sleep(5)
        
        # turn OFF (0x00 is 0 min)
        bus.write_byte_data(relay_addr, device_bus, 0x00)
        print("solenoid closed")
        
        # delay before next loop
        time.sleep(5)

        
    print("done")

except KeyboardInterrupt:
    print('done')