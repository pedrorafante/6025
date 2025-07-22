import time
from datetime import datetime, timezone
import serial
import signal
import sys
import json
from mqtt.mqtt_conn import MQTTClient

from constants.constants_embed import *
from log.logger import Logger

class AUX:

    def __init__(self):
        self.computer = dict(AUX_PARAMS)
        self.data_collection = list()
        self.last_interpolation = dict()
        self.logger = Logger(AUX_LOG_NAME,LOG_PATH)
        self.mqtt_client = MQTTClient(client_id=AUX_ID)

        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)

    def handle_exit(self, sig, frame):
        raise(SystemExit)

    def parse(self, data_raw):
        """
        Método que converte dados brutos oriundos do AUX para uma lista de floats equivalentes. Cada
        elemento da lista corresponde à uma medida dos dados brutos.

        Method that convert a raw data from AUX computer to an equivalent of string list. Each float
        list element correspond to a measure from the raw data.

        Data raw has a set of measures.

        Args:
            data_raw:: string list
        Returns:
            float list
        """
        parameters = list()
        for data in data_raw:
            #TODO: LENGTH CAN BE 58 OR 56 depending on the locmotive.
            if (len(data) == 56):
                tf1 = float((int(data[3:5],16))) # temperature 1. Needs to remember it´s name. Given in Farenheit
                tf2 = float((int(data[5:7],16))) # temperature 2. Needs to remember it´s name. Given in Farenheit
                t3 = float((int(data[7:9],16))) # temperature 3. Needs to remember it´s name. Given in Celsius

                t1 = (tf1-32.0)*5.0/9.0
                t2 = (tf2-32.0)*5.0/9.0
                parameters = [t1, t2, t3]
        return parameters

    def sync_callback(self, topic, message):
         if self.data_collection:
            self.logger.write_log("processing data to sent database...")
            sync_msg = json.loads(message)
            data_msg = dict()
            data_msg["data"] = self.data_collection[-1][0]
            data_msg["timestamp"] = sync_msg["timestamp"]

            self.mqtt_client.publish(AUX_TOPIC, json.dumps(data_msg))
            self.logger.write_log("Data sent!")
            self.data_collection = list()

    def connect_mqtt(self):
        self.mqtt_client.connect()
        self.mqtt_client.subscribe("sync", self.sync_callback)

    def connect_serial(self):
        if not self.computer["serial_obj"]:
            self.logger.write_log("initializing CAB module...")

            self.computer["serial_obj"] = serial.Serial(
                port=self.computer["serial_port"],
                baudrate=self.computer["baudrate"],
                timeout=self.computer["timeout"],
                parity=self.computer["parity"],
                bytesize=self.computer["bytesize"],
                xonxoff=self.computer["xonxoff"]
            )

            self.logger.write_log("all done!")

    def process_data(self):
        self.logger.write_log("reading data from AUX")
        while True:
            try:
                data_raw = list()
                
                for _ in range(self.computer["number_messages"]):
                    serial_read = self.computer["serial_obj"].read_until(terminator='\r'.encode())
                    data_raw.append(serial_read)

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
                self.logger.write_log('Failed to read data from AUX. Collector will be restarted...')
                self.computer["serial_obj"].close()
                self.computer["serial_obj"] = None
                time.sleep(1)
                self.connect()

    def run_telemetry(self):
        self.connect_mqtt()
        self.connect_serial()
        self.process_data()

def main():
    mts_aux = AUX()
    try:
        mts_aux.run_telemetry()
    except(KeyboardInterrupt, SystemExit):
        mts_aux.logger.write_log_warn("AUX will be finished.")
        mts_aux.computer["serial_obj"].close()
        sys.exit()

if __name__ == "__main__":
    main()
