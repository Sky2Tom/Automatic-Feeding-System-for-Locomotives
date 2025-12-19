/**
******************************************************************************
* @file    ModBus_user.c
* @author  Yu
* @version V1.0
* @date    2018年5月31日
* @brief   TODO(用一句话描述该文件做什么)
******************************************************************************
* @attention
*
*
*
******************************************************************************
*/
/* Includes ------------------------------------------------------------------*/
#include  "modBus/ModBus_user.h"
#include "modBus/Modbus.h"

//////////////////////////从机代码/////////////////////////////////////////////////////////////////
void Reply_01(tUartParms * UartInfoTmp) 				//读线圈请求
{
      //unsigned int i;
        unsigned short temp;
        unsigned short TxDataCnt = 0;
        int i = 0;
        int j =0;
        int start_byte;
        int bit_offset;
        uint16_t tmpDataNum = 0;
        uint16_t tmpDataHead = 0;
        int cur_cnt=0;//表示当前赋值完毕哪一位了

        uint8_t *tmppointer;//做一个临时的8位的指针，可以保证每次只是增加16位的大小
        tmppointer=(uint8_t*)UartInfoTmp->CoilRegisterList;

        //查询当前的位状态，
        UartInfoTmp->TxData[0] = UartInfoTmp->MyModbusID;       //站号
        UartInfoTmp->TxData[1] = 0x01;          //重复功能码
        tmpDataNum = (UartInfoTmp->RxData[4]*256+UartInfoTmp->RxData[5]);//寄存器数量
        UartInfoTmp->TxData[2] = (tmpDataNum+7)/8;  //字节计数(N:N个字节表示有8*N个线圈状态)

        //从第4个字节开始，填充数据
        TxDataCnt=3;

        tmpDataHead = (UartInfoTmp->RxData[2]*256+UartInfoTmp->RxData[3]);//寄存器起始地址
        start_byte = tmpDataHead / 8; // 计算开始字节和位偏移
        bit_offset = tmpDataHead % 8;
        if(tmpDataHead+tmpDataNum>32) return;//超界了，直接返回

        if(bit_offset==0)//正好没有位偏移
        {
            for (i = 0; i < ((tmpDataNum+7)/8); i++) {
                            uint8_t coil_byte = 0;
                            for (j =0; j < 8 && cur_cnt < tmpDataNum; j++) {
                                cur_cnt++;
                                if ( *(tmppointer+start_byte)&(1<<((bit_offset+j)%8)))
                                {
                                    coil_byte |= (1 << j);
                                }
                            }
                            start_byte++;
                            UartInfoTmp->TxData[TxDataCnt] = coil_byte;
                            TxDataCnt++;
                        }
        }
        else{
            for (i = 0; i < ((tmpDataNum+7)/8); i++) {
                            uint8_t coil_byte = 0;
                            for (j =0; j < 8 && cur_cnt < tmpDataNum; j++) {
                                cur_cnt++;
                                if((bit_offset+j)==8)//从等于8开始表示到下一个下标了
                                {
                                    start_byte++;
                                }

                                if (*(tmppointer+start_byte)&(1<<((bit_offset+j)%8)))
                                {
                                    coil_byte |= (1 << j);
                                }
                            }
                            UartInfoTmp->TxData[TxDataCnt] = coil_byte;
                            TxDataCnt++;
                        }
        }

        temp = CRC16(UartInfoTmp->TxData,TxDataCnt);
        UartInfoTmp->TxData[TxDataCnt] = temp/256;TxDataCnt++; //校验码高字节
        UartInfoTmp->TxData[TxDataCnt] = temp%256;TxDataCnt++; //校验码低字节

        ModBus1_send(UartInfoTmp,TxDataCnt);


}


void Reply_02(tUartParms * UartInfoTmp)   				//读离散量输入回复函数
{
    //unsigned int i;
           unsigned short temp;
           unsigned short TxDataCnt = 0;
           int i = 0;
           int j =0;
           uint16_t tmpDataNum = 0;
           uint16_t tmpDataHead = 0;
           int cur_cnt=0;//表示当前赋值完毕哪一位了

           uint8_t *tmppointer;//做一个临时的8位的指针，可以保证每次只是增加16位的大小
          tmppointer=(uint8_t*)UartInfoTmp->CoilRegisterList;

           //查询当前的位状态，
           UartInfoTmp->TxData[0] = UartInfoTmp->MyModbusID;       //站号
           UartInfoTmp->TxData[1] = 0x02;          //重复功能码
           tmpDataNum = (UartInfoTmp->RxData[4]*256+UartInfoTmp->RxData[5]);//寄存器数量
           UartInfoTmp->TxData[2] = (tmpDataNum+7)/8;  //字节计数(N:N个字节表示有8*N个线圈状态)             ？

           //从第4个字节开始，填充数据
           TxDataCnt=3;

           tmpDataHead = (UartInfoTmp->RxData[2]*256+UartInfoTmp->RxData[3]);//寄存器起始地址
           uint8_t start_byte = tmpDataHead / 8; // 计算开始字节和位偏移
           uint8_t bit_offset = tmpDataHead % 8;
           if(tmpDataHead+tmpDataNum>32) return;


           if(bit_offset==0)//正好没有位偏移
                   {
                       for (i = 0; i < ((tmpDataNum+7)/8); i++) {
                                       uint8_t Dis_byte = 0;
                                       for (j =0; j < 8 && cur_cnt < tmpDataNum; j++) {
                                           cur_cnt++;
                                           if (*(tmppointer+start_byte)&(1<<((bit_offset+j)%8)))
                                           {
                                               Dis_byte |= (1 << j);
                                           }
                                       }
                                       start_byte++;
                                       UartInfoTmp->TxData[TxDataCnt] = Dis_byte;
                                       TxDataCnt++;
                                   }
                   }
                   else{
                       for (i = 0; i < ((tmpDataNum+7)/8); i++) {
                                       uint8_t Dis_byte = 0;
                                       for (j =0; j < 8 && cur_cnt < tmpDataNum; j++) {
                                           cur_cnt++;
                                           if((bit_offset+j)==8)//从等于8开始表示到下一个下标了
                                           {
                                               start_byte++;
                                           }

                                           if (*(tmppointer+start_byte)&(1<<((bit_offset+j)%8)))
                                           {
                                               Dis_byte |= (1 << j);
                                           }
                                       }
                                       UartInfoTmp->TxData[TxDataCnt] = Dis_byte;
                                       TxDataCnt++;
                                   }
                   }

                   temp = CRC16(UartInfoTmp->TxData,TxDataCnt);
                   UartInfoTmp->TxData[TxDataCnt] = temp/256;TxDataCnt++; //校验码高字节
                   UartInfoTmp->TxData[TxDataCnt] = temp%256;TxDataCnt++; //校验码低字节

                   ModBus1_send(UartInfoTmp,TxDataCnt);
}

void Reply_03(tUartParms * UartInfoTmp)			      //读03保持寄存器
{
	uint16_t temp;
	uint16_t i = 0;
	uint16_t tmpData = 0;
	uint16_t tmpDataNum = 0;
	uint16_t tmpDataHead = 0;
	uint16_t *tmppointer;//做一个临时的16位的指针，可以保证每次只是增加16位的大小
	tmppointer=(uint16_t*)UartInfoTmp->DataRegisterList;
	unsigned short TxDataCnt = 0;
	UartInfoTmp->TxData[0] = UartInfoTmp->MyModbusID;           //站号
	UartInfoTmp->TxData[1] = 0x03;         //重复功能码
	UartInfoTmp->TxData[2] = (UartInfoTmp->RxData[4]*256+UartInfoTmp->RxData[5])*2;//字节计数,一个寄存器对应两个字节

	TxDataCnt = 3;


	tmpDataNum = (UartInfoTmp->RxData[4]*256+UartInfoTmp->RxData[5]);//寄存器数量
	tmpDataHead = (UartInfoTmp->RxData[2]*256+UartInfoTmp->RxData[3]);//寄存器起始地址
	if(tmpDataNum+tmpDataHead>48) return;

	for(i = 0; i < tmpDataNum; i ++)
	{
		tmpData = *(tmppointer+tmpDataHead+i);//UartInfoTmp->DataRegisterList[tmpDataHead + i];
		UartInfoTmp->TxData[TxDataCnt] = (tmpData & 0xff00)>>8;TxDataCnt ++;//寄存器2内容
		UartInfoTmp->TxData[TxDataCnt] = tmpData & 0xff;TxDataCnt ++;
	}


    temp = CRC16(UartInfoTmp->TxData,TxDataCnt);   //生成CRC校验码
    UartInfoTmp->TxData[TxDataCnt] = temp/256;TxDataCnt ++;//校验码高字节
    UartInfoTmp->TxData[TxDataCnt] = temp%256;TxDataCnt ++;//校验码低字节

	ModBus1_send(UartInfoTmp,TxDataCnt);

}

void Reply_04(tUartParms * UartInfoTmp)                      //读输入寄存器
{
    uint16_t temp;
        uint16_t i = 0;
        uint16_t tmpData = 0;
        uint16_t tmpDataNum = 0;
        uint16_t tmpDataHead = 0;
        uint16_t *tmppointer;
        tmppointer=(uint16_t*)UartInfoTmp->Zero_3RegisterList;
        unsigned short TxDataCnt = 0;
        UartInfoTmp->TxData[0] = UartInfoTmp->MyModbusID;           //站号
        UartInfoTmp->TxData[1] = 0x04;         //重复功能码
        UartInfoTmp->TxData[2] = (UartInfoTmp->RxData[4]*256+UartInfoTmp->RxData[5])*2;//字节计数

        TxDataCnt = 3;

        tmpDataNum = (UartInfoTmp->RxData[4]*256+UartInfoTmp->RxData[5]);//寄存器数量
        tmpDataHead = (UartInfoTmp->RxData[2]*256+UartInfoTmp->RxData[3]);//寄存器起始地址
        if(tmpDataNum+tmpDataHead>48) return;

        for(i = 0; i < tmpDataNum; i ++)
        {
            tmpData = *(tmppointer+tmpDataHead+i);//UartInfoTmp->InputRegisterList[tmpDataHead + i];
            UartInfoTmp->TxData[TxDataCnt] = (tmpData & 0xff00)>>8;TxDataCnt ++;//寄存器2内容
            UartInfoTmp->TxData[TxDataCnt] = tmpData & 0xff;TxDataCnt ++;
        }

        temp = CRC16(UartInfoTmp->TxData,TxDataCnt);   //生成CRC校验码
        UartInfoTmp->TxData[TxDataCnt] = temp/256;TxDataCnt ++;//校验码高字节
        UartInfoTmp->TxData[TxDataCnt] = temp%256;TxDataCnt ++;//校验码低字节

        ModBus1_send(UartInfoTmp,TxDataCnt);

}

void Reply_05(tUartParms * UartInfoTmp)            		    //写单个线圈请求
{
	unsigned short temp;
	uint16_t tmpDataHead = 0;
	uint8_t *tmppointer;//做一个临时的8位的指针，可以保证每次只是增加16位的大小
	tmppointer=(uint8_t*)UartInfoTmp->CoilRegisterList;

	tmpDataHead = UartInfoTmp->RxData[2]*256+	UartInfoTmp->RxData[3];
	if(tmpDataHead>32) return;

    if(UartInfoTmp->RxData[4] == 0xff && UartInfoTmp->RxData[5] == 0x00)//置1
    {
        *(tmppointer+tmpDataHead/8) |= 1<<(tmpDataHead%8);
    }
    else if(UartInfoTmp->RxData[4] == 0x00 && UartInfoTmp->RxData[5] == 0x00)//置0
    {
        *(tmppointer+tmpDataHead/8) &= ~(1<<(tmpDataHead%8));
    }
    else//error
    {
    	return;
    }

    UartInfoTmp->TxData[0] = UartInfoTmp->MyModbusID;         		    //站号
    UartInfoTmp->TxData[1] = 0x05;         		    //功能码
    UartInfoTmp->TxData[2] = UartInfoTmp->RxData[2];        //地址高位
    UartInfoTmp->TxData[3] = UartInfoTmp->RxData[3];        //地址低位
    UartInfoTmp->TxData[4] = UartInfoTmp->RxData[4];        //输出值高位
    UartInfoTmp->TxData[5] = UartInfoTmp->RxData[5];        //输出值低位

	temp = CRC16(UartInfoTmp->TxData,6);   		    //生成CRC校验码
	UartInfoTmp->TxData[6] = temp/256;     		    //校验码高字节
	UartInfoTmp->TxData[7] = temp%256;     		    //校验码低字节

	ModBus1_send(UartInfoTmp,8); 					    //发送
}

void Reply_06(tUartParms * UartInfoTmp)					    //写寄存器请求
{
	unsigned short temp;
	uint16_t *tmppointer;
	uint16_t tmpDataHead = 0;
	tmppointer=(uint16_t*)UartInfoTmp->DataRegisterList;
	tmpDataHead = UartInfoTmp->RxData[2]*256+UartInfoTmp->RxData[3];//地址
	if(tmpDataHead>32) return;

	 *(tmppointer+tmpDataHead)= UartInfoTmp->RxData[4]*256+UartInfoTmp->RxData[5];//数据赋值  UartInfoTmp->DataRegisterList[tmpDataHead]

	UartInfoTmp->TxData[0] = UartInfoTmp->MyModbusID;         		    //站号
	UartInfoTmp->TxData[1] = 0x06;         		    //功能码
	UartInfoTmp->TxData[2] = UartInfoTmp->RxData[2];        //地址高位
	UartInfoTmp->TxData[3] = UartInfoTmp->RxData[3];        //地址低位
	UartInfoTmp->TxData[4] = UartInfoTmp->RxData[4];        //输出值高位
	UartInfoTmp->TxData[5] = UartInfoTmp->RxData[5];        //输出值低位

    temp = CRC16(UartInfoTmp->TxData,6);   				//生成CRC校验码
    UartInfoTmp->TxData[6] = temp/256;     				//校验码高字节
    UartInfoTmp->TxData[7] = temp%256;     				//校验码低字节

    ModBus1_send(UartInfoTmp,8); 									//发送
//    MyFlashWrite(0,DataRegisterList,1024);
}

//写多个线圈
void Reply_0F(tUartParms * UartInfoTmp)
{
	unsigned short temp;
	uint16_t tmpDataNum = 0;
	uint16_t tmpDataHead = 0;
	int i=0;
	int j=0;
	int start_byte;
	int bit_offset;
	int cur_cnt=0;//表示当前赋值完毕哪一位了
	uint8_t *tmppointer;//做一个临时的8位的指针，可以保证每次只是增加16位的大小
	tmppointer=(uint8_t*)UartInfoTmp->CoilRegisterList;

	tmpDataNum = (UartInfoTmp->RxData[4]*256+UartInfoTmp->RxData[5]);//寄存器数量

	tmpDataHead = (UartInfoTmp->RxData[2]*256+UartInfoTmp->RxData[3]);//寄存器起始地址
	           start_byte = tmpDataHead / 8; // 计算开始字节和位偏移
	           bit_offset = tmpDataHead % 8;
	           if(tmpDataHead+tmpDataNum>32) return;

	          if(bit_offset==0)//正好没有位偏移
	          {
	              for (i = 0; i < UartInfoTmp->RxData[6]; i++)
	              {
	                    for (j =0; j < 8 && cur_cnt < tmpDataNum; j++) {
	                         cur_cnt++;
	                      if ((UartInfoTmp->RxData[7+i] & (1 << j)) >>j)//如果数据对应的第j位为1，则给线圈该位赋值为1
	                           {
	                          *(tmppointer+start_byte) |= 1<<((j+bit_offset)%8);
	                           }
	                      else
	                           {
	                          *(tmppointer+start_byte) &=~ (1<<((j+bit_offset)%8));//对应位为0,则赋值为0
	                           }
	                 }
	                    start_byte++;
	               }

	          }
	          else{
	              for (i = 0; i < UartInfoTmp->RxData[6]; i++) {
	                 for (j =0; j < 8 && cur_cnt < tmpDataNum; j++) {
	                    cur_cnt++;
	                    if((bit_offset+j)==8)//等于8表示到下一个下标了
	                    {
	                         start_byte++;
	                    }
	                    if ((UartInfoTmp->RxData[7+i] & (1 << j)) >>j)//如果数据对应的第j位为1，则给线圈该位赋值为1
	                    {
	                        *(tmppointer+start_byte)  |= 1<<((j+bit_offset)%8);
	                    }
	                    else
	                    {
	                        *(tmppointer+start_byte)  &=~ (1<<((j+bit_offset)%8));//对应位为0,则赋值为0
	                    }
	                   }
	          }
	          }

	UartInfoTmp->TxData[0] = UartInfoTmp->MyModbusID;         		    //站号
	UartInfoTmp->TxData[1] = 0x0F;         		    //功能码
	UartInfoTmp->TxData[2] = UartInfoTmp->RxData[2];        //地址高位
	UartInfoTmp->TxData[3] = UartInfoTmp->RxData[3];        //地址低位
	UartInfoTmp->TxData[4] = UartInfoTmp->RxData[4];        //输出值高位
	UartInfoTmp->TxData[5] = UartInfoTmp->RxData[5];        //输出值低位

    temp = CRC16(UartInfoTmp->TxData,6);   				//生成CRC校验码
    UartInfoTmp->TxData[6] = temp/256;     				//校验码高字节
    UartInfoTmp->TxData[7] = temp%256;     				//校验码低字节

    ModBus1_send(UartInfoTmp,8); 									//发送
}

//写多个保持寄存器
void Reply_10(tUartParms * UartInfoTmp)
{
	unsigned short temp;
	uint16_t tmpDataNum = 0;
	uint16_t tmpDataHead = 0;
	unsigned char i = 0;
	uint16_t *tmppointer;
	tmppointer=(uint16_t*)UartInfoTmp->DataRegisterList;

	tmpDataNum = UartInfoTmp->RxData[4]*256 +	UartInfoTmp->RxData[5];//读数量
	tmpDataHead = UartInfoTmp->RxData[2]*256 +	UartInfoTmp->RxData[3];//读地址
	if(tmpDataHead+tmpDataNum>32) return;

	for(i = 0; i < tmpDataNum; i ++)
	{
//			dataList[i] = UartInfoTmp->RxData[2*i+7]*256+UartInfoTmp->RxData[2*i+8];
	    *(tmppointer+i+tmpDataHead)=  UartInfoTmp->RxData[2*i+7]*256+UartInfoTmp->RxData[2*i+8];;// UartInfoTmp->DataRegisterList[i+tmpDataHead]
	}


	UartInfoTmp->TxData[0] = UartInfoTmp->MyModbusID;         		    //站号
	UartInfoTmp->TxData[1] = 0x10;         		    //功能码
	UartInfoTmp->TxData[2] = UartInfoTmp->RxData[2];        //地址高位
	UartInfoTmp->TxData[3] = UartInfoTmp->RxData[3];        //地址低位
	UartInfoTmp->TxData[4] = UartInfoTmp->RxData[4];        //数量高位
	UartInfoTmp->TxData[5] = UartInfoTmp->RxData[5];        //数量低位

    temp = CRC16(UartInfoTmp->TxData,6);   				//生成CRC校验码
    UartInfoTmp->TxData[6] = temp/256;     				//校验码高字节
    UartInfoTmp->TxData[7] = temp%256;     				//校验码低字节

    ModBus1_send(UartInfoTmp,8); //发送
}

