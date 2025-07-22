from gps.connectgps import GPS
import gps.constants_gps as CONST
from mqtt.mqtt_conn import MQTTClient
import time
from datetime import datetime
import json
from log.logger import Logger

def get_valid_gps(gps):
    gps_data = gps.get_gps()
    while gps_data["gps_status"] == "V":
        time.sleep(1.5)
        gps_data = gps.get_gps()

    if(type(gps_data["gps_timestamp"]) == type(float())):
        gps_data['gps_timestamp'] = datetime.fromtimestamp(gps_data['gps_timestamp']).isoformat()

    return gps_data

def main():
    logger = Logger(CONST.LOG_FILE, CONST.LOG_PATH)

    logger.write_log("Starting gps...")
    gps = GPS()
    gps.run()
    logger.write_log("Done!")

    logger.write_log("Starting mqtt connection...")
    mqtt_client = MQTTClient(client_id=CONST.CLIENT_ID)
    mqtt_client.connect()
    logger.write_log("Done!")

    while True:
        data = get_valid_gps(gps)
        logger.write_log("Publishing gps data {}".format(data))
        mqtt_client.publish(topic=CONST.GPS_TOPIC, payload=json.dumps(data))
        time.sleep(1)

if __name__ == "__main__":
    main()
