/**
  ******************************************************************************
  * @file    gpio.c
  * @brief   This file provides code for the configuration
  *          of all used GPIO pins.
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "gpio.h"


/* USER CODE BEGIN 0 */
#include "tim.h"
#include "usart.h"
#include  "modBus/ModBus_content.h"
#define IN1 GPIO_PIN_12
#define IN2 GPIO_PIN_13
#define IN3 GPIO_PIN_14
#define IN4 GPIO_PIN_15
#define IN5 GPIO_PIN_8
#define IN6 GPIO_PIN_9
#define IN7 GPIO_PIN_10
#define IN8 GPIO_PIN_11


//volatile uint32_t firstRiseTime = 0; // 第一次上升沿时间
//volatile uint32_t secondRiseTime = 0; // 第二次上升沿时间
//volatile uint8_t edgeCount = 0; // 边沿计数
/* USER CODE END 0 */

/*----------------------------------------------------------------------------*/
/* Configure GPIO                                                             */
/*----------------------------------------------------------------------------*/
/* USER CODE BEGIN 1 */

/* USER CODE END 1 */

/** Configure pins as
        * Analog
        * Input
        * Output
        * EVENT_OUT
        * EXTI
*/
void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);

  /*Configure GPIO pin : PC13 */
  GPIO_InitStruct.Pin = GPIO_PIN_13;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pins : PB12 PB13 PB14 PB15 */
  GPIO_InitStruct.Pin = GPIO_PIN_12|GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /*Configure GPIO pins : PA8 PA9 PA10 PA11 */
  GPIO_InitStruct.Pin = GPIO_PIN_8|GPIO_PIN_9|GPIO_PIN_10|GPIO_PIN_11;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI9_5_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);

  HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);

}

/* USER CODE BEGIN 2 */
/**
  * 函    数：LED1开启
  * 参    数：无
  * 返 回 值：无
  */
void LED0_ON(void)
{
	  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
}

/**
  * 函    数：LED1关闭
  * 参    数：无
  * 返 回 值：无
  */
void LED0_OFF(void)
{
		HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
}

/**
  * 函    数：LED1状态翻转
  * 参    数：无
  * 返 回 值：无
  */
void LED0_Turn(void)
{
	if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET)		//获取输出寄存器的状态，如果当前引脚输出低电平
	{
		HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);					//则设置PA1引脚为高电平
	}
	else													//否则，即当前引脚输出高电平
	{
		HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);					//则设置PA1引脚为低电平
	}
}
uint16_t calc_time_diff(EdgeCapture_t cap) {
    if (cap.capture_flag != 1) return 0; // 未完成捕获
		LED0_OFF();
    uint32_t total_ticks = cap.overflow_count * 0xFFFF+cap.end_val - cap.start_val; // 溢出补偿
    return total_ticks*1e-6; // 单位us
}


void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
	uint32_t currentTime = __HAL_TIM_GET_COUNTER(&htim3); // 获取当前计数值
  if (GPIO_Pin == IN1) { // 如果是IN1中断
		edge_cap[0].start_val=currentTime;
		edge_cap[0].overflow_count=0;
		edge_cap[0].capture_flag=1;
		LED0_ON();
	}
	if (GPIO_Pin == IN2) { // 如果是IN2中断
		edge_cap[0].end_val=currentTime;
		uint16_t timeDiff = calc_time_diff(edge_cap[0]);
		DataRegisterList1.DC_current_range=timeDiff;//给速度赋值
		edge_cap[0].capture_flag=0;
	}
//    if (edgeCount == 0) {
//			LED0_ON();
//      firstRiseTime = HAL_GetTick(); // 或用TIM计数器的值（更精确）
//      edgeCount = 1;
//    } else if (edgeCount == 1) {
//      secondRiseTime = HAL_GetTick();
//      uint32_t timeDiff = secondRiseTime - firstRiseTime; // 时间差（毫秒）
//      // 处理时间差数据（如打印或存储）
//      edgeCount = 0; // 重置计数
//			LED0_OFF();
//    }
}

/* USER CODE END 2 */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
