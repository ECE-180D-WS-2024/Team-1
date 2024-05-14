#include <ArduinoBLE.h>

#define WIRE_1 2
#define WIRE_2 3
#define WIRE_3 4
#define WIRE_4 5
#define WIRE_5 6
#define WIRE_6 7
#define SPEECH 8
#define RED 15
#define GREEN 16
#define BLUE 17
#define RGB_ENABLE 20
#define SKIP 21

long randColor;
long randFlash;
int prevLight = 0;
int FlashInterval[3] = {0, 200, 1000};
bool on = true;

BLEService GameService("c24660cb-48d0-4f69-af9a-72f3c8da7c94"); // Send Game Info
BLEIntCharacteristic RgbCharacteristic("5976c24b-7bf4-493f-84d6-11c8ca71d899", BLERead | BLEWrite);

void setup() { 
  pinMode(WIRE_1, INPUT);
  pinMode(WIRE_2, INPUT);
  pinMode(WIRE_3, INPUT);
  pinMode(WIRE_4, INPUT);
  pinMode(WIRE_5, INPUT);
  pinMode(WIRE_6, INPUT);
  pinMode(SPEECH, INPUT);
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);
  pinMode(RGB_ENABLE, INPUT);
  Serial.begin(9600);
  BleSetup();
  Serial1.begin(9600);
}

void loop() {
  BLEDevice central = BLE.central();
  if (central && central.connected()) {
    if (RgbCharacteristic.written() && RgbCharacteristic.value()) {
      Serial.println((uint8_t) RgbCharacteristic.value());
      int value = (uint8_t) RgbCharacteristic.value();
      if (value / 10 >= 0 && value / 10 <= 5 && value % 10 >= 0 && value % 10 <= 2) {
        randColor = value / 10;
        randFlash = value % 10;
        RgbCharacteristic.writeValue(-1);
      }
    }
  }
  ReadWire();
  ControlRGB();
  checkSkip();
  checkSpeech();
  BLE.advertise();
}
void BleSetup() {
  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting Bluetooth® Low Energy module failed!");

    while (1);
  }
  // set advertised local name and service UUID:
  BLE.setLocalName("RGB Config");
  BLE.setAdvertisedService(GameService);

  // add the characteristic to the service
  GameService.addCharacteristic(RgbCharacteristic);
  // add service
  BLE.addService(GameService);

  // start advertising
  BLE.advertise();

}

void checkSkip() {
  int skip = digitalRead(SKIP);
  if (skip) {
    Serial1.println('s');
  }
  else {
    Serial1.println('n');
  }
}

void checkSpeech() {
  int speech = digitalRead(SPEECH);
  if (speech) {
    Serial1.println('t');
  }
  else {
    Serial1.println('q');
  }
}

void ControlRGB() {
  int light = digitalRead(RGB_ENABLE);
  if (light) {
    SetRGB();
    Serial1.println('p');
  }
  else {
    digitalWrite(RED, 0);
    digitalWrite(GREEN, 0);
    digitalWrite(BLUE, 0);
    Serial1.println("r");
  }
}
void SetRGB() {
  if (millis() - prevLight >= FlashInterval[randFlash]) {
    prevLight = millis();
    on = !on;
  }
  if (on) {
    GenColor();
  }
  else {
    digitalWrite(RED, 0);
    digitalWrite(GREEN, 0);
    digitalWrite(BLUE, 0);
  }
}
void GenColor() {
  if (randColor == 0) {
    digitalWrite(RED, 1);
    digitalWrite(GREEN, 0);
    digitalWrite(BLUE, 0);
  }
  if (randColor == 1) {
    digitalWrite(RED, 0);
    digitalWrite(GREEN, 1);
    digitalWrite(BLUE, 0);
  }
  if (randColor == 2) {
    digitalWrite(RED, 0);
    digitalWrite(GREEN, 0);
    digitalWrite(BLUE, 1);
  }
  if (randColor == 3) {
    digitalWrite(RED, 1);
    digitalWrite(GREEN, 1);
    digitalWrite(BLUE, 0);
  }
  if (randColor == 4) {
    digitalWrite(RED, 1);
    digitalWrite(GREEN, 0);
    digitalWrite(BLUE, 1);
  }
  if (randColor == 5) {
    digitalWrite(RED, 1);
    digitalWrite(GREEN, 1);
    digitalWrite(BLUE, 1);
  }
}

void ReadWire() {
  int one = digitalRead(WIRE_1);
  int two = digitalRead(WIRE_2);
  int three = digitalRead(WIRE_3);
  int four = digitalRead(WIRE_4);
  int five = digitalRead(WIRE_5);
  int six = digitalRead(WIRE_6);
  if (one) {
    Serial1.println('1');
  }
  else if (two) {
    Serial1.println('2');
  }
  else if (three) {
    Serial1.println('3');
  }
  else if (four) {
    Serial1.println('4');
  }
  else if (five) {
    Serial1.println('5');
  }
  else if (six) {
    Serial1.println('6');
  }
  else {
    Serial1.println('0');
  }
}
