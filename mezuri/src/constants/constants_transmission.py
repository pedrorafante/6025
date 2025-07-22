import os

"""
Constantes referentes à transmissão dos dados.
"""

LOG_NAME = "TRANSMISSION.LOG"
LOG_PATH = "/var/log/"

CLIENT_ID = "transmitter"
REQUEST_DATA_TOPIC = "request_data"
SEND_DATA_TOPIC = "send_data"

PACKAGE_SIZE = 60

DEFAULT_DATA_MSG = {"package_size": PACKAGE_SIZE, "answer_topic": SEND_DATA_TOPIC}

AWS_ENDPOINT = "a3eyvgkwgag9hz-ats.iot.us-east-1.amazonaws.com"
AWS_PORT = 443

AWS_CLIENT = "vli_000"
AWS_TOPIC = "dev/vli/000"

CERTS_DIR = 'aws_certs'
AWS_CERT_FILE = "device-cert.pem"
AWS_KEY_FILE = "private.key"
AWS_CA_FILE = "ca1.pem"

AWS_CERT = os.path.join(os.path.dirname(__file__), CERTS_DIR, AWS_CERT_FILE)
AWS_KEY = os.path.join(os.path.dirname(__file__), CERTS_DIR, AWS_KEY_FILE)
AWS_CA = os.path.join(os.path.dirname(__file__), CERTS_DIR, AWS_CA_FILE)

LOCO_NUMBER = 6025
