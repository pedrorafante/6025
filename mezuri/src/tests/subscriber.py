import paho.mqtt.client as mqtt

# Define the MQTT broker address and port
broker_address = "192.168.137.100"
broker_port = 1883
topic = "sync"

# Callback function for when a message is received
def on_message(client, userdata, message):
    print(f"Received message: '{message.payload.decode()}' on topic: '{message.topic}'")

# Create a new MQTT client instance
client = mqtt.Client("Subscriber")

# Assign the on_message callback function
client.on_message = on_message

# Connect to the broker
client.connect(broker_address, broker_port)

# Subscribe to the topic
client.subscribe(topic)
client.subscribe("gps")
client.subscribe("egu")

# Start the loop to process callbacks
client.loop_start()

# Keep the script running
input("Press Enter to exit...\n")

# Stop the loop and disconnect from the broker
client.loop_stop()
client.disconnect()
