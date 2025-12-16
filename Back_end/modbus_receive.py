#-----------------------------------------------------接受modbus帧-------------------------------------------------------------
# tUartParms类主要负责：存储和管理 ModBus 通信相关的参数和状态信息
class tUartParms:
    def __init__(self):
        self.Instance = 0                   # ModBus实例编号（0~255），用于区分多个 ModBus 实例
        self.MasterSlave = 0                # 主从模式标志（ModBusFlag_Master 或 ModBusFlag_Slave） 
        self.MyModbusID = 0                 # 设备地址（1~255），主机时为 0
        self.ModBusTxID = 1                 # 发送帧的 ID（默认为 1）
        self.EnSendModBus = EnFlagFalse     # 发送使能标志（EnFlagTrue/EnFlagFalse）
        self.Mdbs_Send_TimerCnt = 0         # 发送定时器计数器
        
        self.Mdbs_EnTimerCnt = EnFlagFalse  # 接收定时器使能标志（用于帧间隔检测）
        self.Mdbs_TimerCnt = 0              # 接收定时器计数器, 定时器计数值（0.1ms 单位）
        self.Mdbs_EnRcvCheck = EnFlagFalse  # 接收完成标志（EnFlagTrue/EnFlagFalse）
        self.RxTimes = 0                    # 已接收的字节数
        self.RxCurData = 0                  # 当前接收的字节
        self.RxData = [0] * 256             # 接收数据缓冲区（最大 256 字节）
        self.RxAddr = 0                     # 接收的设备地址(接收帧的地址字节)
        self.RxFuncID = 0                   # 接收的功能码(接收帧的功能码字节)   
        self.Mdbs_state = 0                 # ModBus 状态标志, 帧分析结果（包含错误标志如 CRC_err、ADDR_err 等）
        self.MdbsCNT = ModBusCounters()     # 错误计数器对象（记录各类错误次数）
        self.TxData = bytearray(256)        # 发送数据缓冲区（最大 256 字节）


# ModBusCounters类主要负责：统计 ModBus 通信过程中的各类错误和成功帧的数量
class ModBusCounters:
    def __init__(self):
        self.CRCerr_CNT = 0         # CRC 校验错误次数（帧数据校验失败）
        self.Addrerr_CNT = 0        # 地址错误次数（接收帧地址不匹配）
        self.IDerr_CNT = 0          # 功能码错误次数（接收帧功能码不合法）
        self.Frabrk_CNT = 0         # 帧损坏次数（接收帧长度不合法或格式错误）
        self.Frame_CNT = 0          # 成功帧计数（接收帧格式正确且通过 CRC 校验）

# Constants
EnFlagFalse = 0
EnFlagTrue = 1
ModBusFlag_Slave = 0
ModBusFlag_Master = 1
MaxLen = 256

# Error flags
ADDR_err = 0x01
Length_err = 0x02
FuncID_err = 0x04
Frame_broken = 0x08
CRC_err = 0x10
Frame_OK = 0x20


# CRC tables (these need to be defined as in the original C code)
auchCRCHi = [
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
    0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40
]

auchCRCLo = [
    0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4,
    0x04, 0xCC, 0x0C, 0x0D, 0xCD, 0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
    0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD,
    0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
    0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6, 0xF7,
    0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
    0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE,
    0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
    0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1, 0x63, 0xA3, 0xA2,
    0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
    0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB,
    0x7B, 0x7A, 0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
    0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91,
    0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
    0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58, 0x98, 0x88,
    0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
    0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80,
    0x40
]

def InitModBus(UartInfoTmp, Instance, MasterSlave, MyID):
    UartInfoTmp.Instance = Instance
    UartInfoTmp.MasterSlave = MasterSlave
    UartInfoTmp.MyModbusID = MyID
    
    UartInfoTmp.ModBusTxID = 1
    UartInfoTmp.EnSendModBus = EnFlagFalse
    UartInfoTmp.Mdbs_Send_TimerCnt = 0
    
    UartInfoTmp.Mdbs_EnTimerCnt = EnFlagFalse
    UartInfoTmp.Mdbs_TimerCnt = 0
    UartInfoTmp.Mdbs_EnRcvCheck = EnFlagFalse
    
    UartInfoTmp.RxTimes = 0

def ModBus_TIM_Callback(UartInfoTmp):
    if UartInfoTmp.Mdbs_EnTimerCnt == EnFlagTrue:       # 检查定时器是否启用
        UartInfoTmp.Mdbs_TimerCnt += 1                  # 计数器递增（0.1ms 单位）
        if UartInfoTmp.Mdbs_TimerCnt > 35:              # 超过 3.5ms（35 * 0.1ms）
            UartInfoTmp.Mdbs_TimerCnt = 0               # 清零计数器
            UartInfoTmp.Mdbs_EnRcvCheck = EnFlagTrue    # 标记帧接收完成
            UartInfoTmp.Mdbs_EnTimerCnt = EnFlagFalse   # 关闭定时器
            print("ModBus_TIM_Callback: 定时器超时，触发帧检查")  # 调试信息
            ModBusCheck(UartInfoTmp)                   # 调用帧检查函数

def ModBus_Rcv_Callback(UartInfoTmp, RcvData):  
    UartInfoTmp.RxCurData = RcvData & 0xFF              # 获取接收到的字节数据（8位）
    if UartInfoTmp.RxTimes == 0:                        # 如果是帧的第一个字节
        UartInfoTmp.RxData[0] = UartInfoTmp.RxCurData   # 存储缓冲区
        UartInfoTmp.RxAddr = UartInfoTmp.RxCurData      # 记录帧地址
        UartInfoTmp.RxTimes = 1                         # 递增已接收字节数
        
        # 启动定时器（用于检测帧间隔超时）
        UartInfoTmp.Mdbs_TimerCnt = 0
        UartInfoTmp.Mdbs_EnTimerCnt = EnFlagTrue
        print(f"ModBus_Rcv_Callback: 接收到第一个字节 0x{UartInfoTmp.RxCurData:02X}, 已接收 {UartInfoTmp.RxTimes} 字节")  # 调试信息
    else:                                                                # 如果不是第一个字节，即已进入帧接收状态
        UartInfoTmp.RxData[UartInfoTmp.RxTimes] = UartInfoTmp.RxCurData  # 存入缓冲区
        UartInfoTmp.RxTimes += 1                                         # 递增已接收字节数
        if UartInfoTmp.RxTimes == 2:                                     # 第二个字节是功能码
            UartInfoTmp.RxFuncID = UartInfoTmp.RxCurData                 # 记录备份下 功能码
        
        UartInfoTmp.Mdbs_TimerCnt = 0                                    # 每次收到数据都重置定时器（防止超时误判）
        UartInfoTmp.Mdbs_EnTimerCnt = EnFlagTrue

        # 每次接收后调用一次 ModBus_TIM_Callback，模拟定时器行为
        ModBus_TIM_Callback(UartInfoTmp)
        print(f"ModBus_Rcv_Callback: 接收到字节 0x{UartInfoTmp.RxCurData:02X}, 已接收 {UartInfoTmp.RxTimes} 字节")  # 调试信息
        
def ModBusCheck(UartInfoTmp):
    if UartInfoTmp.Mdbs_EnRcvCheck == EnFlagTrue:                        # 检测到帧接收完成
        UartInfoTmp.Mdbs_TimerCnt = 0                                    # 复位标志和定时器
        UartInfoTmp.Mdbs_EnRcvCheck = EnFlagFalse
        UartInfoTmp.Mdbs_EnTimerCnt = EnFlagFalse
        
        UartInfoTmp.Mdbs_state = AnalyFrm(UartInfoTmp)                   # 分析接收到的帧，获取状态标志
        
        # 更新错误计数器
        UartInfoTmp.MdbsCNT.CRCerr_CNT += 1 if (UartInfoTmp.Mdbs_state & CRC_err) else 0
        UartInfoTmp.MdbsCNT.Addrerr_CNT += 1 if (UartInfoTmp.Mdbs_state & ADDR_err) else 0
        UartInfoTmp.MdbsCNT.IDerr_CNT += 1 if (UartInfoTmp.Mdbs_state & FuncID_err) else 0
        UartInfoTmp.MdbsCNT.Frabrk_CNT += 1 if (UartInfoTmp.Mdbs_state & Frame_broken) else 0
        UartInfoTmp.MdbsCNT.Frame_CNT += 1 if (UartInfoTmp.Mdbs_state & Frame_OK) else 0
        
        # 处理有效帧(暂时改成在主程序中进行)
        # if UartInfoTmp.Mdbs_state & Frame_OK:
            # Deal_OKfrm(UartInfoTmp)                                      # 执行功能码对应的操作
        

def AnalyFrm(UartInfoTmp):
    Mdbs = 0                                                             # 初始化状态标志（无错误）
     
    # 1. 校验地址（如果是从机）
    if UartInfoTmp.MasterSlave == ModBusFlag_Slave:                    
        if UartInfoTmp.RxAddr != UartInfoTmp.MyModbusID:
            Mdbs = Mdbs | ADDR_err

    # 2. 校验帧长度
    if UartInfoTmp.RxTimes > 256:
        Mdbs = Mdbs | Length_err

    # 3. 校验功能码
    if UartInfoTmp.RxFuncID > 127:
        Mdbs = Mdbs | FuncID_err
    else:
        # 4. 校验特定功能码的帧长度（示例：功能码 0x03 的请求帧应为 8 字节!!）
        if UartInfoTmp.MasterSlave == ModBusFlag_Slave:
            if UartInfoTmp.RxFuncID in [0x03] and UartInfoTmp.RxTimes < 6:
                Mdbs = Mdbs | Frame_broken  # 帧长度不符合协议要求

    # 5. 校验 CRC（仅当其他校验通过时）
    if Mdbs == 0:
        if UartInfoTmp.RxTimes > 2:
            CRC_cacul = CRC16(UartInfoTmp.RxData, UartInfoTmp.RxTimes - 2)
            if ((UartInfoTmp.RxData[UartInfoTmp.RxTimes - 2] << 8) | UartInfoTmp.RxData[UartInfoTmp.RxTimes - 1]) == CRC_cacul:
                Mdbs = Frame_OK          # CRC 校验成功
            else:
                Mdbs = Mdbs | CRC_err    # CRC 校验失败
        else:
            Mdbs = Mdbs | CRC_err
    
    return Mdbs

def CRC16(puchMsg, usDataLen):
    uchCRCHi = 0xFF
    uchCRCLo = 0xFF
    
    if usDataLen > MaxLen:
        return 0xFFFF
    
    for i in range(usDataLen):
        uIndex = uchCRCHi ^ puchMsg[i]
        uchCRCHi = uchCRCLo ^ auchCRCHi[uIndex]
        uchCRCLo = auchCRCLo[uIndex]
    
    return (uchCRCHi << 8) | uchCRCLo

def Deal_OKfrm(UartInfoTmp):
    if UartInfoTmp.MasterSlave == ModBusFlag_Slave:
        if UartInfoTmp.RxFuncID == 0x01:
            Reply_01(UartInfoTmp)
        elif UartInfoTmp.RxFuncID == 0x02:
            Reply_02(UartInfoTmp)
        elif UartInfoTmp.RxFuncID == 0x03:
            Reply_03(UartInfoTmp)
        elif UartInfoTmp.RxFuncID == 0x04:
            Reply_04(UartInfoTmp)
        elif UartInfoTmp.RxFuncID == 0x05:
            Reply_05(UartInfoTmp)
        elif UartInfoTmp.RxFuncID == 0x06:
            Reply_06(UartInfoTmp)
        elif UartInfoTmp.RxFuncID == 0x0F:
            Reply_0F(UartInfoTmp)
        elif UartInfoTmp.RxFuncID == 0x10:
            Reply_10(UartInfoTmp)

# 对不同功能码的帧进行回复操作（接口）
def Reply_01(UartInfoTmp): print("Reply_01 called with data:", UartInfoTmp.RxData[:UartInfoTmp.RxTimes])
def Reply_02(UartInfoTmp): print("Reply_02 called with data:", UartInfoTmp.RxData[:UartInfoTmp.RxTimes])
def Reply_03(UartInfoTmp): print("Reply_03 called with data:", UartInfoTmp.RxData[:UartInfoTmp.RxTimes])
def Reply_04(UartInfoTmp): print("Reply_04 called with data:", UartInfoTmp.RxData[:UartInfoTmp.RxTimes])
def Reply_05(UartInfoTmp): print("Reply_05 called with data:", UartInfoTmp.RxData[:UartInfoTmp.RxTimes])
def Reply_06(UartInfoTmp): print("Reply_06 called with data:", UartInfoTmp.RxData[:UartInfoTmp.RxTimes])  
def Reply_0F(UartInfoTmp): print("Reply_0F called with data:", UartInfoTmp.RxData[:UartInfoTmp.RxTimes])
def Reply_10(UartInfoTmp): print("Reply_10 called with data:", UartInfoTmp.RxData[:UartInfoTmp.RxTimes])

def Modbus_receive_Interface(rcv_hex_str):
    # 1. 初始化 ModBus 参数
    uart_info = tUartParms()
    InitModBus(uart_info, Instance=0, MasterSlave=ModBusFlag_Slave, MyID=1)  # 从站模式，地址为1
    # 保持十六进制表示
    process_hex = lambda s: [int(s[i:i+2], 16) for i in range(0, len(s), 2)]

    test_frame = process_hex(rcv_hex_str)

    # print([hex(x) for x in test_frame])
    # 输出: ['0x1', '0x3', '0x4', '0x0', '0x0', '0x0', '0x0', '0xfa', '0x33']

    for byte in test_frame:
        ModBus_Rcv_Callback(uart_info, byte)

    uart_info.Mdbs_EnRcvCheck = EnFlagTrue
    ModBusCheck(uart_info)

    # 解析帧
    if uart_info.Mdbs_state & Frame_OK:
        print("正在解析是否为有效帧...")
        RxAddr = uart_info.RxData[0]
        RxFuncID = uart_info.RxData[1]
        RxDataLen = uart_info.RxData[2]  # 字节数
        raw_bytes = uart_info.RxData[3:3 + RxDataLen]

        if RxFuncID in (0x03, 0x04):  # 读寄存器
            RxData = [f"0x{(raw_bytes[i] << 8) | raw_bytes[i+1]:04x}" 
                    for i in range(0, len(raw_bytes), 2)]
        elif RxFuncID in (0x01, 0x02):  # 读线圈/离散输入
            bits = []
            for b in raw_bytes:
                for bit in range(8):
                    bits.append((b >> bit) & 0x01)
            RxData = bits
        else:
            RxData = list(raw_bytes)
        print("有效帧，继续进程...")

    else:
        print("无效帧，无法解析！！")
        RxAddr = None
        RxFuncID = None
        RxDataLen = None
        RxData = None

    # 复位接收状态（无论帧是否有效）
    uart_info.RxTimes = 0
    uart_info.RxAddr = 0
    uart_info.RxFuncID = 0
    print("已经完成帧检查！！")

    # 3. 返回解析结果
    return RxAddr, RxFuncID, RxDataLen, RxData, uart_info.Mdbs_state, uart_info.MdbsCNT



# ---------------------------- 主函数调试（仅供调试用） ----------------------------
if __name__ == "__main__":
    # 1. 初始化 ModBus 参数
    uart_info = tUartParms()
    InitModBus(uart_info, Instance=0, MasterSlave=ModBusFlag_Slave, MyID=1)  # 从站模式，地址为1

    # 2. 模拟接收一个有效的 Modbus RTU 帧（示例：读取保持寄存器请求）
    rcv_frame = "01 03 04 00 00 00 00 FA 33"  # 用于打印对比
    
    test_frame = [
        0x01,       # 从站地址
        0x03,       # 功能码 (读取线圈寄存器)
        0x04,       # 读1位
        0x00, 0x00, 0x00, 0x00,      # 数据
        0xFA, 0x33  # CRC16 校验码 (预先计算好的)
    ]

    print("----------开始接收Modbus帧----------")
    for byte in test_frame:
        ModBus_Rcv_Callback(uart_info, byte)
    print(f"接收的完整帧: {rcv_frame}")
    print("----------Modbus帧接收完成----------")

    # 3. 手动触发帧检查（模拟定时器超时）
    print("\n\n----------开始触发帧检查----------")
    uart_info.Mdbs_EnRcvCheck = EnFlagTrue
    ModBusCheck(uart_info)
    # 解析帧
    if uart_info.Mdbs_state & Frame_OK:
        print("正在解析有效帧...")
        RxAddr = uart_info.RxData[0]
        RxFuncID = uart_info.RxData[1]
        RxDataLen = uart_info.RxData[2]  # 数据长度
        RxData = uart_info.RxData[3:3 + RxDataLen]  # 数据部分(是否×2取决于是线圈寄存器or保持寄存器)
        print(f"接收地址: {RxAddr}, 功能码: {RxFuncID}, 数据长度: {RxDataLen}, 数据: {RxData}")
    else:
        print("无效帧，无法解析。")
        RxAddr = None
        RxFuncID = None
        RxDataLen = None
        RxData = None

    # 复位接收状态（无论帧是否有效）
    uart_info.RxTimes = 0
    uart_info.RxAddr = 0
    uart_info.RxFuncID = 0
    print("----------已经完成帧检查----------")

    # 4. 打印解析结果
    print("\n\n----------帧解析结果----------")
    if uart_info.Mdbs_state & Frame_OK:
        print("状态: 帧有效 (Frame_OK)")
    else:
        print("状态: 帧无效")
        if uart_info.Mdbs_state & ADDR_err:
            print("错误: 地址不匹配 (ADDR_err)")
        if uart_info.Mdbs_state & CRC_err:
            print("错误: CRC校验失败 (CRC_err)")
        if uart_info.Mdbs_state & Frame_broken:
            print("错误: 帧损坏 (Frame_broken)")
    print("----------帧解析结果----------")

    # 5. 打印错误计数器
    print("\n\n----------错误计数器统计----------")
    print(f"CRC错误次数: {uart_info.MdbsCNT.CRCerr_CNT}")
    print(f"地址错误次数: {uart_info.MdbsCNT.Addrerr_CNT}")
    print(f"功能码错误次数: {uart_info.MdbsCNT.IDerr_CNT}")
    print(f"帧损坏次数: {uart_info.MdbsCNT.Frabrk_CNT}")
    print(f"成功帧次数: {uart_info.MdbsCNT.Frame_CNT}")
    print("----------错误计数器统计----------")
