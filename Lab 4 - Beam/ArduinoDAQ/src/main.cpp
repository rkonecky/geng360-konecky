// This is a data acquisition script for the Arduino.
// It uses non-blocking code to sample the analog pins at a consistent rate.
// You should test the script with your hardware to determine the smallest stable sample interval.

// Author: Prof. Gordon Hoople

#include <Arduino.h>

const unsigned long SAMPLE_PERIOD = 500;  // Sample period in milliseconds, you can adjust this value.

unsigned long previousMillis = 0;  // Stores the last sampling time
bool firstSample = true;          // Flag for first sample

void setup(){
  //Serial Setup
  Serial.begin(115200); // Note the highest recommended serial baud rate for stability is 115200. 
  Serial.println("Time (ms),Sensor 0 (raw),Sensor 1 (raw),Sensor 2 (raw)"); // Print header for data
}

void loop() {
  unsigned long currentMillis = millis();
  unsigned long elapsedTime = currentMillis - previousMillis;
  
  // Check if it's time to take a sample
  if (elapsedTime >= SAMPLE_PERIOD) {
    // Calculate missed samples (only after first sample)
    if (!firstSample) {
      float missedSamples = (float)elapsedTime / (float)SAMPLE_PERIOD - 1.0; // Must use float division or else it rounds down
      if (missedSamples > 0) {
        Serial.print("WARNING: Missed ");
        Serial.print(missedSamples);
        Serial.println(" samples!");
      }
    } else {
      firstSample = false;
    }
    
    // Save the time of this sample
    previousMillis = currentMillis;
    
    // Read the input on analog pins. 
    // You might want to adapt this part of the code depending on the number of sensors you have.
    int sensorValue0 = analogRead(A0);
    int sensorValue1 = analogRead(A1);
    int sensorValue2 = analogRead(A2);

    // Print out the data
    Serial.print(currentMillis);
    Serial.print(",");
    Serial.print(sensorValue0);
    Serial.print(",");
    Serial.print(sensorValue1);
    Serial.print(",");
    Serial.println(sensorValue2);

  }

}
