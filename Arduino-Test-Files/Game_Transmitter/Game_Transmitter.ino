
#define WIRE_1 12
#define WIRE_2 11
#define WIRE_3 10
#define WIRE_4 9
#define WIRE_5 8
#define WIRE_6 7
#define TOP_RIGHT 6
#define BOTTOM_RIGHT 5
#define TOP_LEFT 4
#define BOTTOM_LEFT 3

long randColor;
long randFlash;
int prevLight = 0;
bool on = true;

void setup() { 
  pinMode(WIRE_1, INPUT);
  pinMode(WIRE_2, INPUT);
  pinMode(WIRE_3, INPUT);
  pinMode(WIRE_4, INPUT);
  pinMode(WIRE_5, INPUT);
  pinMode(WIRE_6, INPUT);
  pinMode(TOP_RIGHT, INPUT);
  pinMode(BOTTOM_RIGHT, INPUT);
  pinMode(TOP_LEFT, INPUT);
  pinMode(BOTTOM_LEFT, INPUT);
  Serial1.begin(9600);
}

void loop() {
  readWires();
  readSequence();
}

void readWires() {

  int w_1 = digitalRead(WIRE_1);
  int w_2 = digitalRead(WIRE_2);
  int w_3 = digitalRead(WIRE_3);
  int w_4 = digitalRead(WIRE_4);
  int w_5 = digitalRead(WIRE_5);
  int w_6 = digitalRead(WIRE_6);

  if (w_1) {
    Serial1.println('1');
  }
  else if (w_2) {
    Serial1.println('2');
  }
  else if (w_3) {
    Serial1.println('3');
  }
  else if (w_4) {
    Serial1.println('4');
  }
  else if (w_5) {
    Serial1.println('5');
  }
  else if (w_6) {
    Serial1.println('6');
  }
  else {
    Serial1.println('0'); // No Button Pressed
  }
}

void readSequence() {

  int top_right = digitalRead(TOP_RIGHT);
  int bottom_right = digitalRead(BOTTOM_RIGHT);
  int top_left = digitalRead(TOP_LEFT);
  int bottom_left = digitalRead(BOTTOM_LEFT);

  if (top_right) {
    Serial1.println('a');
  }
  else if (bottom_right) {
    Serial1.println('b');
  }
  else if (top_left) {
    Serial1.println('c');
  }
  else if (bottom_left) {
    Serial1.println('d');
  }
  else {
    Serial1.println('n'); // No Button Pressed
  }
}
