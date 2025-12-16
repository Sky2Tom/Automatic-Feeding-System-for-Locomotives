/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef MODBUSBSP_H_
#define MODBUSBSP_H_
/* Includes ------------------------------------------------------------------*/
#include  "modBus/ModBus_content.h"

/* Exported types ------------------------------------------------------------*/
typedef enum
{
	EnFlagFalse = 0x33,//False
	EnFlagTrue = 0x55,//True
	UnWantedEnFlag = 0x72//error
} e_EnFlag;


/* Private define ------------------------------------------------------------*/
#define MaxLen  99
#define MaxModBusNum	49
#define FirstModBusNum	0
#define MODBUS1_INSTANCE	0x01
#define MODBUS2_INSTANCE	0x02
#define MODBUS3_INSTANCE	0x03
#define MODBUS4_INSTANCE	0x04
#define MODBUS5_INSTANCE	0x05
#define MODBUS6_INSTANCE	0x06
#define MODBUS7_INSTANCE	0x07
#define MODBUS8_INSTANCE	0x08
#define MODBUS9_INSTANCE	0x09


typedef enum
{
	ModBusFlag_Master = 0x33,//Master
	ModBusFlag_Slave = 0x55,//Slave
	UnWantedModBusMasterSlave = 0x72//error
} e_ModBusMasterSlave;//指示主站还是从站的

//=================================事件计数结构体=======================================
typedef struct tagModbusCount
{
unsigned int CRCerr_CNT;   		//CRC帧校验出错次数
unsigned int Chara_OvrTime;     //字符超时次数计数
unsigned int Addrerr_CNT;       //地址出错次数
unsigned int IDerr_CNT;         //ID出错次数
unsigned int Frabrk_CNT;	    //残破帧次数
unsigned int Frame_CNT; 		//接收的数据帧帧数
} tModbusCount;

/*---------------事件计数结构体定义结束---------------*/
//================================ Uart参数结构体定义 ===============================
typedef struct UartParms
{
	unsigned char Instance;//
	e_ModBusMasterSlave MasterSlave;

    //从机数据指针
    CoilRegister *CoilRegisterList;//线圈寄存器
//  DiscreteInputRegister *DiscreteInputRegisterList;//离散输入寄存器
    DataRegister *DataRegisterList;//保持寄存器
    Zero_3Register *Zero_3RegisterList;
//  InputRegister *InputRegisterList;//输入寄存器

	//主机数据指针
//	uchar (*Slave_CR_List)[MAX_SLAVE_CR_NUM];
//	uint16_t (*Slave_DR_List)[MAX_SLAVE_DR_NUM];
//	uint16_t (*Slave_IR_List)[MAX_SLAVE_IR_NUM];

	//Master
	unsigned char ModBusTxID;// = 1;
	unsigned char ModBusTxFistID;//从机轮寻首地址
	unsigned char ModBusTxMaxID;//从机轮寻末地址
	e_EnFlag EnSendModBus;// = EnFlagFalse;
	unsigned int Mdbs_Send_TimerCnt;// = 0;发送的计时
	unsigned int  Mdbs_Send_TimerCntPeriod;//中断计数周期/即主机发送时间间隔

	// 全局变量定义
	uint16_t Mdbs_state;
	uint16_t ReceivedChar;

	e_EnFlag Mdbs_EnTimerCnt;// = EnFlagFalse;接受计时标志位，如果为true则可以计数，否则在定时器回调函数中不能够计数
	uint16_t Mdbs_TimerCnt;// = 0;接受计时数
	uint16_t Mdbs_EnRcvCheck;// = EnFlagFalse; 接收帧检验，如果是true代表为新的帧

	tModbusCount MdbsCNT;

	unsigned char MyModbusID;// = 0;站地址

	unsigned char RxCurData;            //接收的当前数据
    unsigned char RxAddr;               //帧地址
    unsigned char RxFuncID;				//接收的功能码标识
    unsigned char RxData[MaxLen];    	//接收数据缓存，对应正好每一个单位是八个bit，即意味着每一个单位等于两个16位的字符,只读功能码收到的是8个字节
    unsigned int  RxTimes;              //接收字节计数，每两个16位的字符对应着一个字节。第一个字节应该是站地址ID，第二个字节是功能码
    unsigned int  RxCRC;           		//校验和CRC校验码

    unsigned char TxCurData;            //接收的当前数据
    unsigned char TxAddr;				//发送的功能码标识
	unsigned char TxFuncID;
    unsigned char TxData[MaxLen];       //发送字节计数
    unsigned int  TxTimes;              //发送字节计数
    unsigned int  TxCRC;			    //发送数据的CRC校验码
} tUartParms;
/*---------------异步通信口1结构体定义结束---------------*/


#define HIVaddr    0x01  //变频器地址
//modbus所处的状态
#define CRC_err      0x0001 //接收到完整的帧后校验错误  0000 0001
#define ADDR_err     0x0002 //帧地址不正确			  0000 0010
#define Length_err   0x0004 //帧长超过标准			  0000 0100
#define FuncID_err 	 0x0008 //帧ID越界错误			  0000 1000
#define Frame_broken 0x0010 //帧是残破的				  0001 0000
#define Frame_OK	 0x0020 //帧正确 					  0010 0000

//数值常数
#define True   1
#define False  0
/* Exported macro ------------------------------------------------------------*/
//extern UART_HandleTypeDef huart1;//估计是不需要吧
/* Exported functions ------------------------------------------------------- */
void ModBus1_send(tUartParms * UartInfoTmp, uint16_t n);  	//发送数据
#endif /* MODBUSBSP_H_ */
/******************* (C) COPYRIGHT YuRobo *****END OF FILE****/
