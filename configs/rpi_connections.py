rpi_connections = {

    # these parameters specify the pins used on the RPi board for connections 
    # your physical wiring should match these parameters below
    # we use BCM (which is the GPIOXX), not direct pin number

    # RASPBERRY PI CONNECTIONS
    # red LED pin [BCM 16 // GPIO16 // pin #36]
    'red_LED':16,

    # blue LED pin [BCM 20 // GPIO20 // pin #38]
    'blue_LED':20,

    # green LED pin [BCM 21 // GPIO21 // pin #40]
    'green_LED':21,
    
    # device number - this is set with the physical switches on the relay, 1 is default
    'device_bus':1,
    
    # relay number - this is the number of the relay to actuate (0x10, 0x20, 0x30, or 0x40)
    'relay_addr':0x10,


    # RPI-to-ARDUINO CONNECTION
    # note: the .ino script must be flashed to the arduino separately
        # there are also some parameters in the .ino script that must be set
        # the below parameters relate to the USB connection between the RPi and the Arduino

    # serial port where the RPi sees the Arduino via USB
    'ino_usb_port':'/dev/ttyUSB0',

    # baud rate for the serial connection
    'ino_usb_baudrate':9600

}