/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef MODBUS_USER_H_
#define MODBUS_USER_H_
/* Includes ------------------------------------------------------------------*/
#include  "modBus/ModBus.h"
#include  "modBus/ModBus_bsp.h"

void Reply_01(tUartParms * UartInfoTmp);     	//处理读线圈请求(0x设备类型)，  可读可写
void Reply_02(tUartParms * UartInfoTmp);     	//处理读离散量请求(1x设备类型)，只能读
void Reply_03(tUartParms * UartInfoTmp);     	//处理读保持寄存器(3x设备类型)
void Reply_04(tUartParms * UartInfoTmp);     	//处理读输入寄存器(4x设备类型)
void Reply_05(tUartParms * UartInfoTmp);     	//处理写单个线圈请求
void Reply_06(tUartParms * UartInfoTmp);     	//处理写单个保持寄存器请求
void Reply_0F(tUartParms * UartInfoTmp);     	//写多个线圈
void Reply_10(tUartParms * UartInfoTmp);     	//写多个保持寄存器

#endif /* MODBUS_USER_H_ */
