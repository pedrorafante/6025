"""
Constantes relativas ao módulo de GPS.
"""

##Host de leitura dos dados de GPS.
UDP_IP = "192.168.137.100"
##Porta de leitura de dados de GPS.
UDP_PORT = 8500
##Estruturação de ip e porta do websocket.
GPS_BIND = (UDP_IP, UDP_PORT)

CLIENT_ID = "GPS"
GPS_TOPIC = "gps"

LOG_FILE = "GPS_MAIN.LOG"
LOG_PATH = '/var/log/'