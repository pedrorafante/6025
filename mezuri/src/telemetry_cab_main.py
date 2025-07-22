import time
from datetime import datetime, timezone
import serial
import signal
import sys
import json
from mqtt.mqtt_conn import MQTTClient

from constants.constants_embed import *
from log.logger import Logger

class CAB:

    def __init__(self):
        self.computer = dict(CAB_PARAMS)
        self.data_collection = list()
        self.last_interpolation = dict()
        self.logger = Logger(CAB_LOG_NAME,LOG_PATH)
        self.mqtt_client = MQTTClient(client_id=CAB_ID)

        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)

    def handle_exit(self, sig, frame):
        raise(SystemExit)

    def parse(self, data_raw):
        """
        Método que converte dados brutos oriundos do CAB para uma lista equivalente de strings. Cada
        string da lista corresponde à uma posição corrente da reversora/seletora.

        Method that convert a raw data from CAB computer to an equivalent of string list. Each string
        list element correspond to a reversor/selector current position.

        Data raw has a set of measures.

        Args:
            data_raw:: string list
        Returns:
            string list
        """
        parameters = list()
        params1 = list()
        params2 = list()
        params3 = list()
        selector_position_name = ""
        reversor_point_name = ""
        pcs = ''

        rev_points_N = [257,265,281,329,345,489,505,361,377]
        rev_points_N_pcs = [256,264,280,328,344,488,504,360,376]
        rev_points_R = [261,269,285,333,349,493,509,365,381]
        rev_points_R_pcs = [260,268,284,332,348,492,508,364,380]
        rev_points_F = [259,267,283,331,347,491,507,363,379]
        rev_points_F_pcs = [258,266,282,330,346,490,506,362,378]
        for data in data_raw:
            if (len(data) == 68):
                params1 = []

            if (len(data) == 58):
                 rev_point = int(data[8:11],16)
                 if rev_point in rev_points_N:
                     reversor_point_name = "N{0}".format(rev_points_N.index(rev_point))
                     penalty = '0'
                 if rev_point in rev_points_R:
                     reversor_point_name = "R{0}".format(rev_points_R.index(rev_point))
                     penalty = '0'
                 if rev_point in rev_points_F:
                     reversor_point_name = "F{0}".format(rev_points_F.index(rev_point))
                     penalty = '0'
                
                 if rev_point in rev_points_N_pcs:
                     reversor_point_name = "N{0}".format(rev_points_N_pcs.index(rev_point))
                     penalty = '1'
                 if rev_point in rev_points_R_pcs:
                     reversor_point_name = "R{0}".format(rev_points_R_pcs.index(rev_point))
                     penalty = '1'
                 if rev_point in rev_points_F_pcs:
                     reversor_point_name = "F{0}".format(rev_points_F_pcs.index(rev_point))
                     penalty = '1'

                 selector_position = int(data[15:18],16)
                 #TODO: In some locomotives, the code number is different.
                 #if selector_position == 770: # arranque
                 if (selector_position == 834) or (selector_position == 835) or (selector_position == 770): # arranque
                     selector_position_name="ARRANQUE"
                 #if selector_position == 772: # marcha
                 if (selector_position == 836) or (selector_position == 837) or (selector_position == 772): # marcha
                     selector_position_name="MARCHA"
                 #if selector_position == 776: # isolado
                 if (selector_position == 840) or (selector_position == 841) or (selector_position == 776): # isolado
                     selector_position_name="ISOLADO"
                 
                 battery_level = int(data[5:7],16)
                 dynamic_brake = int(data[7])
                 params2 = [reversor_point_name, selector_position_name, penalty, battery_level, dynamic_brake]
            
            if (len(data) == 36):
                params3 = []
        parameters = params1 + params2 + params3
        return parameters

    def sync_callback(self, topic, message):
         if self.data_collection:
            self.logger.write_log("processing data to sent database...")
            sync_msg = json.loads(message)
            data_msg = dict()
            data_msg["data"] = self.data_collection[-1][0]
            data_msg["timestamp"] = sync_msg["timestamp"]

            self.mqtt_client.publish(CAB_TOPIC, json.dumps(data_msg))
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
        self.logger.write_log("reading data from CAB")
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
                self.logger.write_log('Failed to read data from CAB. Collector will be restarted...')
                self.computer["serial_obj"].close()
                self.computer["serial_obj"] = None
                time.sleep(1)
                self.connect()

    def run_telemetry(self):
        self.connect_mqtt()
        self.connect_serial()
        self.process_data()

def main():
    mts_cab = CAB()
    try:
        mts_cab.run_telemetry()
    except(KeyboardInterrupt, SystemExit):
        mts_cab.logger.write_log_warn("CAB will be finished.")
        mts_cab.computer["serial_obj"].close()
        sys.exit()

if __name__ == "__main__":
    main()
