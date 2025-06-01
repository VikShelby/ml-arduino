#include <Servo.h>

const int servoPins[] = {3, 5, 6, 9, 10, 11};
const int NUM_SERVOS = 6;

const int TRIG_PIN = 12;
const int ECHO_PIN = 13;
Servo servos[NUM_SERVOS];
int currentAngles[NUM_SERVOS]; 
int targetAngles[NUM_SERVOS];
const int BAUD_RATE = 115200; 
const int INITIAL_SERVO_ANGLE = 90; 

void setup() {
  Serial.begin(BAUD_RATE);
  while (!Serial) {
    ; 
  }
  Serial.println("Robotic Arm Controller - Arduino Ready.");
  Serial.println("Ensure external power is supplied to servos!");

 
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  for (int i = 0; i < NUM_SERVOS; i++) {
    servos[i].attach(servoPins[i]);
    currentAngles[i] = INITIAL_SERVO_ANGLE;
    targetAngles[i] = INITIAL_SERVO_ANGLE;
    servos[i].write(currentAngles[i]);
    delay(50); 
  }
  Serial.println("Servos initialized.");
}

void loop() {
  long duration, distanceCm;
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH, 30000); 

  if (duration > 0) {
    distanceCm = duration * 0.0343 / 2;
  } else {
    distanceCm = -1; 
  }
  for (int i = 0; i < NUM_SERVOS; i++) {
    Serial.print(currentAngles[i]);
    if (i < NUM_SERVOS - 1) {
      Serial.print(",");
    }
  }
  Serial.print(",");
  Serial.println(distanceCm);
    String command = Serial.readStringUntil('\n');
    command.trim(); 
    int parsedCount = 0;
    int tempAngles[NUM_SERVOS];
    int lastCommaIndex = -1;

    for (int i = 0; i < command.length(); i++) {
      if (command.charAt(i) == ',' || i == command.length() - 1) {
        String angleStr = command.substring(lastCommaIndex + 1, (command.charAt(i) == ',') ? i : i + 1);
        if (parsedCount < NUM_SERVOS) {
          tempAngles[parsedCount] = angleStr.toInt();
        }
        parsedCount++;
        lastCommaIndex = i;
      }
    }

    if (parsedCount == NUM_SERVOS) {
      for (int i = 0; i < NUM_SERVOS; i++) {
        targetAngles[i] = constrain(tempAngles[i], 0, 180); 
  

    } else {
      Serial.print("Error: Malformed command. Expected 6 angles, received string: '");
      Serial.print(command);
      Serial.print("', parsed ");
      Serial.print(parsedCount);
      Serial.println(" angles.");
    }
  }

  bool moved = false;
  for (int i = 0; i < NUM_SERVOS; i++) {
    if (currentAngles[i] != targetAngles[i]) {
        servos[i].write(targetAngles[i]);
        currentAngles[i] = targetAngles[i];
        moved = true;
    }
  }
  

  delay(50); 
             
}