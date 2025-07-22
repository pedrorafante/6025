from mqtt.constants_mqtt import ADDR, PORT
import paho.mqtt.client as mqtt
import ssl
import traceback

class MQTTClient:
    def __init__(self, broker_address=None, broker_port=None, client_id=None):
        self.broker_address = broker_address or ADDR
        self.broker_port = broker_port or PORT
        self.client_id = client_id or "mqttclient_{}".format(broker_address)
        self.client = mqtt.Client(self.client_id)

        self.client.on_message = self.on_message

        self.topic_callbacks = {}

    def connect(self):
        self.client.connect(self.broker_address, self.broker_port, 60)
        self.client.loop_start()
        # print("Connected to MQTT broker at {0}:{1}".format(self.broker_address,self.broker_port))

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        # print("Disconnected from MQTT broker at {0}:{1}".format(self.broker_address,self.broker_port))

    def on_message(self, client, userdata, message):
        topic = message.topic
        payload = message.payload.decode()
        # print("Received message: '{0}' on topic: '{1}'".format(payload,topic))

        # Call the specific callback for this topic, if available
        for registered_topic, callback in self.topic_callbacks.items():
            if mqtt.topic_matches_sub(registered_topic, topic):
                callback(topic,payload)
                break
            # else:
            #     print("No callback found for topic: {0}".format(topic))

    def subscribe(self, topic, callback=None):
        self.client.subscribe(topic)
        # print("Subscribed to topic: {0}".format(topic))

        # Store the callback if provided
        if callback:
            self.topic_callbacks[topic] = callback
            # print("Registered callback for topic: {0}".format(topic))

    def publish(self, topic, payload):
        self.client.publish(topic, payload)
        # print("Published message: '{0}' to topic: '{1}'".format(payload,topic))
    

class AWSMQTTClient:
    def __init__(self, client_id=None, aws_endpoint=None,aws_port=None,
                 aws_cert=None, aws_key=None, aws_ca=None):
        self.client = mqtt.Client(client_id) or ""
        self.aws_endpoint = aws_endpoint
        self.aws_port = aws_port
        self.aws_cert = aws_cert
        self.aws_key = aws_key
        self.aws_ca = aws_ca

    def ssl_alpn(self):
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.set_alpn_protocols(["x-amzn-mqtt-ca"])
            ssl_context.load_verify_locations(self.aws_ca)
            ssl_context.load_cert_chain(certfile=self.aws_cert, keyfile=self.aws_key)
            return ssl_context
        except Exception as e:
            print(e)
            print(traceback.print_exc())
            raise e

    def connect_aws(self):
        self.stop()
        if not all([self.aws_endpoint, self.aws_cert, self.aws_key, self.aws_ca]):
            raise ValueError("AWS IoT Core parameters must be set")

        ssl_context = self.ssl_alpn()

        self.client.tls_set_context(context=ssl_context)

        self.client.connect(self.aws_endpoint, self.aws_port)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic, payload):
        self.client.publish(topic, payload)
        # print("Published message: '{0}' to topic: '{1}'".format(payload,topic))
    


def main():
    # Create instance of the class
    mqtt_client = MQTTClient(client_id="client123")

    # Connect to the broker
    mqtt_client.connect()

    # Define custom callbacks
    def callback_topic1(message):
        print("Callback for topic1: {0}".format(message))

    def callback_topic2(message):
        print("Callback for topic2: {0}".format(message))

    # Subscribe to topics with specific callbacks
    mqtt_client.subscribe("topic1", callback_topic1)
    mqtt_client.subscribe("topic2", callback_topic2)

    input("Press Enter to exit...\n")

    # Disconnect from the broker
    mqtt_client.disconnect()


# Example usage
if __name__ == "__main__":
    main()