#include "modBus/ModBus_content.h"
#include "modBus/ModBus_user.h"

//线圈寄存器(PLC地址0x00001-0x09999),PLC输出引脚,网球机中做为控制状态寄存器使用
//uchar CoilRegisterList1[MAX_CR_NUM1]={56,34,73,68,89};
CoilRegister CoilRegisterList1;

//保持寄存器(PLC地址0x40001-0x49999),ModBus可读可写
//Uint16 DataRegisterList1[MAX_DR_NUM1]={0x0536,0x3344,0x0743,0x0654,0x8139,0x0536,0x3344,0x0743,0x0654,0x8139};
DataRegister  DataRegisterList1;

//输入寄存器(PLC地址0x30001-0x39999),ModBus只读
//Uint16 InputRegisterList1[MAX_IR_NUM1]={0x0536,0x3344,0x0743,0x0654,0x8139,0x0536,0x3344,0x0743,0x0654,0x8139};
Zero_3Register Zero_3RegisterList1;



void initModbusData(void)
	{
		DataRegisterList1.AC_range=0x1223;
		DataRegisterList1.DC_current_range=0x0000;
		DataRegisterList1.fire_display_ratio=0x0654;
		DataRegisterList1.DC_feedback_amplitude=0x8139;
		DataRegisterList1.AC_feedback_amplitude=0x0536;
		DataRegisterList1.extern_given_amplitude=0x0743;
	}
