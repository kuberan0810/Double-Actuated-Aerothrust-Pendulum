unsigned long long previousmillis = 0,previousmillis1 = 0;
unsigned long long previousmillis2 = 0,previousmillis3 = 0;
int varl=0,varh=0;
int set_theta=0;
double angle=0.00;
double previous_angle = 0.0;
int theta=0,thetader=0;
double error = 0.0; 
double error_acc = 0;
double D_error = 0;
double previous_error = 0.0;
double theta_dot = 0.0;
double Kp=0.91,Kd=0.98,Ki=0.01;
double mg=1.6314;
double l=0.825;
double mgsinQ = 0.0;
double controller_out = 0.0;
double thrust = 0.0,thrustneg=0.0;
int duty_cycle =0,duty_cycle1=0;
bool BLDC_ON=0,inc=0,dec=0,plotmode=0;
const int mask1 = 31;
const byte msbmask = 32;
const byte mask =31;
void setup() 
{
  // Datasheet page 392 Encoder Interface  
  pinMode(PC13,OUTPUT);
  digitalWrite(PC13,LOW);
  Serial.begin(115200);
  Serial1.begin(115200);
  while(Serial1.available()<1);
  digitalWrite(PC13,HIGH);
  RCC_BASE->APB2ENR |= (1<<2); // Enable clock to Port A
  GPIOA_BASE->CRL |= ( (1<<3)|(1<<7) ); // PA0,PA1 as INPUT_PULLUP
  GPIOA_BASE->CRL &= ~( 1|(1<<1)|(1<<2)|(1<<4)|(1<<5)|(1<<6) );
  GPIOA_BASE->ODR |= 1|(1<<1);
  //TIMER2_BASE->CR1 = TIMER_CR1_CEN; // Enable Timer
  TIMER2_BASE->CR1 =1;
  TIMER2_BASE->CR2 = 0;
  TIMER2_BASE->SMCR |= 3; // Encoder Mode SMS = 011
  TIMER2_BASE->DIER = 0; // Disable Timer Interrupts
  TIMER2_BASE->EGR = 0;
  TIMER2_BASE->CCMR1 = 257; // Encoder Mode Enable
  TIMER2_BASE->CCMR2 = 0;   
  TIMER2_BASE->CCER = 0;
  TIMER2_BASE->PSC = 0;
  TIMER2_BASE->ARR = 3999; // 4000 Pulse Per revolution
  TIMER2_BASE->DCR = 0;
  TIMER2_BASE->CNT = 0;
  // PWM Pulse Generation
  GPIOA_BASE->CRL |= ((1<<24)|(1<<25)|(1<<27)|(1<<28)|(1<<29)|(1<<31));
  GPIOA_BASE->CRL &= ~((1<<26)|(1<<30));
  GPIOB_BASE->CRL |= (1<<23);
  GPIOB_BASE->CRL &= ~((1<<22)|(1<<21)|(1<<20));
  GPIOB_BASE->ODR &= ~(1<<5);
  TIMER3_BASE->CR1 = 1;
  TIMER3_BASE->CR2 = 0;
  TIMER3_BASE->SMCR = 0;
  TIMER3_BASE->DIER = 0;
  TIMER3_BASE->EGR = 0;
  TIMER3_BASE->CCMR1 |=((1<<11)|(1<<13)|(1<<14)|(1<<3)|(1<<5)|(1<<6));
  TIMER3_BASE->CCMR1 &= ~((1<<12)|(1<<4)); 
  TIMER3_BASE->CCMR2 = 0;
  TIMER3_BASE->CCER = (1|(1<<4));
  TIMER3_BASE->PSC = 71;
  TIMER3_BASE->ARR = 20000;
  TIMER3_BASE->DCR = 0;
  TIMER3_BASE->CNT = 0;
  TIMER3_BASE->CCR1 = 2000;
  TIMER3_BASE->CCR2 = 2000;
  delay(2000);
  TIMER3_BASE->CCR1 = 1000;
  TIMER3_BASE->CCR2 = 1000;
  delay(2000);
}

void loop() 
{
  //Read PB5 port
  plotmode = ((GPIOB_BASE->IDR)>>5)&1;
  
  if(Serial1.available()>0)         
   dataRead(Serial1.read());

   theta_change(500);  

   angle = (TIMER2_BASE->CNT)*0.09;
   theta = (int)angle;
   if (angle>180)
      angle -=360;
   if (set_theta>180)
      set_theta -=360;
      
   error = set_theta-angle;
   if (error<-180)
   error+=360;
   else if (error>180)
   error-=360;
   error = error*0.0175;
   
   errorcal(10);
   controller_out = (error*Kp) + (D_error*Kd*100) + (error_acc*Ki*0.01);
   mgsinQ = mg*sin(angle*0.01745);   
   thrust = (controller_out/l) + mgsinQ;
  
   duty_cycle = (int)((237.74*thrust)+1037.7);   
   if (duty_cycle>1700)
      duty_cycle = 1700;
      
   if (BLDC_ON==1)
   {
     if  (thrust<0)   
      {
        thrustneg = abs(thrust);
        duty_cycle1 = (int)((280.18*thrustneg)+1083.8);
        if (duty_cycle1>1700)
            duty_cycle1 = 1700;
        TIMER3_BASE->CCR1 = 1000;
        TIMER3_BASE->CCR2 = duty_cycle1;
      }
     else
      {
         TIMER3_BASE->CCR1 = duty_cycle;
         duty_cycle1 = 1000;
         TIMER3_BASE->CCR2 = duty_cycle1;
      }
   }
   else
    {
      TIMER3_BASE->CCR1 = 1000;
      TIMER3_BASE->CCR2 = 1000;
    }
  if (plotmode==1)   
    roll_graph(100);   
     
  else  
    pumpdata(40);  
}

void dataRead(byte data)
{      
  switch(data/32)
  {
    case 0:
    varl = data&mask;
    break;
    
    case 1:
    varh = data&mask;
    varh = (varh*32)+varl;   
    Kp = varh/100.0;     
    break;
    
    case 2:
    varl = data&mask;
    break;
    
    case 3:
    varh = data&mask;
    varh = (varh*32)+varl;   
    Kd = varh/100.0;     
    break;

    case 4:
    varl = data&mask;
    break;
    
    case 5:
    varh = data&mask;
    varh = (varh*32)+varl;   
    Ki = varh/100.0;
    break;

    case 6:
    varl = data&mask;
    break;
    
    case 7:
    varh = data&mask;    
    varh = (varh*32)+varl; 
    if (varh>=512)
    {
      dec = (varh&4)/4;
      inc =  (varh&2)/2;  
      BLDC_ON =  (varh&1);     
      break;
    }
    set_theta = varh;       
    break;
    default:
    break;
    
  }  
}
void errorcal(unsigned int delayy)
{     
  if ((millis()-previousmillis)>=delayy)
  {  
    theta_dot = (int)((angle-previous_angle)*1000/delayy);
    thetader=(theta_dot+1200)/3;
    D_error = error - previous_error;  
    error_acc += previous_error;
    if (error_acc>80)
    error_acc = 80;
    else if (error_acc<-80)
    error_acc = -80;
    previous_error = error;
    previous_angle = angle;
    previousmillis = millis();
    if (previousmillis > 4294967296)  
    previousmillis -= 4294967296;      
  }  
}
  void roll_graph(unsigned int delayy1)
  {
    if ((millis()-previousmillis1)>=delayy1)
    { 
                   
      Serial.print(angle);     
      Serial.print(" ");  
      Serial.print(set_theta);
      Serial.print(" "); 
      Serial.print(-180); 
      Serial.print(" ");  
      Serial.println(180);    
      /*
      Serial.print("Set theta =");
      Serial.println(set_theta);
      Serial.print(" ");
      Serial.print("Angle =");
      Serial.print(angle);
      Serial.print(" ");senddata(theta,0);
      senddata(thetader,1);
      Serial.print("Error =");    
      Serial.println(error/0.0175);
      Serial.print("Thrust =");    
      Serial.println(thrust);
      Serial.print("Duty_motor1 =");
      Serial.println(duty_cycle);
      Serial.print("Duty_motor2 =");
      Serial.println(duty_cycle1);
      */
      previousmillis1 = millis();
    }
  }

void pumpdata(unsigned int delayy2)
{
  if ((millis()-previousmillis2)>=delayy2)
  {                 
    senddata(theta,0);
    senddata(thetader,1);    
    previousmillis2 = millis();
  }
}
void theta_change(unsigned int delayy3)
{
  if ((millis()-previousmillis3)>=delayy3)
    {      
      if (inc==1)
        set_theta+=1;
      else if (dec==1)
        set_theta-=1;
      previousmillis3 = millis(); 
    }
}
void senddata(int x,byte channel)
{     
    byte valh=0,vall=0; 
    byte splitvall=x&mask1;    
    byte splitvalh=(x>>5)&mask1;   
    vall =channel<<6;
    vall+= splitvall;   
    Serial1.write(vall);    
    valh = (channel<<6)|msbmask;
    valh+= splitvalh;   
    Serial1.write(valh);      
}
