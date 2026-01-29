/*
 * Arduino Strain Data Acquisition
 * 
 * This is a data acquisition script designed for measuring strain data with
 * an Arduino and the Adafruit HX711 load cell amplifier. It will also collect
 * data from analog pin A0, though you may not need this information.
 * 
 * It uses non-blocking code to sample at a mostly consistent rate with microsecond timing,
 * it appears to have 4 microseconds of variability in the sample period. You should check this
 * for yourself.
 * 
 * The micros() timer resets after about 1 hour, so don't collect data with this script for more than an hour.
 * 
 * Data Output Format:
 * timestamp_micros,interval_micros,strain,sensorValue0
 * timestamp_micros is the time in microseconds since the Arduino started.
 * interval_micros is the time in microseconds since the last sample.
 * strain is the raw output from the HX711's 24 bit ADC and has values 0 -> 2^24-1.
 * sensorValue0 is the raw output from the Arduino's 10 bit ADC and has values 0-1023.
 * 
 * You must install the Adafruit HX711 library to use this sketch.
 * 
 * Make sure the switch on you HX711 is set to H (80 SPS) to get the maximum data acquisition rate.
 * 
 * Author: Prof. Gordon Hoople
 */

#include <Arduino.h>
#include <Adafruit_HX711.h>

// Define the pins for the HX711 communication
const uint8_t DATA_PIN = 2;  // Must be a pin that can handle interrupts!
const uint8_t CLOCK_PIN = 3; 
Adafruit_HX711 hx711(DATA_PIN, CLOCK_PIN);

// Define Sample Period in microseconds
const unsigned long SAMPLE_PERIOD = 12500; // Target 12.5ms = 80 Hz based on data sheet. 
// When set to 12500, actual period observed to be either exactly 12.5 ms or 12.5ms +4uS 

// Setup timing variables with microsecond precision
unsigned long previousMicros = 0;  // Stores the last sampling time in microseconds
unsigned long currentMicros = 0;   // Current time in microseconds
unsigned long intervalMicros = 0;  // Interval between readings in microseconds

// Interrupt flags
volatile boolean newDataReady = false;

// Interrupt routine: Sets flag when HX711 has new data available
void dataReadyISR() {
    newDataReady = true;
}

void setup() {
  // Serial Communication Setup
  Serial.begin(115200); // Note the highest recommended serial baud rate for stability is 115200.
  Serial.println("Times (us),interval (us),strain (raw),sensorValue0 (raw)"); // Print header for data
  // Initialize the HX711
  hx711.begin();

  // Attach interrupt for HX711 data ready (DOUT goes LOW)
  attachInterrupt(digitalPinToInterrupt(DATA_PIN), dataReadyISR, FALLING);
}

void loop() {
  currentMicros = micros(); // Get current microsecond timestamp

  // Check if new data is ready and minimum interval has passed
  if (newDataReady && (currentMicros - previousMicros) >= SAMPLE_PERIOD) {
    // Calculate interval since last reading
    intervalMicros = currentMicros - previousMicros;
    
    // Update previous time
    previousMicros = currentMicros;

    // Get the raw strain value
    int32_t strain = hx711.readChannelRaw(CHAN_A_GAIN_128);
    newDataReady = false;
   
    // Get the analog data (you can comment this out if you don't want it)
    int sensorValue0 = analogRead(A0);

    // Output the data
    Serial.print(currentMicros);
    Serial.print(",");
    Serial.print(intervalMicros);
    Serial.print(",");
    Serial.print(strain);
    Serial.print(",");
    Serial.println(sensorValue0);
  }
}