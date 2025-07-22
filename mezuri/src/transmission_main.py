import json
import base64
import zlib
import time
import constants.constants_transmission as CONST
from mqtt.mqtt_conn import MQTTClient, AWSMQTTClient

class Transmission:
    def __init__(self):
        self.mqtt_client = MQTTClient(client_id=CONST.CLIENT_ID)

        self.aws_client = AWSMQTTClient(client_id=CONST.AWS_CLIENT, 
                                        aws_endpoint=CONST.AWS_ENDPOINT,
                                        aws_port=CONST.AWS_PORT,
                                        aws_ca=CONST.AWS_CA,
                                        aws_cert=CONST.AWS_CERT,
                                        aws_key=CONST.AWS_KEY
                                        )
        
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(CONST.SEND_DATA_TOPIC, self.get_data)

        self.aws_client.connect_aws()

        self.last_id = 0
        self.message = None
        

    def request_data(self):
        req_msg = dict(CONST.DEFAULT_DATA_MSG)
        req_msg["last_id"] = self.last_id
        self.mqtt_client.publish(CONST.REQUEST_DATA_TOPIC, json.dumps(req_msg))


    def get_data(self, topic, message):
        self.message = message
        

    def send_data(self):
        print("waiting message")
        while not self.message:
            time.sleep(0.5)

        print("printing message")
        msg_list = json.loads(self.message)
        for item in msg_list:
            print(item)
            time.sleep(0.1)
        
        msg = {"locomotive": CONST.LOCO_NUMBER, 
               "data": base64.b64encode(zlib.compress(self.message.encode())).decode()}
        self.aws_client.publish(CONST.AWS_TOPIC, json.dumps(msg))

        print(msg)
        self.last_id = msg_list[-1]["id"]
        self.message = None
        print("all done")
        time.sleep(5)


def main():
    transmitter = Transmission()
    
    while True:
        if not transmitter.message:
            transmitter.request_data()
            transmitter.send_data()
        time.sleep(1)


if __name__ == "__main__":
    main()
