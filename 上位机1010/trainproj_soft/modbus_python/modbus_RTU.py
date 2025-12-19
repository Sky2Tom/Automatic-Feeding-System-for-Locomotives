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
 
    def CRC16(self,hex_num):
        """
        CRC16校验
        """
        crc = '0xffff'
        crc16 = '0xA001'
        # test = '01 06 00 00 00 00'
        test = hex_num.split(' ')
        print(test)
 
        crc = self.Binary.Hex2Dex(crc)  # 十进制
        crc16 = self.Binary.Hex2Dex(crc16)  # 十进制
        for i in test:
            temp = '0x' + i
            # 亦或前十进制准备
            temp = self.Binary.Hex2Dex(temp)  # 十进制
            # 亦或
            crc ^= temp  # 十进制
            for i in range(8):
                if self.Binary.Dex2Bin(crc)[-1] == '0':
                    crc >>= 1
                elif self.Binary.Dex2Bin(crc)[-1] == '1':
                    crc >>= 1
                    crc ^= crc16
                # print('crc_D:{}\ncrc_B:{}'.format(crc, self.Binary.Dex2Bin(crc)))
 
        crc = hex(crc)
        crc_H = crc[2:4] # 高位
        crc_L = crc[-2:] # 低位
 
        return crc, crc_H, crc_L

def test():
    CRC_obj = CRC()
    test = '01 03 00 40 00 01'
    test1 = '\x01 \x03 \x00 \x40 \x00 \x01'
    crc, crc_H, crc_L = CRC_obj.CRC16(test)
    print("crc:{0}\ncrc_H:{1}\ncrc_L:{2}".format(crc,crc_H,crc_L))

if __name__ == "__main__":
    test()

