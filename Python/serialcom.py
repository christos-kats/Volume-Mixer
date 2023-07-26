import serial
import serial.tools.list_ports

def getAvailablePorts():
    ports = serial.tools.list_ports.comports()
    #portNames = []
    #for port in ports:
    #    portNames.append(port.name)
    #    print(port.description)
    #    print(port.serial_number)
    #return portNames
    return ports

class serialCommunication():
    def __init__(self, port, baudRate, timeout):
        self.serialDevice = None
        self.port = port
        self.baudRate = baudRate
        self.timeout = timeout
    
    def connect(self):
        self.serialDevice = serial.Serial(port= self.port, baudrate=self.baudRate, timeout=self.timeout)

    def serialWrite(self,writeString):
        self.serialDevice.write(bytes(writeString, 'utf-8'))
    
    def serialRead(self):
        readString = self.serialDevice.readline().decode(encoding='utf-8')
        return readString

    def isConnected(self):
        return self.serialDevice.isOpen()
    
    def disconnect(self):
        self.serialDevice.close()
