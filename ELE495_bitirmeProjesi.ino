#include <Servo.h>
#define capPin A2
#define buzPin A1

int pos = 70;
//digital pin for servo : 9
//Metal çöp gönderimi
unsigned long signalStartTime = 0;
unsigned long signalDuration = 1000; //Duration in miliseconds

unsigned long program_Timer = 3000;
unsigned long program_start = 0;

int jetson_nano_signal = 0;
int signal_state = 0;

int init_value = 0;

int metal_detected = 0;

Servo myservo;

int flag = 0;

int servo_init = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(capPin,INPUT);
  pinMode(buzPin,INPUT);
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  myservo.write(pos); // tell servo to go to position in variable 'pos'
  delay(10);
}

//1 geldiğinde metal detektör çalıştırılır
//2 geldiğinde Kol kapanır.
//3 geldiğinde Kol açılır.
void loop() {
  // put your main code here, to run repeatedly:
    if(Serial.available() > 0 && flag == 0){
    flag = Serial.parseInt();
  }

  //Starting servo motor
  if(flag == 2 && servo_init == 0){
    if(servo_init == 0){          
        myservo.attach(9);  // attaches the servo on pin 9 to the servo object
        myservo.write(pos); // tell servo to go to position in variable 'pos'
        delay(10); 
    }
    //70,135 eski değerler
    for (pos = 70; pos <= 125; pos += 1) { // goes from 0 degrees to 180 degrees
                                        // in steps of 1 degree
      myservo.write(pos);              // tell servo to go to position in variable 'pos'
      delay(10);                       // waits 15ms for the servo to reach the position
      flag = 0;
  }
  servo_init = 1;
  myservo.detach();
  }
  if(flag == 3){   
    if(servo_init == 0){
      myservo.attach(9);  // attaches the servo on pin 9 to the servo object
      myservo.write(pos); // tell servo to go to position in variable 'pos'
      delay(10);
    }
      for(pos = 125; pos >= 70; pos -= 1) {// goes from 180 degrees to 0 degrees
      myservo.write(pos);              // tell servo to go to position in variable 'pos'
      delay(10);   
      flag = 0;                    // waits 15ms for the servo to reach the position
  }
}

  if(flag == 1 && init_value == 0){
    program_start = millis();
    init_value = 1;
  }
   //Metal detec
      if(((program_Timer) >= (millis() - program_start)) && flag == 1)
      {
        int counter = 0;
        int minval=1023;
        int maxval=0;

        long unsigned int sum=0;

        for (int i=0; i<256; i++)
        {
          //reset the capacitor
          
          pinMode(capPin,OUTPUT);
          digitalWrite(capPin,LOW);
          delayMicroseconds(20);
          pinMode(capPin,INPUT);
          //read the charge of capacitor
          int val = analogRead(capPin);//takes 13x8=104 microseconds
          minval = min(val,minval);
          maxval = max(val,maxval);
          sum+=val;
          
        }
        //mavi 5V,mor Toprak
        //sarı A2,yeşil Toprak
        //
        sum /= 256;
        //Karşılaştırma burada yapılacak 
        if(sum >= 150)
          metal_detected = 1;        

        //Çöp değer ataması gerçekleştirildi.Ölçüm alındı
        //metal mi değil mi?
        if(jetson_nano_signal != signal_state){
          signal_state = jetson_nano_signal;
          // If the signal is HIGH (metal detected), start the timer
          if (signal_state == 1) {
            signalStartTime = millis();
          }
        } 
        while(signal_state == 1 && signalDuration  >= millis() - signalStartTime)
        {      
        //Serial.println("1");
          metal_detected = 1;
        }//3sn boyunca metal sinyali gönderilir.                
        signal_state = 0;
        jetson_nano_signal = 0;
        //subtract minimum and maximum value to remove spikes
        sum-=minval; 
        sum-=maxval;
      }
      else if(flag == 1)
      {
        //Now send python a message if metal is detected or not
        if(metal_detected == 1){
          //metal is detected
          Serial.println("1");//which means metal
          init_value = 0;
          flag = 0;
          metal_detected = 0;
          //New code
          // waits 15ms for the servo to reach the position
          servo_init = 0;
        }
        else if(metal_detected == 0){
          Serial.println("2");//which means plastic or glass
          init_value = 0;
          flag = 0;
          //New code
          // waits 15ms for the servo to reach the position
          servo_init = 0;
        }
      }
}
