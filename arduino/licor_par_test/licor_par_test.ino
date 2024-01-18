// Arduino Script to Read Analog Voltages from LiCOR PAR Sensor
  // Arduino Mega --> 5V operating voltage, 10 bit resolution (0 to 1023 for A/D converter)

// Follow this guide https://www.licor.com/env/support/Light-Sensors/topics/2420-quick-start.html



// arduino mega has 5V logic
#define logic_voltage 5

// arduino mega has 10bit resolution
#define num_bits 1023

// define a constant for the LiCOR PAR sensor differential low
#define licor_diff_analog_low A0

// define a constant for the LiCOR PAR sensor differential high
#define licor_diff_analog_high A1

// define the gain (WRONG VALUE)
#define G 0.275 // this is physically set on the amplifier, our choice
  // G = 5V / (I_max * C), then round down (see amplifier guide)

// define calibration constant (WRONG VALUE)
#define C 6.5 // uA per 1000umol m^-2 s^-1



// this runs once
void setup() {

  // start serial communications for debugging on serial monitor
  Serial.begin(9600);

}


// this runs over and over
void loop() {

  // read licor analog pins (10bit resolution --> 0 to 1023 values)
  int licor_diff_low = analogRead(licor_diff_analog_low);
  int licor_diff_high = analogRead(licor_diff_analog_high);
  int licor_diff = licor_diff_high - licor_diff_low;

  // calculate original voltage (divide by bits, multiply by 5V logic)
  int licor_voltage = (licor_diff / num_bits) * logic_voltage;

  // calculate voltage multiplier M
  float M = 1 / (G * C); // umol m^-2 s^-1 V^-1

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


  // one second time delay for readability each loop
  delay(1000);

}
