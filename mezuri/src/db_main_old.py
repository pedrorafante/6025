from mqtt.mqtt_conn import MQTTClient
from database.connectdb import DataDAO
import json
from datetime import datetime, timezone
import threading
import database.constants_db as CONST
from log.logger import Logger

class DataReceiver:
    def __init__(self):
        self.logger = Logger(CONST.LOG_FILE, CONST.LOG_PATH)

        self.sync_flag = threading.Event()
        
        self.logger.write_log("Starting database connection...")
        self.comp_db_client = DataDAO(computer_name='embed_computers')
        self.logger.write_log("Done!")
        
        self.data = dict()
        self.sync_timestamp = None
        self.gps_data = dict()

        self.logger.write_log("Starting mqtt connections...")
        self.mqtt_client = self._start_conn(CONST.CLIENT_ID)
        self.logger.write_log("Done!")

    def _start_conn(self, client_id):
        mqtt_client = MQTTClient(client_id=client_id)
        mqtt_client.connect()

        for topic in CONST.COMP_TOPIC_LIST:
            mqtt_client.subscribe(topic, self.comp_callback)

        mqtt_client.subscribe(CONST.SYNC_TOPIC, self.sync_callback)
        mqtt_client.subscribe(CONST.GPS_TOPIC, self.gps_callback)
        mqtt_client.subscribe(CONST.GET_DATA, self.get_data)

        return mqtt_client

    def gps_callback(self, topic, message):
         self.gps_data = json.loads(message)

    def sync_callback(self, topic, message):
         self.sync_flag.set()
         msg = json.loads(message)
         self.sync_timestamp = msg["timestamp"]
     #     print("time in call_back: {}".format(self.sync_timestamp))


    def comp_callback(self, topic, message):
        self.data[topic] = message

    def get_data(self, topic, message):
            msg = json.loads(message)
            id_number = msg["last_id"]
            number_rows = msg["package_size"]
            response = self.comp_db_client.retrieve_data(id_number,number_rows)
            self.mqtt_client.publish(msg["answer_topic"], json.dumps(response))
            self.comp_db_client.delete_data(msg["last_id"])

    def run_process_data(self):
         while True:
              if self.sync_flag.wait(timeout=0.15):
                   self.sync_flag.clear()
               #     timestamp = self.sync_timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
                   timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
               #     timestamp = self.sync_timestamp
                   if self.data:
                        print("time in run_process_data: {}".format(timestamp))
                    #     timestamp = timestamp[:19]
                        self.logger.write_log("saving data from {}".format(list(self.data.keys())))
                        self.comp_db_client.insert_data(data=self.data,timestamp=timestamp,gps_data=self.gps_data)
                   self.data = dict()
                   self.gps = dict()
                   self.sync_timestamp = None
               #     print("\n")


def main():
     data_receiver = DataReceiver()
     data_receiver.run_process_data()

# Example usage
if __name__ == "__main__":
    main()