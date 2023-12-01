rpi_connections = {

    # these parameters specify the pins used on the RPi board for connections 
    # your physical wiring should match these parameters below
    # we use BCM (which is the GPIOXX), not direct pin number

    # red LED pin [BCM 16 // GPIO16 // pin #36]
    'red_LED':16,

    # yellow LED pin [BCM 20 // GPIO20 // pin #38]
    'yellow_LED':20,

    # green LED pin [BCM 21 // GPIO21 // pin #40]
    'green_LED':21,
    
    # device number - this is set with the physical switches on the relay, 1 is default
    'device_bus':1,
    
    # relay number - this is the number of the relay to actuate (0x10, 0x20, 0x30, or 0x40)
    'relay_addr':0x10 

}