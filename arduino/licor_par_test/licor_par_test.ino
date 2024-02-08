// THIS SCRIPT IS FOR TROUBLESHOOTING ONLY. FLASH THE OTHER SCRIPT FOR PRODUCTION LEVEL USE.
    // for testing, flash this and open the serial monitor. confirm the values you see with a light meter.

// Arduino Script to Read Analog Voltages from LiCOR PAR Sensor
// Arduino Mega --> 5V operating voltage, 10 bit resolution (0 to 1023 for A/D converter)
// Follow this guide https://www.licor.com/env/support/Light-Sensors/topics/2420-quick-start.html

// note on data types: keep everything as floats to avoid accidental integer division (rounding errors)

// arduino mega has 5V logic
#define logic_voltage 5.0

// arduino mega has 10bit resolution
#define num_bits 1023.0

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

// define the built-in LED pinß
#define led_pin 13

// this runs once
void setup() {
  // start serial communications for debugging on serial monitor
  Serial.begin(9600);

  // set the LED pin as an output
  pinMode(led_pin, OUTPUT);
}

// this runs over and over
void loop() {
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

  // print values to serial console
  Serial.print("licor low A0: ");
  Serial.println(licor_diff_low);
  Serial.print("licor high A1: ");
  Serial.println(licor_diff_high);

  Serial.print("licor diff analog values: ");
  Serial.println(licor_diff);
  Serial.print("licor diff voltage: ");
  Serial.println(licor_voltage);

  Serial.print("voltage multiplier M: ");
  Serial.println(M);
  Serial.print("licor light intensity: ");
  Serial.println(licor_light_intensity);

  Serial.println("*******************");


  delay(500);

}
