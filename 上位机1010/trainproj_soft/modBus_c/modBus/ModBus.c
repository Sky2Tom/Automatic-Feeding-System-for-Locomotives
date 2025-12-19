/*
 * ModBus.c
 *
 *  Created on: 2018年2月5日
 *      Author: Yu
 */

/* Includes --------------------------------------------z----------------------*/
#include  "modBus/ModBus.h"
#include  "modBus/ModBus_user.h"
#include  "modBus/ModBus_content.h"



tUartParms UartInfo1;				//Uart数据结构

/* Private function prototypes -----------------------------------------------*/
/* Private functions ---------------------------------------------------------*/
/**
  * @brief  modBus初始化函数,初始化相关变量.
  * @param  * UartInfoTmp: modBus实例化变量指针
  * @param  Instance: modBus实例化标志号,值为0~255的宏
  * @param  MyID: modBus实例化标ID,值为1~255,当为主机时该值为0
	* @param  e_ModBusMasterSlave:主站还是从站
  * @retval None
  */
void InitModBus(tUartParms * UartInfoTmp,unsigned char Instance,e_ModBusMasterSlave MasterSlave,unsigned char MyID)//初始化modbus 通讯信息结构、实例、站地址
{
	UartInfoTmp->Instance = Instance;
	UartInfoTmp->MasterSlave = MasterSlave;
	UartInfoTmp->MyModbusID = MyID;//站地址

	// 全局变量定义
	UartInfoTmp->ModBusTxID = 1;
	UartInfoTmp->EnSendModBus = EnFlagFalse;
	UartInfoTmp->Mdbs_Send_TimerCnt = 0;


	UartInfoTmp->Mdbs_EnTimerCnt = EnFlagFalse;
	UartInfoTmp->Mdbs_TimerCnt = 0;
	UartInfoTmp->Mdbs_EnRcvCheck = EnFlagFalse;

	UartInfoTmp->RxTimes=0;
}


/**
  * @brief  在Tim中断回调函数中调用,需要0.1ms的中断.
  * @param  None
  * @retval None
  */
void ModBus_TIM_Callback(tUartParms * UartInfoTmp)
{
	if(UartInfoTmp->Mdbs_EnTimerCnt == EnFlagTrue)
	{
		UartInfoTmp->Mdbs_TimerCnt ++;
		if(UartInfoTmp->Mdbs_TimerCnt > 35)//3.5ms
		{
			UartInfoTmp->Mdbs_TimerCnt = 0;//清计数
			UartInfoTmp->Mdbs_EnRcvCheck = EnFlagTrue;//标志位
			UartInfoTmp->Mdbs_EnTimerCnt = EnFlagFalse;//关定时器计数
		}
	}
}

/**
  * @brief  在串口接收中断回调函数中调用.
  * @param  None
  * @retval None
  */
void ModBus_Rcv_Callback(tUartParms * UartInfoTmp, unsigned char RcvData)//SCIRXBUF每次只能够接收一个字节
{

	UartInfoTmp->RxCurData  =  RcvData & 0xff;//获取数据
	 if(UartInfoTmp->RxTimes == 0)
	{
		 UartInfoTmp->RxData[0] =  UartInfoTmp->RxCurData; //保存帧地址字节，先不急于判断
		 UartInfoTmp->RxAddr    =  UartInfoTmp->RxCurData; //保存帧地址字节
		 UartInfoTmp->RxTimes   =  1;                  //已经接收一个地址字节

		 UartInfoTmp->Mdbs_TimerCnt = 0;//清计数
		 UartInfoTmp->Mdbs_EnTimerCnt = EnFlagTrue;//开定时器计数
	}
      else	//已经进入帧接收状态了
	{
		UartInfoTmp->RxData[UartInfoTmp->RxTimes] = UartInfoTmp->RxCurData; //接收到数据存放在数据缓存中
		UartInfoTmp->RxTimes++;
		if(UartInfoTmp->RxTimes==2)
		   UartInfoTmp->RxFuncID = UartInfoTmp->RxCurData; //保存帧ID号
		UartInfoTmp->Mdbs_TimerCnt = 0;//清计数
		UartInfoTmp->Mdbs_EnTimerCnt = EnFlagTrue;//开定时器计数
	}
}

/**
  * @brief  在main函数的主循环中调用.
  * @param  None
  * @retval None
  */
void ModBusCheck(tUartParms * UartInfoTmp)//检查是不是捕捉了数据帧，并且处理
{
	//For ModBus
	if(UartInfoTmp->Mdbs_EnRcvCheck == EnFlagTrue)    //帧计时器超时,表明已经在信道中捕获了一个数据帧，帧通过帧间间隔时间分开
	{
		UartInfoTmp->Mdbs_TimerCnt = 0;//清计数
		UartInfoTmp->Mdbs_EnRcvCheck = EnFlagFalse;//清标志位
		UartInfoTmp->Mdbs_EnTimerCnt = EnFlagFalse;//关定时器计数
		//-----分析信道中捕获的帧,返回帧的状态参数-----
		UartInfoTmp->Mdbs_state = AnalyFrm(UartInfoTmp);
		//-----------管理事件计数器-------------
		UartInfoTmp->MdbsCNT.CRCerr_CNT += UartInfoTmp->Mdbs_state&CRC_err;
		UartInfoTmp->MdbsCNT.Addrerr_CNT+= UartInfoTmp->Mdbs_state&ADDR_err;
		UartInfoTmp->MdbsCNT.IDerr_CNT  += UartInfoTmp->Mdbs_state&FuncID_err;
		UartInfoTmp->MdbsCNT.Frabrk_CNT += UartInfoTmp->Mdbs_state&Frame_broken;
		UartInfoTmp->MdbsCNT.Frame_CNT  += UartInfoTmp->Mdbs_state&Frame_OK;    //记录正确帧的帧数
		//-----------事件计数器管理结束--------------

		//-----------正常帧处理-------------
		if(UartInfoTmp->Mdbs_state&Frame_OK)
		{
			Deal_OKfrm(UartInfoTmp);         //处理正确的帧,包括向触摸屏回送状态信息
		}
		//-----------处理完帧之后需要对计数器进行清零处理,正常帧和错误帧都要清零------
		UartInfoTmp->RxTimes  = 0;
		UartInfoTmp->RxAddr   = 0;
		UartInfoTmp->RxFuncID = 0;
		//-----------帧处理结束之后，关闭定时器，等待下个帧的首字节-------


	}//end of if(Mdbs_EnRcvCheck == EnFlagTrue)
}
//================分析捕获的数据帧=====================
unsigned int AnalyFrm(tUartParms * UartInfoTmp)
{
    uint16_t  Mdbs;
    unsigned short CRC_cacul;
    Mdbs = 0;
    if(UartInfoTmp->MasterSlave ==ModBusFlag_Slave)//从机
    {
      	if(UartInfoTmp->RxAddr!=UartInfoTmp->MyModbusID)	//判断站号
     			Mdbs =  Mdbs|ADDR_err;
    }
	if(UartInfoTmp->RxTimes>256)						       //判断帧长
		Mdbs =  Mdbs|Length_err;
	if(UartInfoTmp->RxFuncID>127)   						   //判断功能码
		Mdbs =  Mdbs|FuncID_err;
	else      										//功能码正确，接下来判断有无破损帧
	{
		if(UartInfoTmp->MasterSlave ==ModBusFlag_Slave)//从机
		{
			switch(UartInfoTmp->RxFuncID)
			{
				case 0x01:
				case 0x02:
				case 0x03:
				case 0x04:	if(UartInfoTmp->RxTimes!= 8)  Mdbs =  Mdbs|Frame_broken;  break;
				case 0x05:							    						  break;
				case 0x06:							    						  break;
				case 0x0F:							    						  break;
				case 0x10:							    						  break;
				default:							    						  break;
			}
		}
	}

    if(Mdbs == 0)								 //如果前面的错误都没有，则核对计算校验码
	{
    	if(UartInfoTmp->RxTimes > 2)
    	{
			CRC_cacul = CRC16(UartInfoTmp->RxData,UartInfoTmp->RxTimes-2);  //计算CRC校验码
			if((UartInfoTmp->RxData[UartInfoTmp->RxTimes-2]<<8|UartInfoTmp->RxData[UartInfoTmp->RxTimes-1])== CRC_cacul)
				Mdbs = Frame_OK;			        //CRC校验码低位在前，高位在后,此为最终确认的正确帧
			else
				Mdbs = Mdbs|CRC_err;
    	}
    	else
    	{
    		Mdbs = Mdbs|CRC_err;
    	}
	}
	return 	Mdbs;								  //返回Modbus的故障状态，正常与否
}



//==============CRC校验码生成函数=================
//参数：  校验数据区指针，校验数据长度
//返回值：如果校验值和接收到的CRC值相同，则为真的，否则为零
//
unsigned short CRC16(unsigned char *puchMsg,unsigned int usDataLen)                   //                  ？
{
	unsigned char uchCRCHi = 0xFF ; /* 高CRC字节初始化  */
	unsigned char uchCRCLo = 0xFF ; /* 低CRC 字节初始化 */
	unsigned uIndex ;				/* CRC循环中的索引  */
//	unsigned int dataLenTmp = 0;

//	dataLenTmp = (unsigned int) (sizeof(puchMsg) / sizeof(unsigned char));
	if(usDataLen > MaxLen)//dataLenTmp)//超出数组范围
	{
		return 0xFFFF;
	}

	while (usDataLen--) 			/* 传输消息缓冲区   */
	{
		uIndex = uchCRCHi ^ *puchMsg++ ; /* 计算CRC */
		uchCRCHi = uchCRCLo ^ auchCRCHi[uIndex];
		uchCRCLo = auchCRCLo[uIndex] ;
	}
	return (uchCRCHi << 8 | uchCRCLo) ;

}

//===========得到正确的帧后，进行帧信息回送==============
void Deal_OKfrm(tUartParms * UartInfoTmp)
{
	if(UartInfoTmp->MasterSlave == ModBusFlag_Slave)//从机
	{
		switch(UartInfoTmp->RxFuncID)
		{
			case 0x01:  Reply_01(UartInfoTmp);	break;    //读线圈请求(读写类型)
			case 0x02:  Reply_02(UartInfoTmp);	break;    //读离散量输入(只读类型)
			case 0x03:  Reply_03(UartInfoTmp);	break;    //读保持寄存器(读写类型)
			case 0x04:  Reply_04(UartInfoTmp);	break;    //读输入寄存器(只读类型)
			case 0x05:  Reply_05(UartInfoTmp);	break;    //写单个线圈
			case 0x06:  Reply_06(UartInfoTmp);	break;    //写单个保持寄存器
			case 0x0F:  Reply_0F(UartInfoTmp);  break;    //写多个线圈
			case 0x10:  Reply_10(UartInfoTmp);  break;    //写多个保持寄存器
			default:	  				 break;
		}
	}
	else
	{
		
	}

}


