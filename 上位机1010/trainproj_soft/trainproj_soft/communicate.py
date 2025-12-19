import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
import serial
import struct


class ModbusRTUGUI(QWidget):

    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()

        # Serial Port Configuration Section
        hlayout_port = QHBoxLayout()
        self.port_label = QLabel('Port:')
        self.port_input = QLineEdit('/dev/ttyUSB0')  # Default port on Linux systems
        hlayout_port.addWidget(self.port_label)
        hlayout_port.addWidget(self.port_input)

        hlayout_baudrate = QHBoxLayout()
        self.baudrate_label = QLabel('Baud Rate:')
        self.baudrate_input = QLineEdit('9600')
        hlayout_baudrate.addWidget(self.baudrate_label)
        hlayout_baudrate.addWidget(self.baudrate_input)

        connect_button = QPushButton('Connect')
        connect_button.clicked.connect(self.on_connect_clicked)

        layout.addLayout(hlayout_port)
        layout.addLayout(hlayout_baudrate)
        layout.addWidget(connect_button)

        # Add more UI elements here as needed...

        self.setLayout(layout)
        self.setWindowTitle('Modbus RTU Client with PyQt5 &amp; PySerial')

    def on_connect_clicked(self):
        try:
            ser = serial.Serial(
                port=self.port_input.text(),
                baudrate=int(self.baudrate_input.text()),
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            
            if not ser.isOpen():
                raise Exception("Failed to open the specified COM port")

            print(f"Connected successfully to {ser.name}")

            # Example of sending a simple MODBUS request (Function Code 3 - Read Holding Registers)
            slave_id = 1
            function_code = 3
            start_address = 0x00
            quantity_of_registers = 1
            
            crc = calculate_crc([slave_id, function_code, start_address >> 8, start_address & 0xFF, quantity_of_registers >> 8, quantity_of_registers & 0xFF])
            modbus_request = bytearray([
                slave_id,
                function_code,
                start_address >> 8,
                start_address & 0xFF,
                quantity_of_registers >> 8,
                quantity_of_registers & 0xFF,
                *crc])

            ser.write(modbus_request)
            response = ser.read(size=len(modbus_request))

            process_response(response)

            ser.close()

        except Exception as e:
            print(e)


def calculate_crc(data):
    """Calculate CRC-16 checksum according to Modbus standard."""
    crc = 0xFFFF
    
    for pos in data:
        crc ^= pos
        
        for _ in range(8):
            if ((crc & 0x0001) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
                
    return [(crc & 0xff), (crc >> 8)]  # Return CRC as a list of two bytes


def process_response(resp_bytes):
    """Process received byte array from device"""
    pass  # Implement processing logic based on your needs.


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = ModbusRTUGUI()
    window.show()

    sys.exit(app.exec_())
