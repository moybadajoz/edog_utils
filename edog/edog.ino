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
        Moises Badajoz Martinez <moisesbadajoz36@gmail.com>
        Paola Lizbet Cabrera Oros <pl.cabreraoros@ugto.mx> 
University of Guanajuato, 2023
*/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ModbusIP_ESP8266.h>
#include <WiFi.h>

#define SMIN 100
#define SMAX 600

//Magic initial servo values (roughly the 90 degree position for each servo)
//You may replace them with your own empirically determined values.
//int sval[8] = { 310, 310, 443, 458, 335, 320, 425, 390 };
int sval[8] = {175, 188, 532, 583, 286, 281, 452, 467};
const char* ssid = "edog"; 
const char* password = "";
// WiFiUDP Udp;
IPAddress local_ip(192, 168, 4, 1);
IPAddress gateway(192, 168, 4, 1);
IPAddress subnet(255, 255, 255, 0);
// WebServer server(80);

const int IDX_REG = 0;

ModbusIP mb;

Adafruit_PWMServoDriver b1 = Adafruit_PWMServoDriver();
uint8_t snum = 0;

void setup() {
  // put your setup code here, to run once:
  b1.begin();
  b1.setPWMFreq(60);
  WiFi.softAP(ssid, password);
  WiFi.softAPConfig(local_ip, gateway, subnet);
  // Udp.begin(4210);
  mb.server(502); // inicializacion del servidor y asignacion del puerto
  mb.addHreg(IDX_REG, 0, 8); // marca el inidice del registro, su valor y cuantos registros podra almacenar

  for(int k=0; k < 8; k++)
    b1.setPWM(snum+k, 0, sval[k]);

}

void loop() {
  // Read a string from the serial port and parse it for integers
  // representing the PWM values for each servo.
  mb.task(); // no se que hace pero dice que es necesario
  for(int k=0; k < 8; k++)
  {
    int ang = mb.Hreg(IDX_REG+k);
    if (ang > 0)
      b1.setPWM(snum+k, 0, ang);
  }
}
