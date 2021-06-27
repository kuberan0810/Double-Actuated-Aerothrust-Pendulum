unsigned int dutycycle =1050,dutycycle1=1050;
float angle=0;
bool flag=0;
void setup() 
{
  // Datasheet page 392 Encoder Interface
  Serial.begin(115200);
  RCC_BASE->APB2ENR |= (1<<2); // Enable clock to Port A
  // PA0,PA1 as INPUT_PULLUP
  GPIOA_BASE->CRL |= ((1<<3)|(1<<7)); 
  GPIOA_BASE->CRL &= ~(1|(1<<1)|(1<<2)|(1<<4)|(1<<5)|(1<<6));
  GPIOA_BASE->ODR |= 1|(1<<1);  
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
  // PWM Pulse Generation// PA6 as Output PWM
  GPIOA_BASE->CRL |= ((1<<24)|(1<<25)|(1<<27)|(1<<28)|(1<<29)|(1<<31)); 
  GPIOA_BASE->CRL &= ~((1<<30)|(1<<26)); 
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
  flag = ((GPIOB_BASE->IDR)>>5)&1;      
  if (flag==0)
    {
      Serial.println(dutycycle);      
      dutycycle+=10;          
    }
  else
  {
    Serial.println(dutycycle1);    
    dutycycle1+=10;          
  } 
  angle = (TIMER2_BASE->CNT)*0.09;
  if (angle>180)
  angle =360-angle;
  Serial.println(angle); 
  if (dutycycle>1700)
  dutycycle=1700; 
  if (dutycycle1>1700)
  dutycycle1=1700;
  TIMER3_BASE->CCR2 = dutycycle1; 
  TIMER3_BASE->CCR1 = dutycycle; 
  delay(7000);  
}

