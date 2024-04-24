/*
  LED

  This example creates a Bluetooth® Low Energy peripheral with service that contains a
  characteristic to control an LED.

  The circuit:
  - Arduino MKR WiFi 1010, Arduino Uno WiFi Rev2 board, Arduino Nano 33 IoT,
    Arduino Nano 33 BLE, or Arduino Nano 33 BLE Sense board.

  You can use a generic Bluetooth® Low Energy central app, like LightBlue (iOS and Android) or
  nRF Connect (Android), to interact with the services and characteristics
  created in this sketch.

  This example code is in the public domain.
*/

#include <ArduinoBLE.h>
#include <Arduino_LSM6DS3.h>

BLEService ledService("180A"); // Bluetooth® Low Energy LED Service
BLEService deathService("1234"); // Check if connection is still alive
BLEService ImuService("a2de8038-5b04-4299-9940-3bfa34d2fc3b"); // Send IMU informatoin

// Bluetooth® Low Energy LED Switch Characteristic - custom 128-bit UUID, read and writable by central
BLEByteCharacteristic switchCharacteristic("2A57", BLERead | BLEWrite);
BLEByteCharacteristic checkCharacteristic("0123", BLERead | BLEWrite);
// UUIDs were randomly generated. Can always change but need to change corresponding UUID in host file
BLEFloatCharacteristic xAccelCharacteristic("663fdcf8-2126-464d-a6c1-c882f5477fb7", BLERead | BLEWrite);
BLEFloatCharacteristic yAccelCharacteristic("e6ac0344-9aee-49ab-b601-1d26b77cf08c", BLERead | BLEWrite);
BLEFloatCharacteristic zAccelCharacteristic("224ad21b-9c75-4e1c-a3f0-51c0c7d0a9a8", BLERead | BLEWrite);
BLEFloatCharacteristic xAngularVeloCharacteristic("4de63bcd-e713-4e28-9392-3cc1d7efbabc", BLERead | BLEWrite);
BLEFloatCharacteristic yAngularVeloCharacteristic("99c07d47-9018-489b-a937-0d911a61aa69", BLERead | BLEWrite);
BLEFloatCharacteristic zAngularVeloCharacteristic("85c17e72-fb28-4883-9333-479b20fce5a7", BLERead | BLEWrite);

const int ledPin = LED_BUILTIN; // pin to use for the LED
void ImuSetup();
void BleSetup();

void setup() {
  Serial.begin(9600);

  // set LED pin to output mode
  pinMode(LED_BUILTIN, OUTPUT);
  // setup IMU
  ImuSetup();
  // setup BLE
  BleSetup();
  
}

void loop() {
  unsigned long timer = 0;
  unsigned long prevUpdate = 0;
  float x, y, z, rx, ry, rz;
  int tx_x, tx_y, tx_z, tx_rx, tx_ry, tx_rz;
  // listen for Bluetooth® Low Energy peripherals to connect:
  BLEDevice central = BLE.central();

  // if a central is connected to peripheral:
  if (central) {
    Serial.print("Connected to central: ");
    // print the central's MAC address:
    Serial.println(central.address());
    prevUpdate = millis();
    // while the central is still connected to peripheral:
    while (central.connected()) {

      // Ensure connection is responsive
      timer = millis() - prevUpdate;
      if (timer > 1000) {
        Serial.println("Connection Timeout, Disconnecting...");
      }
      if (checkCharacteristic.written()) {
        prevUpdate = millis();
      }
      // if the remote device wrote to the characteristic,
      // use the value to control the LED:
      if (switchCharacteristic.written()) {
        if (switchCharacteristic.value()) {   // any value other than 0
          Serial.println("LED on");
          digitalWrite(ledPin, HIGH);         // will turn the LED on
        } else {                              // a 0 value
          Serial.println(F("LED off"));
          digitalWrite(ledPin, LOW);          // will turn the LED off
        }
      }
      
      // Send IMU Data through BLE, 
      if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
        digitalWrite(ledPin, HIGH); // Indicator that data is sending
        IMU.readAcceleration(x, y, z);
        IMU.readGyroscope(rx, ry, rz);
        /*        
        // Convert to int because float conversion at host causing issues
        tx_x = static_cast<int>(x * 1000);
        tx_y = static_cast<int>(y * 1000);
        tx_z = static_cast<int>(z * 1000);
        tx_rx = static_cast<int>(rx * 1000);
        tx_ry = static_cast<int>(ry * 1000);
        tx_rz = static_cast<int>(rz * 1000);

        */
        Serial.print("x: ");
        Serial.println(x);
        Serial.print("y: ");
        Serial.println(y);
        Serial.print("z: ");
        Serial.println(z);
        Serial.print("rx: ");
        Serial.println(rx);
        Serial.print("ry: ");
        Serial.println(ry);
        Serial.print("rz: ");
        Serial.println(rz);
        xAccelCharacteristic.writeValue(x);
        yAccelCharacteristic.writeValue(y);
        zAccelCharacteristic.writeValue(z);
        xAngularVeloCharacteristic.writeValue(rx);
        yAngularVeloCharacteristic.writeValue(ry);
        zAngularVeloCharacteristic.writeValue(rz);
        prevUpdate = millis();
      }
    }

    // when the central disconnects, print it out:
    Serial.print(F("Disconnected from central: "));
    Serial.println(central.address());
  }
}

void ImuSetup() {
    if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");

    while (1);
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
  BLE.setDeviceName("Nano 33 IoT");
  BLE.setAdvertisedService(ImuService);

  // add the characteristic to the service
  ledService.addCharacteristic(switchCharacteristic);

  deathService.addCharacteristic(checkCharacteristic);

  ImuService.addCharacteristic(xAccelCharacteristic);
  ImuService.addCharacteristic(yAccelCharacteristic);
  ImuService.addCharacteristic(zAccelCharacteristic);
  ImuService.addCharacteristic(xAngularVeloCharacteristic);
  ImuService.addCharacteristic(yAngularVeloCharacteristic);
  ImuService.addCharacteristic(zAngularVeloCharacteristic);

  // add service
  BLE.addService(ledService);
  BLE.addService(deathService);
  BLE.addService(ImuService);

  // set the initial value for the characeristic:
  switchCharacteristic.writeValue(0);

  // start advertising
  BLE.advertise();

  Serial.println("BLE LED Peripheral");
  Serial.println(BLE.address());
}
