import paho.mqtt.client as mqtt

# Define the MQTT broker address and port
broker_address = "10.0.0.15"
broker_port = 1883

# Create a new MQTT client instance
client = mqtt.Client("Publisher")

# Connect to the broker
client.connect(broker_address, broker_port)


client.subscribe("topic1")
client.subscribe("topic2")

topic = "topic1"
message = "Hello MQTT! TOPIC1"
client.publish(topic, message)

topic = "topic2"
message = "Hello MQTT! TOPIC2"
client.publish(topic, message)

# Disconnect from the broker
client.disconnect()

print(f"Published message: '{message}' to topic: '{topic}'")