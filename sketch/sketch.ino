#include <Arduino.h>
#include <Arduino_RouterBridge.h>

static void setChannel(uint8_t pin, bool logicalOn) {
  // active-low
  digitalWrite(pin, logicalOn ? LOW : HIGH);
}

static void applyLed(const char* ledName, bool ledOn, bool r, bool g, bool b) {
  uint8_t pinR = 0;
  uint8_t pinG = 0;
  uint8_t pinB = 0;

  if (strcmp(ledName, "led3") == 0) {
    pinR = LED3_R;
    pinG = LED3_G;
    pinB = LED3_B;
  } else if (strcmp(ledName, "led4") == 0) {
    pinR = LED4_R;
    pinG = LED4_G;
    pinB = LED4_B;
  } else {
    return;
  }

  setChannel(pinR, ledOn && r);
  setChannel(pinG, ledOn && g);
  setChannel(pinB, ledOn && b);
}

void onSetMcuLed(String ledName, int onValue, int rValue, int gValue, int bValue) {
  bool ledOn = (onValue != 0);
  bool r = (rValue != 0);
  bool g = (gValue != 0);
  bool b = (bValue != 0);

  applyLed(ledName.c_str(), ledOn, r, g, b);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

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

  Serial.println("MCU RGB controller ready");
}

void loop() {
  
}


