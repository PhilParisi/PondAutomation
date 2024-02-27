# Raspberry Pi Python Code to Read Serial Data from Arduino
# See message structure being sent in the .ino code

import serial
import time


# return a dictionary 'arduino_data' from the Arduino
def read_ino_serial(rpi_connections):

    # parse arguments
    port = rpi_connections.get('ino_usb_port','/dev/ttyUSB0')
    baudrate = rpi_connections('ino_usb_baudrate','9600')



    ser = serial.Serial(port, baudrate)

    try: 
        for _ in range(3):  # Check the serial port three times
            if ser.in_waiting > 0:

                # Read data from Arduino
                serial_data = ser.readline().decode().strip()

                # Split the received string into a list of strings
                serial_data = serial_data.split(',')

                # Organize into a struct
                arduino_data = {'licor_light_intensity':float(serial_data[0]),
                                'licor_temperature': 0}


                # Close the serial port
                ser.close()

                # Return the sensor data string
                print('Serial data read from Arduino')
                return arduino_data


            # Wait for a short time before checking again
            time.sleep(0.1)


        # if no data received after three attempts, return None
        return None


    except Exception as e:
        print(f"An error occured when opening/closing arduino serial connection: {e}")

    finally:
        # Close the serial port
        ser.close()

