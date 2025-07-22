"""
Constantes relacionadas à telemetria dos computadores embarcados.
"""

##Caminho do arquivo de log.
LOG_PATH = "/var/log/"

##Nome do arquivo de log.
EGU_LOG_NAME = "EGU_TELEMETRY.LOG"
CAB_LOG_NAME = "CAB_TELEMETRY.LOG"
EXC_LOG_NAME = "EXC_TELEMETRY.LOG"
AUX_LOG_NAME = "AUX_TELEMETRY.LOG"

EGU_ID = "EGU"
CAB_ID = "CAB"
EXC_ID = "EXC"
AUX_ID = "AUX"

EGU_TOPIC = "egu"
CAB_TOPIC = "cab"
EXC_TOPIC = "exc"
AUX_TOPIC = "aux"

DATA_COLECTION_SIZE = 10

##Mensagem para requisitar dados da EGU.
ADDR_EGU = '00094304 000940D0 000940CE 000940C8 000940CA 000940CC 0009431C 0009431E'

##Dados de controle de portas seriais para cada computador.
EGU_PARAMS = {
    "name": 'egu',
    "serial_obj": None,
    "serial_port": "/dev/ttySPRU2",
    "timeout": 5,
    "bytesize":7,
    "parity": 'E',
    "stopbits": 1,
    "xonxoff": 0,
    "baudrate": 9600,
    "collect": True,
    "number_messages": 1,
    "number_variables": 8
}

EXC_PARAMS = {
    "name": 'exc',
    "serial_obj": None,
    "serial_port": "/dev/ttySPRU1",
    "timeout": 5,
    "bytesize":7,
    "parity": 'E',
    "stopbits": 1,
    "xonxoff": 0,
    "baudrate": 9600,
    "collect": True,
    "number_messages": 2,
    "number_variables": 13
}

CAB_PARAMS = {
    "name": 'cab',
    "serial_obj": None,
    "serial_port": "/dev/ttySPRU0",
    "timeout": 5,
    "bytesize":7,
    "parity": 'E',
    "stopbits": 1,
    "xonxoff": 0,
    "baudrate": 9600,
    "collect": True,
    "number_messages": 3,
    "number_variables": 5
}

AUX_PARAMS = {
    "name": 'aux',
    "serial_obj": None,
    "serial_port": "/dev/ttySPRU4",
    "timeout": 5,
    "bytesize":7,
    "parity": 'E',
    "stopbits": 1,
    "xonxoff": 0,
    "baudrate": 9600,
    "collect": True,
    "number_messages": 1,
    "number_variables": 3
}
