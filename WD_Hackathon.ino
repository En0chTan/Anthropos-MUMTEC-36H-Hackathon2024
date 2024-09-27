#include <Wire.h>

#define LOGGING_PIN A0

#define I2C_MASTER_FREQ_HZ 400000
#define GYRO_LSB_SENSITIVITY 131000.0
#define MPU6050_CALIBRATION_SAMPLE_SIZE 100
#define MPU6050_READ_BYTES 2

#define MPU6050_ADDR 0x68

#define MPU6050_PWR_MGMT_1 0x6B
#define MPU6050_PWR_MGMT_1_VAL 0x00

#define MPU6050_GYRO_CONFIG 0x1B
#define MPU6050_GYRO_CONFIG_VAL 0x00

#define MPU6050_SMPRT_DIV 0X19
#define MPU6050_SMPRT_DIV_VAL 0x00

#define MPU6050_CONFIG 0x1A
#define MPU6050_CONFIG_VAL 0x00

#define MPU6050_TEMP_OUT_H 0x41
#define MPU6050_GYRO_ZOUT_H 0x47

float calibrationZ = 0;
float angleZ = 0, temp = 0;
uint32_t dt = 0, currtime = 0, prevtime = 0;

int16_t mpu6050_getGyroZ_raw();

// List of registers and command to configure mpu6050
uint8_t i2c_data[] = {
    MPU6050_PWR_MGMT_1, MPU6050_PWR_MGMT_1_VAL,
    MPU6050_GYRO_CONFIG, MPU6050_GYRO_CONFIG_VAL,
    MPU6050_SMPRT_DIV, MPU6050_SMPRT_DIV_VAL,
    MPU6050_CONFIG, MPU6050_CONFIG_VAL
};


void mpu6050_setup() {
  Wire.begin();
  Wire.setClock(400000);

  for (int i = 0; i < sizeof(i2c_data); i += 2) {
    uint8_t data[2] = { i2c_data[i], i2c_data[i + 1] };
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(data, sizeof(data));  // Write to mpu6050 registers
    if (Wire.endTransmission(true) != 0) {
      Serial.println("MPU6050 Failed to Initialize!");
      while(1){};
    };
  }

  Serial.println("Calibrating MPU6050, do not move the sensor");
  for (int i = 0; i<MPU6050_CALIBRATION_SAMPLE_SIZE; i++){
        int16_t gyroZ = mpu6050_getGyroZ_raw();
        // Serial.println(gyroZ);
        calibrationZ += (float)gyroZ;
  }
  calibrationZ = (calibrationZ/MPU6050_CALIBRATION_SAMPLE_SIZE);
  Serial.println(calibrationZ);

}

int16_t mpu6050_getGyroZ_raw(){
  int16_t rawGyroZ = 0;

  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_GYRO_ZOUT_H);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050_ADDR, MPU6050_READ_BYTES, true);

  while(Wire.available()){
    rawGyroZ =  Wire.read() << 8;
    rawGyroZ = rawGyroZ | Wire.read();
  }
  return rawGyroZ;
}

void mpu6050_updateZ(float* angleZ) {
  currtime = millis();
  int16_t gyroZ = mpu6050_getGyroZ_raw();
  dt = currtime - prevtime;
  prevtime = currtime;
  temp = ((float)gyroZ - calibrationZ)/GYRO_LSB_SENSITIVITY * (float)dt;
  *angleZ = *angleZ + temp;
}

void setup(){
  Serial.begin(250000);

  mpu6050_setup();

  pinMode(LOGGING_PIN, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(13, OUTPUT);
  // fp_int_t a = float_to_fp(23.76);
  // fp_int_t b = float_to_fp(213.3);
  // fp_int_t c = FP_FROM_INT(25L);
  // fp_int_t d = fp_mul (a, b);

  // Serial.println(fp_to_float(a));
  // Serial.println(fp_to_float(b));
  // Serial.println(fp_to_float(c));
  // Serial.println(fp_to_float(d));
  // Serial.println(25.0);


}


void loop(){
  PORTC |= (1 << 0);
  PORTC &= ~(1 << 0);
  mpu6050_updateZ(&angleZ);
  if (angleZ < 3.0 && angleZ >-3.0){
    digitalWrite(2, HIGH);
    digitalWrite(3, HIGH);
    digitalWrite(4, HIGH);
    digitalWrite(5, HIGH);
    digitalWrite(6, HIGH);
    digitalWrite(7, HIGH);
    digitalWrite(8, HIGH);
    digitalWrite(9, HIGH);
    digitalWrite(10,HIGH);
    digitalWrite(11,HIGH);
    digitalWrite(11,HIGH);
    digitalWrite(12,HIGH);
    digitalWrite(13,HIGH);
  }else{
    digitalWrite(2, LOW);
    digitalWrite(3, LOW);
    digitalWrite(4, LOW);
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10,LOW);
    digitalWrite(11,LOW);
    digitalWrite(11,LOW);
    digitalWrite(12,LOW);
    digitalWrite(13,LOW);
  }

  Serial.println(angleZ);
}
