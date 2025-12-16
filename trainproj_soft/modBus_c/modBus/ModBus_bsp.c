/**
******************************************************************************
* @file    ModBus_bsp.c
* @author  Yu
* @version V1.0
* @date    2018年5月31日
* @brief   BSP(board support package)是板级支持包，争取作到移植时仅修改该文件
******************************************************************************
* @attention
*
*
*
******************************************************************************
*/
/* Includes ------------------------------------------------------------------*/
#include  "modBus/ModBus_bsp.h"
#include  "modBus/ModBus.h"
#include  "usart.h"


/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
/* Private function prototypes -----------------------------------------------*/
/* Private functions ---------------------------------------------------------*/

void ModBus1_send(tUartParms * UartInfoTmp, uint16_t n)  //发送n个字节
{
//	Uint16 i;
//	if(UartInfoTmp->Instance == UartInfo1.Instance)//判断是实例1，则用串口2发送
//	{
		HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
		HAL_Delay(1);
		HAL_UART_Transmit(&huart2,UartInfoTmp->TxData,n,0xffff);
		HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
//	}
}




/**
  * @}
  */ 

/******************* (C) COPYRIGHT YuRobo *****END OF FILE****/
