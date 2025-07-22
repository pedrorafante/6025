import time
from datetime import datetime, timezone
import serial
import signal
import sys
import json
from mqtt.mqtt_conn import MQTTClient

from constants.constants_embed import *
from log.logger import Logger

class EXC:

    def __init__(self):
        self.computer = dict(EXC_PARAMS)
        self.data_collection = list()
        self.last_interpolation = dict()
        self.logger = Logger(EXC_LOG_NAME,LOG_PATH)
        self.mqtt_client = MQTTClient(client_id=EXC_ID)

        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)

    def handle_exit(self, sig, frame):
        raise(SystemExit)

    def parse(self, data_raw):
        parameters = list()
        params1 = list()
        params2 = list()
        for data in data_raw:
            if (len(data) == 64):
                ta = float((int(data[4:7],16))) # alternator tension
                ca = float((int(data[8:11],16))) # alternator current
                l = float((int(data[20:23],16))) # load
                mt1 = float((int(data[24:27],16))) # MT1
                mt2 = float((int(data[28:31],16))) # MT2
                mt3 = float((int(data[32:35],16))) # MT3
                mt4 = float((int(data[36:39],16))) # MT4
                mt5 = float((int(data[40:43],16))) # MT5
                mt6 = float((int(data[44:47],16))) # MT6
                fc = float((int(data[48:51],16))) # field current
                lo = float((int(data[56:59],16))) # Load
                params1 = [ta,ca,l,mt1,mt2,mt3,mt4,mt5,mt6,fc,lo]
            if(len(data) == 16):
                mt7 = float((int(data[6:9],16))) # MT7
                mt8 = float((int(data[10:13],16))) # MT8
                params2 = [mt7, mt8]

        parameters = params1 + params2
        return parameters

    def sync_callback(self, topic, message):
         if True:
        #  if self.data_collection:
            self.logger.write_log("processing data to sent database...")
            sync_msg = json.loads(message)
            data_msg = dict()
            data_msg["data"] = self.data_collection[-1][0]
            data_msg["timestamp"] = sync_msg["timestamp"]

            self.mqtt_client.publish(EXC_TOPIC, json.dumps(data_msg))
            self.logger.write_log("Data sent!")
            self.data_collection = list()

    def connect_mqtt(self):
        self.mqtt_client.connect()
        self.mqtt_client.subscribe("sync", self.sync_callback)

    def connect_serial(self):
        if not self.computer["serial_obj"]:
            self.logger.write_log("initializing EXC module...")

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
        self.logger.write_log("reading data from EXC")
        while True:
            try:
                data_raw = list()
                
                for _ in range(self.computer["number_messages"]):
                    serial_read = self.computer["serial_obj"].read_until(terminator='\r'.encode())
                    data_raw.append(serial_read)

                # print(data_raw)
                timestamp = datetime.now(tz=timezone.utc).isoformat()
                data = self.parse(data_raw)
                
                if len(self.data_collection) >= DATA_COLECTION_SIZE:
                    self.data_collection.pop(0)
                
                if len(data) > 0:
                    self.data_collection.append((data,timestamp))

                # print(self.data_collection)

            except Exception as e:
                self.logger.write_log_error(e)
                self.logger.write_log('Failed to read data from EXC. Collector will be restarted...')
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
    mts_exc = EXC()
    try:
        mts_exc.run_telemetry()
    except(KeyboardInterrupt, SystemExit):
        mts_exc.logger.write_log_warn("EXC will be finished.")
        mts_exc.computer["serial_obj"].close()
        sys.exit()

if __name__ == "__main__":
    main()
