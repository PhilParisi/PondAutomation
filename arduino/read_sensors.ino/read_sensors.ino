// THIS SCRIPT IS PRODUCTION LEVEL USE. FOR TROUBLESHOOTING INDIVIDUAL SENSORS, USE OTHER .INO SCRIPTS

// Arduino Script to Read Analog Voltages from LiCOR PAR Sensor (and other sensors) and send data to RPi over USB.
// Arduino Mega --> 5V operating voltage, 10 bit resolution (0 to 1023 for A/D converter)

// MESSAGE to RPi STRUCTURE:
  // string data type
  // licor_light_intensity, other_sensor_value, other_sensor_value, ...


// note on data types: keep everything as floats to avoid accidental integer division (rounding errors)


// ARDUINO PARAMETERS

// arduino mega has 5V logic
#define logic_voltage 5.0

// arduino mega has 10bit resolution
#define num_bits 1023.0

// define the built-in LED pin
#define led_pin 13


// LICOR PAR SENSOR PARAMETERS

// define a constant for the LiCOR PAR sensor differential low
#define licor_diff_analog_low A0

// define a constant for the LiCOR PAR sensor differential high
#define licor_diff_analog_high A1

// define the gain (max gain)
#define G 0.375 // this is physically set on the amplifier, our choice
// G = 5V / (I_max * C), then round down (see amplifier guide)

// define calibration constant (can tweak this if needed)
    // for in-air sensor: C = 6.5 to 6.6 to minimize error
#define C 6.6 // uA per 1000umol m^-2 s^-1


// OTHER SENSOR PARAMETERS



// COMMS TO RPI
String msg_over_serial;

// TIMERS (in milliseconds)
unsigned long blink_led_timer;
unsigned long blink_led_interval = 2 * 1000.0; // every 2 second
int blink_led_val;
unsigned long send_data_to_rpi_timer;
unsigned long send_data_to_rpi_interval = 60.0 * 1000.0; // every 60 seconds (1min)


// this runs once
void setup() {

  // start serial communications for debugging on serial monitor
  Serial.begin(9600);

  // set the LED pin as an output
  pinMode(led_pin, OUTPUT);

  // initial values for timing variables
  int blink_led_val = 0;
  blink_led_timer = millis();

  // set initial timer
  send_data_to_rpi_timer = millis();

}

// this runs over and over
void loop() {


  // only read sensors (and send to RPi) at the specified interval
  if (millis() - send_data_to_rpi_timer >= send_data_to_rpi_interval) {
    
    // read all the pins, calculate sensor values
    // compile a message to send over serial
    // send it over serial
    msg_over_serial = "";


    // LICOR  PAR SENSOR

    // read licor analog pins (10bit resolution --> 0 to 1023 values)
    float licor_diff_low = analogRead(licor_diff_analog_low);
    float licor_diff_high = analogRead(licor_diff_analog_high);
    float licor_diff = licor_diff_high - licor_diff_low;

    // calculate original voltage (divide by bits, multiply by 5V logic)
    float licor_voltage = (licor_diff / num_bits) * logic_voltage;

    // calculate voltage multiplier M (must have 1000 in the numerator for the units to work)
    float M = 1000.0 / (G * C); // umol m^-2 s^-1 V^-1

    // convert voltage into light intensity with M
    float licor_light_intensity = licor_voltage * M;

    // add to Licor Data to msg_over_serial
    msg_over_serial = msg_over_serial + String(licor_light_intensity);


    // OTHER SENSOR
    // read pins, calc sensor value
    // msg_over_serial = msg_over_serial + "," + String(other_sensor_value);


    // SEND TO RPi
    // clear the serial buffer before sending new data
    Serial.flush();

    // send fresh values to RPi over serial (also viewable via serial monitor)
    Serial.println(msg_over_serial);

    // reset timer
    send_data_to_rpi_timer = millis();

  }





  // toggle the LED on and off (visual heartbeat on the ino)
  if (millis() - blink_led_timer >= blink_led_interval) {
    if (blink_led_val == 0) {
      digitalWrite(led_pin, HIGH);
      blink_led_val = 1;
    } else {
      digitalWrite(led_pin, LOW);
      blink_led_val = 0;
    }
    blink_led_timer = millis();
  }
      

}
