/* This sketch can be used to move the servos on the eDog robot.
Motor Number    Joint
     0          Front right hip
     1          Rear right hip
     2          Rear left hip
     3          Front left hip
     4          Front right knee
     5          Rear right knee
     6          Rear left knee
     7          Front left knee
Author: J.-P. Ramirez-Paredes <jpiramirez@gmail.com> <jpi.ramirez@ugto.mx>
University of Guanajuato, 2023
*/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define SMIN 100
#define SMAX 600

//Magic initial servo values (roughly the 90 degree position for each servo)
//You may replace them with your own empirically determined values.
int sval[8] = { 310, 310, 443, 458, 335, 320, 425, 390 };

Adafruit_PWMServoDriver b1 = Adafruit_PWMServoDriver();
uint8_t snum = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  b1.begin();
  b1.setPWMFreq(60);

  for(int k=0; k < 8; k++)
    b1.setPWM(snum+k, 0, sval[k]);

}

void loop() {
  // Read a string from the serial port and parse it for integers
  // representing the PWM values for each servo.
  int ang;
  int k;

  while (Serial.available() == 0){}

  for(k=0; k < 8; k++)
  {
    ang = Serial.parseInt();
    b1.setPWM(snum+k, 0, ang);
  }

  while (Serial.available() > 0)
    Serial.read(); 
}
