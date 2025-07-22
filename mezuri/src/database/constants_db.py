DB_IP = "localhost"
DB_PORT = 3306
CONNECTION_STR = 'mysql+mysqldb://mezuridev:passwd@{0}:{1}/mezuridb'.format(DB_IP,DB_PORT)

CLIENT_ID = "receiver"
COMP_TOPIC_LIST = ["egu","cab","exc","aux"]
SYNC_TOPIC = "sync"
GPS_TOPIC = "gps"
GET_DATA = "request_data"

LOG_FILE = "DB_MAIN.LOG"
LOG_PATH = '/var/log/'