# Modbus_RTU协议帧格式：/01（设备地址）03（读保持寄存器）00 40（起始地址） 00 01（预读取数量） XX XX (校验码)
# 进制转化实现
class Binary:
    """
        自定义进制转化
    """
    @staticmethod
    def Hex2Dex(e_hex):
        """
        十六进制转换十进制
        :param e_hex:
        :return:
        """
        return int(e_hex, 16)
 
    @staticmethod
    def Hex2Bin(e_hex):
        """
        十六进制转换二进制
        :param e_hex:
        :return:
        """
        return bin(int(e_hex, 16))
 
    @staticmethod
    def Dex2Bin(e_dex):
        """
        十进制转换二进制
        :param e_dex:
        :return:
        """
        return bin(e_dex)
 
# 校验方法实现
class CRC:
    """
     CRC验证
    """
    def __init__(self):
        self.Binary = Binary()
 
    def CRC16(self, hex_num):
        """
        修正版CRC16校验计算
        """
        # 初始化CRC为0xFFFF
        crc = 0xFFFF
        
        # 将十六进制字符串转换为字节列表
        bytes_list = [int(x, 16) for x in hex_num.split()]
        
        # 计算CRC
        for byte in bytes_list:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001  # Modbus多项式(0xA001是0x8005的反转)
                else:
                    crc >>= 1
        
        # 将CRC转换为十六进制字符串
        crc_hex = f"{crc:04x}"
        
        # 返回结果
        return crc_hex, crc_hex[0:2], crc_hex[2:4]  # (完整CRC, 高字节, 低字节)
 

def test():
    CRC_obj = CRC()
    test = '01 03 00 01 00 02'
    crc, crc_H, crc_L = CRC_obj.CRC16(test)
    print("crc:{0}\ncrc_H:{1}\ncrc_L:{2}".format(crc,crc_H,crc_L))

if __name__ == "__main__":
    test()
