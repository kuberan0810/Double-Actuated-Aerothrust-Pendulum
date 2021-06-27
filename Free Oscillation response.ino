bool flag=0;
unsigned long long prevmillis=0;
float timee=0.0;
void setup() 
{
  // Datasheet page 392 Encoder Interface
  Serial.begin(115200);
  RCC_BASE->APB2ENR |= (1<<2); // Enable clock to Port A
  // PA0,PA1 as INPUT_PULLUP
  GPIOA_BASE->CRL |= ((1<<3)|(1<<7)); 
  GPIOA_BASE->CRL &= ~(1|(1<<1)|(1<<2)|(1<<4)|(1<<5)|(1<<6));
  GPIOA_BASE->ODR |= 1|(1<<1);  
  //TIMER2_BASE->CR1 =1;
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
  TIMER2_BASE->CR1 =1; // Timer 2 Enable
  GPIOB_BASE->CRL |= (1<<23);
  GPIOB_BASE->CRL &= ~((1<<22)|(1<<21)|(1<<20));
  GPIOB_BASE->ODR &= ~(1<<5);  
}

void loop() 
{    
  flag = ((GPIOB_BASE->IDR)>>5)&1;      
  printdata(10);  
}
void printdata(int delayy)
{
  if ((millis()-prevmillis)>=delayy)
  {
    if (flag==1)
    {
      Serial.println((TIMER2_BASE->CNT)*0.09);
      timee= millis()/1000.0;
      Serial.println(timee);
    }
    prevmillis = millis();
  }
}
