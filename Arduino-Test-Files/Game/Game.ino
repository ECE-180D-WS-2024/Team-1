#include <ArduinoBLE.h>
#include <Arduino_LSM6DS3.h>

#define PIN_A 6
#define PIN_B 8
#define PIN_C 10
#define PIN_D 11
#define PIN_E 12
#define PIN_F 7
#define PIN_G 9
#define DIG_0 5
#define DIG_1 4
#define DIG_2 3
#define DOT 2
#define RED_LED 21
#define GREEN_LED 20
#define BUTTON_1 14
#define BUTTON_2 15
#define BUTTON_3 16
#define BUTTON_4 17

int digitmappings[10][7] = { // Starts at 9!
  {1, 1, 1, 1, 0, 1, 1}, // 9
  {1, 1, 1, 1, 1, 1, 1}, // 8
  {1, 1, 1, 0, 0, 0, 0}, // 7
  {1, 0, 1, 1, 1, 1, 1}, // 6
  {1, 0, 1, 1, 0, 1, 1}, // 5
  {0, 1, 1, 0, 0, 1, 1}, // 4
  {1, 1, 1, 1, 0, 0, 1}, // 3
  {1, 1, 0, 1, 1, 0, 1}, // 2
  {0, 1, 1, 0, 0, 0, 0}, // 1
  {1, 1, 1, 1, 1, 1, 0}, // 0
};
int pinArr[7] = {PIN_A, PIN_B, PIN_C, PIN_D, PIN_E, PIN_F, PIN_G};
int digArr[4] = {DIG_0, DIG_1, DIG_2};
int idxArr[3] = {9, 9, 6};
int activeDigit = 0;
int prevSec = millis();
int prevUpdate = millis();
int prevBlink = millis();
int prevRead = millis();
bool time_expired = false;
bool game_started = false;
int fail_led = 0;

BLEService ClockService("f8f9c2aa-6ac0-4e7e-9848-a4f4e8800f69"); // Send Clock Information
BLEService GameService("c24660cb-48d0-4f69-af9a-72f3c8da7c94"); // Send Game Info
BLEService PuzzleService("f853a97e-2fff-4dd4-b9a1-b69fe2c74e53"); // Send Puzzle Info
BLEIntCharacteristic TimeCharacteristic("2e92fbab-6365-4ce6-aa19-9b1fe217888c", BLERead | BLEWrite);
BLEIntCharacteristic StartCharacteristic("d1b05699-f934-43e3-ae5f-2510118995f7", BLERead | BLEWrite);
BLEIntCharacteristic SequenceCharacteristic("2e1c9e14-a3d6-41d6-a484-114375527aa6", BLERead | BLEWrite);
BLEIntCharacteristic WireCharacteristic("5101a8d5-e8da-4ef6-9e03-1c0573d25429", BLERead | BLEWrite);
BLEIntCharacteristic OrientationCharacteristic("ba90a02e-9acd-4f6b-8d2d-db52abdab1ab", BLERead | BLEWrite);
BLEIntCharacteristic SkipCharacteristic("31a276d9-606a-4089-971f-0c3c349a7374", BLERead | BLEWrite);
BLEIntCharacteristic SpeechCharacteristic("068891ec-d3b6-4d8a-9572-d4292b02e729", BLERead | BLEWrite);
BLEIntCharacteristic RgbPressedCharacteristic("b12b0137-a6a4-4e6c-b3a2-824e5827afda", BLERead | BLEWrite);


void setup() {
  pinMode(PIN_A, OUTPUT);
  pinMode(PIN_B, OUTPUT);
  pinMode(PIN_C, OUTPUT);
  pinMode(PIN_D, OUTPUT);
  pinMode(PIN_E, OUTPUT);
  pinMode(PIN_F, OUTPUT);
  pinMode(PIN_G, OUTPUT);
  pinMode(DIG_0, OUTPUT);
  pinMode(DIG_1, OUTPUT);
  pinMode(DIG_2, OUTPUT);
  pinMode(DOT, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUTTON_1, INPUT);
  pinMode(BUTTON_2, INPUT);
  pinMode(BUTTON_3, INPUT);
  pinMode(BUTTON_4, INPUT);
  digitalWrite(RED_LED, 0);
  digitalWrite(DOT, 0);
  Serial.begin(9600);
  Serial1.begin(9600);
  BleSetup();
  ImuSetup();
}

void loop() { 
  BLEDevice central = BLE.central();


  if (central && central.connected()) {
    ReadButton();
    ReadImu();
    ReadTransmitter();
    // Wait for start signal from host
    if (StartCharacteristic.written() && StartCharacteristic.value()) {
      ResetClock();
      game_started = true;
      digitalWrite(DOT, 1);
    }
  }
  if (game_started) {
    // Send time remaining to host
    if (central && central.connected()) {
      TimeCharacteristic.writeValue((9 - idxArr[2]) * 60 + (9 - idxArr[1]) * 10 + (9 - idxArr[0]));
    }

    // Write current digit value
    for(int i = 0; i < 3; i++) {
      if (i == activeDigit) {
        digitalWrite(digArr[i], 0);
      }
      else {
        digitalWrite(digArr[i], 1);
      }
    }

    if (!time_expired) {
      if (millis() - prevBlink >= 500) {
        digitalWrite(GREEN_LED, !fail_led);
        fail_led = fail_led ^ 1;
        prevBlink = millis();
      }
      // Update Clock
      if(millis() - prevSec >= 1000) {
        if (idxArr[0] == 9) {
          if (idxArr[1] == 9) {
            if (idxArr[2] == 9) {
              time_expired = true;
              digitalWrite(GREEN_LED, 0);
            }
            else {
              idxArr[2] = (idxArr[2] + 1) % 10;
            }
            if (!time_expired) {
              idxArr[1] = 4;
            }
          }
          else {
            idxArr[1] = (idxArr[1] + 1) % 10;
          }
          if (!time_expired) {
            idxArr[0] = 0;
          }
        }
        else {
        idxArr[0] = (idxArr[0] + 1) % 10;
        }
        prevSec = millis();
      }
    }
    else { 
      if (millis() - prevBlink >= 500) {
        digitalWrite(RED_LED, !fail_led);
        fail_led = fail_led ^ 1;
        prevBlink = millis();
      }
    }
    // Write Display
    for(int i = 0; i < 7; i++) {
      digitalWrite(pinArr[i], digitmappings[idxArr[activeDigit]][i]);
    }

    if(millis() - prevUpdate >= 2) {
      activeDigit = (activeDigit + 1) % 3; // Alternate digit display
      prevUpdate = millis();
    }
  }
}

void BleSetup() {
  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting Bluetooth® Low Energy module failed!");

    while (1);
  }

  // set advertised local name and service UUID:
  BLE.setLocalName("Nano 33 IoT");
  BLE.setAdvertisedService(ClockService);

  // add the characteristic to the service

  ClockService.addCharacteristic(TimeCharacteristic);
  GameService.addCharacteristic(StartCharacteristic);
  GameService.addCharacteristic(SkipCharacteristic);
  GameService.addCharacteristic(SpeechCharacteristic);
  PuzzleService.addCharacteristic(RgbPressedCharacteristic);
  PuzzleService.addCharacteristic(SequenceCharacteristic);
  PuzzleService.addCharacteristic(WireCharacteristic);
  PuzzleService.addCharacteristic(OrientationCharacteristic);
  // add service
  BLE.addService(ClockService);
  BLE.addService(GameService);
  BLE.addService(PuzzleService);

  // start advertising
  BLE.advertise();

}

void ImuSetup() {
  if (!IMU.begin()) {
    Serial.println("starting IMU module failed!");
    while (1);
  }
  Serial.println("Initialized IMU!");
}


void ReadButton() {
  int one = digitalRead(BUTTON_1);
  int two = digitalRead(BUTTON_2);
  int three = digitalRead(BUTTON_3);
  int four = digitalRead(BUTTON_4);
  if (one) {
    Serial.println("1");
    SequenceCharacteristic.writeValue(1);
  }
  else if (two) {
    Serial.println("2");
    SequenceCharacteristic.writeValue(2);
  }
  else if (three) {
    Serial.println("3");
    SequenceCharacteristic.writeValue(3);
  }
  else if (four) {
    Serial.println("4");
    SequenceCharacteristic.writeValue(4);
  }
  else {
    SequenceCharacteristic.writeValue(0);
  }
}

void ResetClock() {
  idxArr[0] = 9;
  idxArr[1] = 9;
  idxArr[2] = 6;
  digitalWrite(RED_LED, 0);
  time_expired = false;
}

void ReadImu() {
  float x, y, z, rx, ry, rz;
  if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
    IMU.readAcceleration(x, y, z);
    IMU.readGyroscope(rx, ry, rz);
    ReadOrientation(x, y, z, rx, ry, rz);
  }
}

void ReadOrientation(float x_accel, float y_accel, float z_accel, float x_gyro, float y_gyro, float z_gyro) {
    if (z_accel > 0.8) {
        OrientationCharacteristic.writeValue(0); // FLAT orientation
    }
    else if (z_accel < -0.8) {
        OrientationCharacteristic.writeValue(1); // UPSIDE DOWN orientation
    }
    else if (x_accel > 0.8) {
        OrientationCharacteristic.writeValue(2); // ANTENNA DOWN orientation
    }
    else if (x_accel < -0.8) {
        OrientationCharacteristic.writeValue(3); // ANTENNA UP orientation
    }
    else {
        OrientationCharacteristic.writeValue(-1); // UNRECOGNIZED orientation
    }
}

void ReadTransmitter() {
  // Read data from UART
  if (Serial1.available() >= 0) {
    char receivedData = Serial1.read();
    // Wire Cutting Data
    if (receivedData == '1') {
      WireCharacteristic.writeValue(1);
    }
    else if (receivedData == '2') {
      WireCharacteristic.writeValue(2);
    }
    else if (receivedData == '3') {
      WireCharacteristic.writeValue(3);
    }
    else if (receivedData == '4') {
      WireCharacteristic.writeValue(4);
    }
    else if (receivedData == '5') {
      WireCharacteristic.writeValue(5);
    }
    else if (receivedData == '6') {
      WireCharacteristic.writeValue(6);
    }
    else if (receivedData == '0') {
      WireCharacteristic.writeValue(0);
    }

    // Game Skip/Stay
    else if (receivedData == 's') {
      SkipCharacteristic.writeValue(1);
    }
    else if (receivedData == 'n') {
      SkipCharacteristic.writeValue(0);
    }

    // Talking/NotTalking
    else if (receivedData == 't') {
      SpeechCharacteristic.writeValue(1);
    }
    else if (receivedData == 'q') {
      SpeechCharacteristic.writeValue(0);
    }
    
    // RGB pressed/released
    else if (receivedData == 'p') {
      RgbPressedCharacteristic.writeValue(1);
    }
    else if (receivedData == 'r') {
      RgbPressedCharacteristic.writeValue(0);
    }
  }
}