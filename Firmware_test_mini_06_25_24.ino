// Library for I2C Wire Transfer
#include <Wire.h>

// Simple library for Debounce logic on buttons
#include <Bounce2.h>

// ALL PIN addresses and registers should be #define . This makes it easier in a global sense and it will use less memory.
// constexpre could potentially work. However it is a newer feature and I am not sure if that is supported in arduino
// Use Arduino Pro or Pro Mini

// Values for register addresses
#define AD5242_1 0b0101100
#define AD5242_2 0b0101101       // digital pot #2
#define LTC2990_1 0b1001100      // voltmeter #1
#define LTC2990_2 0b1001101      // voltmeter #2
#define LTC2990_GLOBAL 0b1110111 // The global setup address for all LTC2990 devices on the buss

// LED for Go and Stop Buttons
#define STOP_LED 3
#define GO_LED 4

// Leds Channels. One for green LED and One for RED Set by Jesus Not me
// Module 1
#define M1_RED_LED 11
#define M1_GREEN_LED 12

// Module 2
#define M2_RED_LED 9
#define M2_GREEN_LED 10

// Module 3
#define M3_RED_LED 7
#define M3_GREEN_LED 8

// Module 4
#define M4_RED_LED 5
#define M4_GREEN_LED 6

// Button Input Pins
#define STOP_BTN 14
#define GO_BTN 15

// Latch Pin and Num Channels Gobal Varibles
#define LATCH 2
#define NUMCHANNELS 4
#define NUMTESTS 72
#define NUMSAMPLES 100

// An array that is filled with the number value of LEDS
const int redLeds[NUMCHANNELS] = {M1_RED_LED, M2_RED_LED, M3_RED_LED, M4_RED_LED};
const int greenLeds[NUMCHANNELS] = {M1_GREEN_LED, M2_GREEN_LED, M3_GREEN_LED, M4_GREEN_LED};

// Resistance step values for the digital pot - 250,231,228,225,222,216,212,208.  Increases HV voltage in 25V increments up to 200V
// const byte AD5242_Res_Set[NUMTESTS] = {250, 231, 228, 225, 222, 216, 212, 208};
// const float correct_high_value[NUMTESTS] = {4.95, 4.90, 4.80, 2.85, 2.50, 1.70, 1.45, 1.1}; // the upper threshold values for verification of the device
// const float correct_low_value[NUMTESTS] = {3.90, 2.00, 1.80, 1.30, 1.15, 0.70, 0.55, 0.45}; // the lower threshold values for verification of the device
float midpoint[NUMTESTS];

// store the binary values read from the LTC2990
byte module_optical_voltage_data_MSB[NUMCHANNELS][NUMTESTS];
byte module_optical_voltage_data_LSB[NUMCHANNELS][NUMTESTS];
byte module_EL_Voltage_data_MSB[NUMCHANNELS][NUMTESTS];
byte module_EL_Voltage_data_LSB[NUMCHANNELS][NUMTESTS];
float module_optical_voltage_numeric[NUMCHANNELS][NUMTESTS];
float module_EL_Voltage_numeric[NUMCHANNELS][NUMTESTS];

// Array to get channel and test number from the serial Out.
const String numToString[NUMCHANNELS] = {"C1:", "C2:", "C3:", "C4:"};
//const String testToString[NUMTESTS] = {"S", "T", "U", "V", "W", "X", "Y", "Z"};
unsigned int channelFails[NUMCHANNELS] = {0, 0, 0, 0};

// Create button debounce object.
Bounce2::Button GoButton = Bounce2::Button();
Bounce2::Button StopButton = Bounce2::Button();

// Varibles for flashing LED logic.
unsigned long previousMillis;
int isFlashing = LOW;
const int interval = 1;

unsigned int numFailed = 0;

// Truth Table. TODO: Delete
bool isSlew = false;
bool isActive = false;

// Simple Intro Sequence when starting up Module. Made by Jesus.
// I made this a lot shorter bc it was really annoying flashing through this everytime the device is reflashed
void printIntro(int length)
{
  // a little showing off
  digitalWrite(5, 1);
  digitalWrite(7, 1);
  digitalWrite(9, 1);
  digitalWrite(11, 1);
  digitalWrite(6, 0);
  digitalWrite(8, 0);
  digitalWrite(10, 0);
  digitalWrite(12, 0);
  latch_pulse();
  delay(length);
  digitalWrite(5, 0);
  digitalWrite(7, 0);
  digitalWrite(9, 0);
  digitalWrite(11, 0);
  digitalWrite(6, 1);
  digitalWrite(8, 1);
  digitalWrite(10, 1);
  digitalWrite(12, 1);
  latch_pulse();
  delay(length);
  digitalWrite(5, 1);
  digitalWrite(7, 1);
  digitalWrite(9, 1);
  digitalWrite(11, 1);
  digitalWrite(6, 1);
  digitalWrite(8, 1);
  digitalWrite(10, 1);
  digitalWrite(12, 1);
  latch_pulse();
  delay(length);
  digitalWrite(5, 0);
  digitalWrite(7, 0);
  digitalWrite(9, 0);
  digitalWrite(11, 0);
  digitalWrite(6, 0);
  digitalWrite(8, 0);
  digitalWrite(10, 0);
  digitalWrite(12, 0);
  latch_pulse();
}

// Sets ths resistance of Each Register to thew same value.
// By default it sets it the highest value.
void setDefaultResistance(byte resistance = 0xFF)
{
  Wire.beginTransmission(AD5242_1);
  Wire.write(0x00);
  Wire.write(resistance);
  Wire.endTransmission();
  Wire.beginTransmission(AD5242_1);
  Wire.write(0x80);
  Wire.write(resistance);
  Wire.endTransmission();
  Wire.beginTransmission(AD5242_2);
  Wire.write(0x00);
  Wire.write(resistance);
  Wire.endTransmission();
  Wire.beginTransmission(AD5242_2);
  Wire.write(0x80);
  Wire.write(resistance);
  Wire.endTransmission();
}

// Allows you set your own resistance values.
// Used during tests
void setGlobalResistance(byte resistance)
{
  Wire.beginTransmission(AD5242_1);
  Wire.write(0x18);
  Wire.write(resistance);
  Wire.endTransmission();
  Wire.beginTransmission(AD5242_1);
  Wire.write(0x98);
  Wire.write(resistance);
  Wire.endTransmission();
  Wire.beginTransmission(AD5242_2);
  Wire.write(0x18);
  Wire.write(resistance);
  Wire.endTransmission();
  Wire.beginTransmission(AD5242_2);
  Wire.write(0x98);
  Wire.write(resistance);
  Wire.endTransmission();
}

// Automatically give state to blink LEDS.
// Returns HIGH if LEDS should be on and LOW if they should be off.
int blinkLed()
{
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval)
  {
    // save the last time you blinked the LED
    previousMillis = currentMillis;

    // if the LED is off turn it on and vice-versa:
    if (isFlashing == LOW)
    {
      isFlashing = HIGH;
    }
    else
    {
      isFlashing = LOW;
    }
  }

  return isFlashing;
}

// Takes info from ampmeter and puts them into an array.
/* TODO: this is bad. If used out of order then the wrong data can be recived.
Figure out how the amp meter works so that each channel can be called up indivdually -Holland */
void getChannelInfo(const unsigned int channel, const unsigned int currentTest)
{
  // Get Optical Data
  module_optical_voltage_data_MSB[channel][currentTest] = Wire.read();
  module_optical_voltage_data_LSB[channel][currentTest] = Wire.read();

  // Get EL Data
  module_EL_Voltage_data_MSB[channel][currentTest] = Wire.read();
  module_EL_Voltage_data_LSB[channel][currentTest] = Wire.read();
}

// this takes the data read from the LTC2990 and converts it to a voltage value.
// Created by Jesus Ortiz
float calculate_voltage(const unsigned int channel, const unsigned int testNum)
{
  byte MSB = module_optical_voltage_data_MSB[channel][testNum];
  byte LSB = module_optical_voltage_data_LSB[channel][testNum];
  word input_data_word = 0x0000; // combine the high and low bytes to make the single data word
  float calculated_voltage;
  bool sign_bit = 0;
  // word bit_mask = 0b0111111111111111;
  float input_data_numeric;

  sign_bit = bitRead(MSB, 6); // read the sign value bit for the signed binary value

  bitWrite(MSB, 7, 0);
  bitWrite(MSB, 6, 0);

  // I don't get why it is done this way. This should be one line -Holland
  input_data_word = MSB;
  input_data_word = input_data_word * 256;
  input_data_word = input_data_word + LSB;
  input_data_numeric = (float)input_data_word; // convert the binary data to an integer for the calculation

  if (sign_bit == 0b1)
  {
    calculated_voltage = ((input_data_numeric + 1.00) * -0.00030518);
  }
  else if (sign_bit == 0b0)
  {
    calculated_voltage = (input_data_numeric * 0.00030518);
  }
  // delay(50);
  return calculated_voltage;
}

// Set all Leds to be a certain color
void setLeds(int redState, int greenState)
{
  for (int i = 0; i < 4; i++)
  {
    latch_pulse();
    digitalWrite(greenLeds[i], greenState);
    latch_pulse();
    digitalWrite(redLeds[i], redState);
  }
}

// Set a single Led State
// void setLeds(int channel, bool state)
// {
//   latch_pulse();
//   digitalWrite(channel, state);
// }

// Needed whenever an LED state is changed. Needed for the IC that is being used to drive the LEDS
void latch_pulse()
{
  digitalWrite(LATCH, false);
  delayMicroseconds(100);
  digitalWrite(LATCH, true);
  delayMicroseconds(100);
}

// Creates a percentage based off of two points.
// Useed for Debugging
inline float percentDiff(float in1, float in2)
{
  const float diff = in1 - in2;
  const float avrg = (in1 + in2) / 2.0f;
  return (diff / avrg) * 100.0f;
}

// Goes through each channel and gets the current voltage and prints it to the serial output.
// Outputs an average of valuues based of off NUMSAMPLES
void getChannelVoltage(int currentTest)
{
  float output[NUMCHANNELS] = {0.0f, 0.0f, 0.0f, 0.0f};
  for (int n = 0; n < NUMSAMPLES; n++)
  {

    // delayMicroseconds(100);

    // Get info from amp meter
    Wire.beginTransmission(LTC2990_1);
    Wire.write(0x06); // Move the register pointer to 0x06
    Wire.endTransmission();
    // delayMicroseconds(100);
    Wire.requestFrom(LTC2990_1, 8, 1);

    // Get Data
    getChannelInfo(0, currentTest);
    getChannelInfo(1, currentTest);

    Wire.beginTransmission(LTC2990_2);
    Wire.write(0x06); // Move the register pointer to 0x06
    Wire.endTransmission();
    // delayMicroseconds(100);
    Wire.requestFrom(LTC2990_2, 8, 1);

    // Get Data
    getChannelInfo(2, currentTest);
    getChannelInfo(3, currentTest);

    // Not going to use a for loops to conserve memory. If we ever have more than 4 channels then the option is there.
    output[0] += calculate_voltage(0, currentTest);
    output[1] += calculate_voltage(1, currentTest);
    output[2] += calculate_voltage(2, currentTest);
    output[3] += calculate_voltage(3, currentTest);
    delay(1);
  }
  
  // Tell the Script there is a new Line
  Serial.print("B1:1,");

  // Take all of the volatages generated from the device and print out the average to the serial Monitor
  for (int x = 0; x < NUMCHANNELS; x++)
  {
    // Get the Average
    output[x] = output[x] / float(NUMSAMPLES);
    Serial.print(numToString[x]);
    Serial.print(output[x]);
    // if (output[x] >= correct_low_value[currentTest] && output[x] <= correct_high_value[currentTest]){
    //   Serial.print(numToString[x]);
    //   Serial.print(output[x]);
    //   //Serial.print("0");
    // }
    // else {
    //   Serial.print(numToString[x]);
    //   Serial.print(output[x]);
    //   //Serial.print("1");
    //   //Serial.print(",");
    //   channelFails[x] += 1;
    // }

    Serial.print(",");
    // if (x != NUMCHANNELS - 1){
    //   Serial.print(",");

    // }
    // Serial.print(numToString[x]);
    // Serial.print(output[x]);
    // Serial.print(" ");
    // Serial.print(percentDiff(output[x], midpoint[currentTest]));
  }

  // Tell the script that the line is Over
  Serial.print("B1:0");
  Serial.println("");


}

// Go through the next test by  slowing decreasing the resistance on the IC
// If you DO NOT go slowly it will be inclined to glich.
void nextTest(int currentTest)
{
  // Make into its own function
  isSlew = true;

  setLeds(HIGH, HIGH);
  // setGlobalResistance(220 - currentTest);
  // delay(interval);
  // setLeds(HIGH, LOW);
  // setGlobalResistance(240 - currentTest);
  delay(interval);
  setLeds(LOW, HIGH);
  setGlobalResistance(250 - currentTest);
  //delay(interval);
  setLeds(LOW, LOW);
  isSlew = false;
  isActive = true;

  // currentTest++;
}

// Main Function. Does this first and then Loops
void setup()
{
  // Set Pins
  pinMode(STOP_LED, OUTPUT);     // The STOP button LED
  pinMode(GO_LED, OUTPUT);       // The GO button LED
  pinMode(M4_RED_LED, OUTPUT);   // Module 4 RED  - the module fails
  pinMode(M4_GREEN_LED, OUTPUT); // Module 4 GREEN  - the module passes
  pinMode(M3_RED_LED, OUTPUT);   // Module 3 RED  - the module fails
  pinMode(M3_GREEN_LED, OUTPUT); // Module 3 GREEN  - the module passes
  pinMode(M2_RED_LED, OUTPUT);   // Module 2 RED  - the module fails
  pinMode(M2_GREEN_LED, OUTPUT); // Module 2 GREEN  - the module passes
  pinMode(M1_RED_LED, OUTPUT);   // Module 1 RED  - the module fails
  pinMode(M1_GREEN_LED, OUTPUT); // Module 1 GREEN  - the module passes
  pinMode(LATCH, OUTPUT);        // The Latch Pulse for the TI buffers. ?
  pinMode(STOP_BTN, INPUT);      // The STOP button
  pinMode(GO_BTN, INPUT);        // The GO button

  // Init Button Objects
  GoButton.attach(GO_BTN);
  StopButton.attach(STOP_BTN);
  GoButton.setPressedState(HIGH);
  StopButton.setPressedState(HIGH);

  // Set Refresh Interval
  GoButton.interval(50);
  StopButton.interval(50);

  // Calculates the Midpoint between the low and high values. Could be done at compile time.
  // for (int i = 0; i < NUMTESTS; i++)
  // {
  //   midpoint[i] = (correct_high_value[i] + correct_low_value[i]) / 2.0f;
  // }

  // Start
  Wire.begin();
  Serial.begin(9600); // set baud rate
  setDefaultResistance(0xFF);

  // setup voltage sensor using global address
  Wire.beginTransmission(LTC2990_GLOBAL);
  Wire.write(0x01); // point Control register
  Wire.write(0x1F); // voltage mode
  Wire.write(0x02); // point Trigger
  Wire.write(0xFF); // write to Trigger
  Wire.endTransmission();

  // Moved the Code into function because it was very long
  printIntro(100);
}


bool startTest = false;

// Main loop
void loop()
{
  // Checks if either button is being pressed
  GoButton.update();
  StopButton.update();

  startTest = GoButton.pressed();

    if (Serial.available() > 0) {
    // Read the incoming data as a string
    String command = Serial.readStringUntil('\n');

    // Remove any whitespace characters (e.g., newlines, carriage returns)
    command.trim();

    // Check the command and act accordingly
    if (command == "Start") {
      startTest = true;
    } else if (command == "Stop") {
    }
  }

  // Figure out if the blinking LEDS are either on or off
  int GlobalLedState = blinkLed();
  //  int GlobalLedState = HIGH;

  // set the LED with the ledState of the variable:
  latch_pulse();
  digitalWrite(STOP_LED, StopButton.isPressed());
  // digitalWrite(GO_LED, GlobalLedState);

  // TODO: Delete this function. Make the stop button actually stop the test
  if (StopButton.pressed())
  {
    setLeds(LOW, LOW);
    // getChannelVoltage();
  }
  // If the button is not pressed it will just go through the Blink animation as normal
  else
  {
    for (int i = 0; i < NUMCHANNELS; i++)
    {
      latch_pulse();
      digitalWrite(greenLeds[i], LOW);
      digitalWrite(redLeds[i], GlobalLedState);
    }
  }

  // If the Go button gets pressed and the stop button is not pressed the go through all the tests
  if ((startTest && !StopButton.isPressed()))
  {
    Serial.println("A1:1");
    for (int t = 0; t < NUMTESTS; t++)
    {
      nextTest(t);
      getChannelVoltage(t);
      // getChannelVoltage(t);
      // getChannelVoltage(t);
    }
    Serial.println("A1:0");

    // Reset Samples
    for (int x = 0; x < NUMCHANNELS; x++){
      channelFails[x] = 0;
      numFailed = 0;
    }

    setDefaultResistance(0xFF);
    startTest = false;
  }
  // If both are pressed the increase the volatage to max
  // TODO: Delete
  else if (GoButton.pressed() && StopButton.isPressed())
  {
    setDefaultResistance(0xFF);
    isActive = false;
  }
}
