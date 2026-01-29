// This script uses an Arduino to control a heater based on temperature readings. 
// It also reads the current and voltage of the heater using an INA219 sensor. 
// Author: Prof. Gordon Hoople

#include <Arduino.h> // Arduino library for basic functions
#include <Wire.h> // Wire library for I2C communication

#include <Adafruit_INA219.h> // Adafruit library for the INA219 current sensor

#include <OneWire.h> // OneWire library for the DS18B20 temperature sensor
#include <DallasTemperature.h> // DallasTemperature library for the DS18B20 temperature sensor

// Pin for the DS18B20 temperature sensor one wire bus. 
#define ONE_WIRE_BUS 4 

// Digital Pin for the heater relay
int heater_pin = 2; // Pin for the heater

// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);

Adafruit_INA219 ina219; // Create an instance of the INA219 class for current sensing
// The Adafruit_INA219 library uses the I2C bus to communicate with the INA219 chip.

const unsigned long SAMPLE_PERIOD = 500;  // Sample period in milliseconds, you can adjust this value.
// You don't need this to be 4 ms like it was for reading accelerometer data.

unsigned long previousMillis = 0;  // Stores the last sampling time

// Variables to hold sensor readings
float shuntvoltage = 0;
float busvoltage = 0;
float current_mA = 0;
float loadvoltage = 0;
float power_mW = 0;
float tempC = 0;

void setup(){
  //Serial Setup
  Serial.begin(115200); // Note the highest recommended serial baud rate for stability is 115200. 

  // Initialize the digital pin for the heater
  pinMode(heater_pin, OUTPUT); 

  // Initialize the INA219.
  // By default the initialization will use the largest range (32V, 2A).
  if (! ina219.begin()) {
    Serial.println("Failed to find INA219 chip");
    while (1) { delay(10); }
  }

  Serial.println("Time (ms), Temperature (C), Shunt Voltage, Bus Voltage (V), Current (mA), Power (mW), Load Voltage (V)");

  // Start up the dallas temperature library
  sensors.begin();

}

void loop() {
  unsigned long currentMillis = millis();
  unsigned long elapsedTime = currentMillis - previousMillis;
  
  // Check if it's time to take a sample
  if (elapsedTime >= SAMPLE_PERIOD) {
  
    // Save the time of this sample
    previousMillis = currentMillis;
    
    // Read the temperature and convert to proper units
    sensors.requestTemperatures(); // Send the command to get temperatures
        
        // Add a small delay to allow sensor to complete reading
        delay(30);

    tempC = sensors.getTempCByIndex(0); // Get the temperature in Celsius from the first sensor on the bus

    // Check if the temperature reading is valid
    bool validTemperature = true;
    if (tempC == DEVICE_DISCONNECTED_C) {
      Serial.println("Error: Temperature sensor disconnected or invalid reading!");
      validTemperature = false; // Mark the temperature as invalid
    }

    // Request data from the INA219 sensor
    shuntvoltage = ina219.getShuntVoltage_mV();
    busvoltage = ina219.getBusVoltage_V();
    current_mA = ina219.getCurrent_mA();
    power_mW = ina219.getPower_mW();
    loadvoltage = busvoltage + (shuntvoltage / 1000);

    // Print out the data
    Serial.print(currentMillis);
    Serial.print(",");
    Serial.print(validTemperature ? tempC : -999); // Use -999 to indicate invalid temperature
    Serial.print(",");
    Serial.print(shuntvoltage);
    Serial.print(",");
    Serial.print(busvoltage);
    Serial.print(",");
    Serial.print(current_mA);
    Serial.print(",");
    Serial.print(power_mW);
    Serial.print(",");
    Serial.println(loadvoltage);

    // Heater control logic only if the temperature is valid
    if (validTemperature) {

      // Complete this heater control control logic

      if () { 

      } 
      else if () { 
        

      }
    }
  }
}
