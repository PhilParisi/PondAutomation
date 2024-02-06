# Raspberry Pi Python Code to Read Serial Data from Arduino

import serial
import time


def read_ino_serial(port='/dev/ttyUSB0', baudrate=9600):
    ser = serial.Serial(port, baudrate)

    for _ in range(3):  # Check the serial port three times
        if ser.in_waiting > 0:
            # Read data from Arduino
            data = ser.readline().decode().strip()

            # Split the received data
            #sensor_data = data.split(',')

            # Process and use the data as needed
            #sensor_value1 = int(sensor_data[0])
            #sensor_value2 = int(sensor_data[1])
            #sensor_value3 = float(sensor_data[2])

            # Print or process the received data
            #print(f"Sensor 1: {sensor_value1}, Sensor 2: {sensor_value2}, Sensor 3: {sensor_value3}")

            # Close the serial port
            ser.close()

            # Return the sensor data string
            return data

        # Wait for a short time before checking again
        time.sleep(0.1)

    # If no data is received after three attempts, close the serial port and return None
    ser.close()
    return None
