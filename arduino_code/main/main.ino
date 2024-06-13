int enA = 9;
int in1 = 8;
int in2 = 7;

int enB = 3;
int in3 = 5;
int in4 = 4;

void setup() {
  // Set all the motor control pins to outputs
  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  pinMode(13, OUTPUT);

  digitalWrite(enA, 1);
  digitalWrite(enB, 1);

  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char serialData = char(Serial.read());

    if (serialData != '\n' and serialData != '\r') {
      switch (serialData) {
        case 'S':
          stop();
          // moveForward();
          digitalWrite(13, 1);
          break;

        case 'F':
          moveForward();
          digitalWrite(13, 0);
          break;

        case 'R':
          digitalWrite(13, 0);
          turnRight();
          break;

        case 'L':
          digitalWrite(13, 0);
          turnLeft();
          break;

        case 'B':
          digitalWrite(13, 0);
          moveBackward();
          break;
      }
    }
  }
}


void moveForward() {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
}

void moveBackward() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
}

void stop() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);  //STOP
  digitalWrite(in4, LOW);
}

void turnRight() {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW); 
  digitalWrite(in4, HIGH);
}

void turnLeft() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
}
