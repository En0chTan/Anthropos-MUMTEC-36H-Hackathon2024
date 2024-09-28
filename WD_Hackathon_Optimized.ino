#define FP_INT_TYPE int32_t
#define FP_INT_XL_TYPE int64_t

typedef FP_INT_TYPE fp_int_t;
typedef FP_INT_XL_TYPE fp_intxl_t;

#define FP_NUM_BITS (sizeof(fp_int_t) << 3)
#define FP_INT_BITS (18)
#define FP_FRAC_BITS (FP_NUM_BITS - FP_INT_BITS)

#define FP_SCALE (FP_FRAC_BITS)
#define FP_SCALE_FACTOR (1L << FP_SCALE)

#define FP_INT_MASK (((1L << FP_INT_BITS) - 1L) << FP_FRAC_BITS)
#define FP_FRAC_MASK ((1L << FP_FRAC_BITS) - 1L)

#define FP_FROM_INT(a) ((fp_int_t)(a) << FP_FRAC_BITS) // Convert int to fp representation
#define FP_VAL_0 0
#define FP_VAL_1 FP_FROM_INT(1)
#define FP_VAL_NEG_1 FP_FROM_INT(-1)

#define FP_SIGN_BIT(a) (a >> (FP_NUM_BITS - 1L) & 1L)
#define FP_SIGN(a) (a >> (FP_NUM_BITS - 1L) & 1L == 0 ? FP_VAL_1 : FP_VAL_NEG_1)

#define fp_add(a, b) ((a) + (b))
#define fp_sub(a, b) ((a) - (b))

float fp_to_float(fp_int_t a){
return (float) a / FP_SCALE_FACTOR;
}

fp_int_t float_to_fp (float a){
return (fp_int_t)(a * FP_SCALE_FACTOR);
}

fp_int_t fp_mul(fp_int_t a, fp_int_t b){
return ((fp_intxl_t)a * b >> FP_SCALE);
}

fp_int_t fp_div(fp_int_t a, fp_int_t b){
return ((fp_intxl_t) (a)  << FP_SCALE) / b;
}

#define SET_PIN_HIGH(port, pin) (PORT ## port |= (1 << pin))
#define SET_PIN_LOW(port, pin)((PORT ## port) &= ~(1 << (pin)))
#define PIN_READ(port, pin) (PIN ## port & (1 << pin))
#include <Wire.h>

#define LOGGING_PIN A0

#define I2C_MASTER_FREQ_HZ 400000L
#define GYRO_LSB_SENSITIVITY float_to_fp(131000.0)
#define MPU6050_CALIBRATION_SAMPLE_SIZE 100L
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

fp_int_t calibrationZ = FP_VAL_0;
fp_int_t angleZ = FP_VAL_0, temp = FP_VAL_0;
uint32_t dt = 0, currtime = 0, prevtime = 0;

int32_t mpu6050_getGyroZ_raw();

// List of registers and command to configure mpu6050
uint8_t i2c_data[] = {
    MPU6050_PWR_MGMT_1, MPU6050_PWR_MGMT_1_VAL,
    MPU6050_GYRO_CONFIG, MPU6050_GYRO_CONFIG_VAL,
    MPU6050_SMPRT_DIV, MPU6050_SMPRT_DIV_VAL,
    MPU6050_CONFIG, MPU6050_CONFIG_VAL
};


void mpu6050_setup() {
  Wire.begin();
  Wire.setClock(I2C_MASTER_FREQ_HZ);

  for (int i = 0; i < sizeof(i2c_data); i += 2) {
    uint8_t data[2] = { i2c_data[i], i2c_data[i + 1] };
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(data, sizeof(data));  // Write to mpu6050 registers
    if (Wire.endTransmission(true) != 0) {
//      Serial.println("MPU6050 Failed to Initialize!");
      while(1){};
    };
  }
  
//  Serial.println("Calibrating MPU6050, do not move the sensor");
  for (int i = 0; i<MPU6050_CALIBRATION_SAMPLE_SIZE; i++){
        int32_t gyroZ = mpu6050_getGyroZ_raw(); 
        // Serial.println(gyroZ);
        calibrationZ = fp_add(calibrationZ, FP_FROM_INT(gyroZ));
  }
  calibrationZ = fp_div(calibrationZ, FP_FROM_INT(MPU6050_CALIBRATION_SAMPLE_SIZE));    
//  Serial.println(calibrationZ);

}

int32_t mpu6050_getGyroZ_raw(){
  int32_t rawGyroZ = 0;

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

void mpu6050_updateZ(fp_int_t* angleZ) {
  currtime = millis();
  int32_t gyroZ = mpu6050_getGyroZ_raw();
  dt = currtime - prevtime;
  prevtime = currtime;
  temp = fp_div(fp_sub(FP_FROM_INT(gyroZ), calibrationZ), GYRO_LSB_SENSITIVITY);
  temp = fp_mul(temp, FP_FROM_INT(dt));
  *angleZ = fp_add(*angleZ, temp);
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
  if (fp_to_float(angleZ) < 3.0 && fp_to_float(angleZ) >-3.0){
    SET_PIN_HIGH(D, 2);
    SET_PIN_HIGH(D, 3);
    SET_PIN_HIGH(D, 4);
    SET_PIN_HIGH(D, 5);
    SET_PIN_HIGH(D, 6);
    SET_PIN_HIGH(D, 7);
    SET_PIN_HIGH(B, 0);
    SET_PIN_HIGH(B, 1);
    SET_PIN_HIGH(B, 2);
    SET_PIN_HIGH(B, 3);
    SET_PIN_HIGH(B, 3);
    SET_PIN_HIGH(B, 4);
    SET_PIN_HIGH(B, 5);
  }else{
    SET_PIN_LOW(D, 2);
    SET_PIN_LOW(D, 3);
    SET_PIN_LOW(D, 4);
    SET_PIN_LOW(D, 5);
    SET_PIN_LOW(D, 6);
    SET_PIN_LOW(D, 7);
    SET_PIN_LOW(B, 0);
    SET_PIN_LOW(B, 1);
    SET_PIN_LOW(B, 2);
    SET_PIN_LOW(B, 3);
    SET_PIN_LOW(B, 3);
    SET_PIN_LOW(B, 4);
    SET_PIN_LOW(B, 5);
  }

  // Serial.println(angleZ);
}