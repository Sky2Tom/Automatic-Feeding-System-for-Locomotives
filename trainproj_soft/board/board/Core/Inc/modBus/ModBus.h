/*
 * ModBus.h
 *
 *  Created on: 2018年2月5日
 *      Author: Yu
 */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef MODBUS_H_
#define MODBUS_H_
/* Includes ------------------------------------------------------------------*/
//#include "Process.h"//e_EnFlag结构体
//For Modbus
//#include  "variablelist.h"      //触摸屏要用到的全局变量声明
#include  "modBus/CRCtable.h"          //CRC冗余校验码表
#include  "modBus/ModBus_bsp.h"

/* Exported types ------------------------------------------------------------*/
/* Exported constants --------------------------------------------------------*/


/* Private define ------------------------------------------------------------*/

/* Exported macro ------------------------------------------------------------*/
/* Exported variables ---------------------------------------------------------*/
extern tUartParms UartInfo1;				//Uart数据结构
extern tUartParms UartInfo2;				//Uart数据结构

/* Exported functions ------------------------------------------------------- */
void InitModBus(tUartParms * UartInfoTmp,unsigned char Instance,e_ModBusMasterSlave MasterSlave,unsigned char MyID);//,uchar *CR_List,Uint16 *DR_List,Uint16 *IR_List);
void ModBus_TIM_Callback(tUartParms * UartInfoTmp);
void ModBus_Rcv_Callback(tUartParms * UartInfoTmp, unsigned char RcvData);
void ModBusCheck(tUartParms * UartInfoTmp);
unsigned short CRC16(unsigned char *puchMsg,unsigned int DataLen); //CRC校验码生成函数
unsigned int AnalyFrm(tUartParms * UartInfoTmp);  //分析捕获到的帧
void Deal_OKfrm(tUartParms * UartInfoTmp);        //处理经过校验后的帧



#endif /* MODBUS_H_ */
