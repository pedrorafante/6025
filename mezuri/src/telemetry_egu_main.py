import time
from datetime import datetime, timezone
import serial
import signal
import sys
import json
from mqtt.mqtt_conn import MQTTClient

from constants.constants_embed import *
from log.logger import Logger

class EGU:

    def __init__(self):
        self.computer = dict(EGU_PARAMS)
        self.data_collection = list()
        self.last_interpolation = dict()
        self.logger = Logger(EGU_LOG_NAME,LOG_PATH)
        self.mqtt_client = MQTTClient(client_id=EGU_ID)

        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)

    def handle_exit(self, sig, frame):
        raise(SystemExit)

    def parse(self, data_raw):
        parameters = list()
        if (len(data_raw)==73):
            es = float((int(data_raw[0:4],16)))/16 #Engine_Speed
            mp = float((int(data_raw[9:13],16)))/128 #Manifold_air_pressure
            mk = float((int(data_raw[18:22],16)))/64 #Manifold_air_temperature
            cp = float((int(data_raw[27:31],16)))/128 #Coolant_pressure
            ck = float((int(data_raw[36:40],16)))/64 #Coolant_temperature
            op = float((int(data_raw[45:49],16)))/128 #Lube_Oil_Pressure
            fv = float((int(data_raw[54:58],16)))/8 #Fuel_Value
            lp = float((int(data_raw[63:67],16)))/(32*1023) #Load Potentiometer
            parameters=[es,mp,mk,cp,ck,op,fv,lp]
            print(parameters)
        return parameters
    
    def request_data(self):
        serial_egu = self.computer["serial_obj"]

        time.sleep(1)
        serial_egu.write(25)
        time.sleep(1) #Tempo necessário para não gerar conflito de comunicação com o EGU
        serial_egu.write('M'.encode())
        time.sleep(0.01)
        serial_egu.write('M'.encode())
        time.sleep(0.01)
        serial_egu.write(' '.encode())
        time.sleep(0.01)
        for c in ADDR_EGU:
            serial_egu.write(c.encode())
            time.sleep(0.02)
        serial_egu.write('\r'.encode())
        time.sleep(0.2)

    def sync_callback(self, topic, message):
         if self.data_collection:
            self.logger.write_log("processing data to sent database...")
            sync_msg = json.loads(message)
            data_msg = dict()
            data_msg["data"] = self.data_collection[-1][0]
            data_msg["timestamp"] = sync_msg["timestamp"]

            self.mqtt_client.publish(EGU_TOPIC, json.dumps(data_msg))
            self.logger.write_log("Data sent!")
            self.data_collection = list()

    def connect_mqtt(self):
        self.mqtt_client.connect()
        self.mqtt_client.subscribe("sync", self.sync_callback)

    def connect_serial(self):
        if not self.computer["serial_obj"]:
            self.logger.write_log("initializing EGU module...")

            self.computer["serial_obj"] = serial.Serial(
                port=self.computer["serial_port"],
                baudrate=self.computer["baudrate"],
                timeout=self.computer["timeout"],
                parity=self.computer["parity"],
                bytesize=self.computer["bytesize"],
                xonxoff=self.computer["xonxoff"]
            )
            self.request_data()

            self.logger.write_log("all done!")

    def process_data(self):
        self.logger.write_log("reading data from EGU")
        while True:
            try:
                data_raw = self.computer["serial_obj"].read_until(terminator='\r'.encode())
                # print(data_raw)
                timestamp = datetime.now(tz=timezone.utc).timestamp()
                data = self.parse(data_raw)
                
                if len(self.data_collection) >= DATA_COLECTION_SIZE:
                    self.data_collection.pop(0)
                
                if len(data) > 0:
                    self.data_collection.append((data,timestamp))

                # print(self.data_collection)

            except Exception as e:
                self.logger.write_log_error(e)
                self.logger.write_log('Failed to read data from EGU. Collector will be restarted...')
                self.computer["serial_obj"].close()
                self.computer["serial_obj"] = None
                time.sleep(1)
                self.connect()


    def run_telemetry(self):
        self.connect_serial()
        time.sleep(5)
        self.connect_mqtt()
        self.process_data()

def main():
    """
    A função main é utilizada para iniciar o software e realizar o tratamento de finalização do software.

    The main function, used to start the software and the exit treatment of the software.

    Args:
        None
    Returns:
        None
    Raises:
        TypeError: KeyboardInterrupt, SystemExit
        ValueError: finalize the telemetry execution and exit the software.
    """
    mts_egu = EGU()
    try:
        mts_egu.run_telemetry()
    except(KeyboardInterrupt, SystemExit):
        mts_egu.logger.write_log_warn("EGU will be finished.")
        mts_egu.computer["serial_obj"].close()
        sys.exit()

if __name__ == "__main__":
    main()
