#include <Arduino.h>
#include <Arduino_RouterBridge.h>

void setChannel(uint8_t pin, bool logicalOn) {
  // active-low
  digitalWrite(pin, logicalOn ? LOW : HIGH);
}


void onSetMcuLed( String ledName, int onValue, int rValue, int gValue, int bValue) {
 
   uint8_t pinR; 
   uint8_t pinG;
   uint8_t pinB;
  
  if (ledName == "led3") {
     pinR = LED3_R;
     pinG = LED3_G;
     pinB = LED3_B;
  } else if (ledName == "led4") {
     pinR = LED4_R;
     pinG = LED4_G;
     pinB = LED4_B;
  } else {
    return;
  }

  setChannel(pinR, onValue && rValue);
  setChannel(pinG, onValue && gValue);
  setChannel(pinB, onValue && bValue);
}

void setup() {

  pinMode(LED3_R, OUTPUT);
  pinMode(LED3_G, OUTPUT);
  pinMode(LED3_B, OUTPUT);
  pinMode(LED4_R, OUTPUT);
  pinMode(LED4_G, OUTPUT);
  pinMode(LED4_B, OUTPUT);

  digitalWrite(LED3_R, HIGH);
  digitalWrite(LED3_G, HIGH);
  digitalWrite(LED3_B, HIGH);
  digitalWrite(LED4_R, HIGH);
  digitalWrite(LED4_G, HIGH);
  digitalWrite(LED4_B, HIGH);

  Bridge.begin();
  Bridge.provide("set_mcu_led", onSetMcuLed);
  Monitor.begin();
  delay(1000);
  Monitor.println("MCU RGB controller ready");
}

void loop() {}
