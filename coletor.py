import serial
import time
from datetime import datetime

# File paths
DATA_FILE = "data.txt"
TIMESTAMP_FILE = "timestamps.txt"

# Serial connection parameters
SERIAL_PORT = "/dev/ttySPRU4"  # Change this to your serial port (e.g., '/dev/ttyUSB0' for Linux)
BAUDRATE = 9600
BYTESIZE = serial.SEVENBITS
PARITY = serial.PARITY_EVEN
STOPBITS = serial.STOPBITS_ONE
XONXOFF = False
TIMEOUT = 1  # 1-second timeout for serial reads

def capture_serial_data():
    try:
        # Open serial connection
        with serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            bytesize=BYTESIZE,
            parity=PARITY,
            stopbits=STOPBITS,
            xonxoff=XONXOFF,
            timeout=TIMEOUT
        ) as ser:
            start_time = time.time()
            end_time = start_time + 60  # Capture data for 1 minute
            
            with open(DATA_FILE, "w") as data_file, open(TIMESTAMP_FILE, "w") as timestamp_file:
                while time.time() < end_time:
                    # Read until terminator '\r'
                    data = ser.read_until(b'\r').decode('ascii', errors='ignore').strip()
                    if data:
                        # Get the current timestamp
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                        
                        # Write to files
                        data_file.write(data + "\n")
                        timestamp_file.write(timestamp + "\n")
                        
                        print(f"Data: {data}, Timestamp: {timestamp}")  # For debugging/monitoring

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    capture_serial_data()

