from mqtt.mqtt_conn import MQTTClient
import constants.constants_sync as CONST
import time
import json
from datetime import datetime, timezone
from log.logger import Logger
from datetime import datetime

def main():

    logger = Logger(CONST.LOG_FILE,CONST.LOG_PATH)

    logger.write_log("Connecting to mqtt broker...")

    mqtt_client = MQTTClient(client_id=CONST.CLIENT_ID)
    mqtt_client.connect()

    logger.write_log("done!")

    while True:
        t1 = datetime.now()
        message = dict()
        message["delta"] = CONST.TIME_DELTA
        message["locomotive"] = CONST.LOCOMOTIVE_NUMBER
        message["timestamp"] = datetime.now(timezone.utc).isoformat()

        logger.write_log("publishing sync message: {}".format(message))
        mqtt_client.publish(CONST.SYNC_TOPIC, json.dumps(message))
        
        time.sleep(CONST.TIME_DELTA)
        t2 = datetime.now()
        print("delta: {}".format(t2-t1))


# Example usage
if __name__ == "__main__":
    main()