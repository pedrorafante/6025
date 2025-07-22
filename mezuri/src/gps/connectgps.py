import socket
import pynmea2
import threading
import datetime
import dateutil.parser as DateParser
from .constants_gps import *
import time

class GPS():

    def __init__(self):
        """
        Método que inicializa o módulo de GPS. inicializa com lock do gps como falso.

        Method that initialize the GPS module. Set gps locked as false.

        Args:
            None
        Returns:
            None
        """
        self.gps_data = self.parse_fake_gps()
        self.thread_gps = None
        self.gps_locked = False
        self.gps_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    def parse_fake_gps(self):
        """
        Método que cria dados falsos de gps, para caso de falta de cobertura de satélite. O formato dos dados
        é idêntico aos dados reais.

        Method that create a fake gps data, for the case the GPS did not lock with satellite yet. The fake data has the same
        format as if the GPS lost connection after a lock.

        Args:
            None
        Returns:
            A dictionary with fake gps data.
        """
        self.gps_locked = False
        gps_data = dict()
        gps_data['gps_timestamp'] = datetime.datetime.now().timestamp()
        gps_data['gps_status'] = 'V'
        gps_data['gps_lat'] = 'E01'
        gps_data['gps_lon'] = 'E01'
        gps_data['gps_mag_variation'] = 'E01'
        gps_data['gps_mag_var_dir'] = 'E01'
        gps_data['gps_speed_on_ground'] = 'E01'
        gps_data['gps_true_course'] = 'E01'
        return gps_data
        
    def parseRMC(self, gps_message):
        """
        Método que recebe uma sentença nmea2 e realiza o parsing para obter os dados de gps.

        Method that receives a nmea2 sentence and perform a parsing to get useful gps data.

        Args:
            gps_message:: String that holds a nmea2 sentence.
        Returns:
            None
        """
        data = pynmea2.parse(gps_message)
        if data.status == 'A':
            date_time = "{0}T{1}".format(data.datestamp,data.timestamp)
            self.gps_data['gps_timestamp'] = DateParser.parse(date_time).timestamp()
            self.gps_data['gps_status'] = data.status
            self.gps_data['gps_lat'] = data.latitude
            self.gps_data['gps_lon'] = data.longitude
            self.gps_data['gps_mag_variation'] = data.mag_variation
            self.gps_data['gps_mag_var_dir'] = data.mag_var_dir
            self.gps_data['gps_speed_on_ground'] = data.spd_over_grnd
            self.gps_data['gps_true_course'] = data.true_course
            self.gps_locked = True
        else:
            self.gps_data = self.parse_fake_gps()

    def get_gps(self):
        """
        Método que retorna os dados de GPS. Se estiver em lock com os satélites, retorna dados reais, caso contrário retorna dados falsos.

        Method that returns a GPS data. It returns the corect data if GPS is locked, or return a fake data if GPS is not locked.

        Args:
            None
        Returns:
            GPS data.
        """
        if self.gps_locked:
            return self.gps_data
        else:
            return self.parse_fake_gps()

    def connect_gps(self):
        """
        Método que cria uma conexão com o serviço de GPS dentro do IR829.

        Method that creates a connection to the GPS server inside IR829.

        Args:
            None
        Returns:
            None
        """

        self.gps_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.gps_socket.settimeout(5)
        toBreak = False
        while True:
            try:
                self.gps_data = self.parse_fake_gps()
                self.gps_socket.bind(GPS_BIND)
                toBreak = True
            except Exception as e:
                pass
                # print("ERROR:: {}".format(e))
            if toBreak:
                break
            time.sleep(1)

    def collect_gps_data(self):
        """
        Método que coleta dados a partir do serviço de GPS dentro do IR829, filtrando sentenças GPRMC. Se obter GPRMC, o estado de lock vai para verdadeiro.
        
        Method that consults GPS data from IR829 websocket. It filters to only get GPRMC sentences. If get a GPRMC sentence, the lock state goes to True.

        Args:
            None
        Returns:
            None
        Raises:
            TypeError: Basic exception
            ValueError: The lock state goes to False.
        """
        self.connect_gps()
        while True:
            try:
                data, _ = self.gps_socket.recvfrom(1024)
                gps_message = data.decode("utf-8")[:-2]

                if "GPRMC" in gps_message:
                    self.parseRMC(gps_message)
            except BaseException as e:
                print("ERROR:: {}".format(e))
                self.gps_socket.close()
                self.connect_gps()

    def run(self):
        """
        Método que executa o módulo de GPS em uma thread.

        Method that run the GPS module as a thread.

        Args:
            None
        Returns:
            None
        """
        self.thread_gps = threading.Thread(target=self.collect_gps_data)
        self.thread_gps.daemon = True
        self.thread_gps.start()


def main():
    """
    Método que testa a execução do módulo de GPS

    Method to test the GPS module execution.

    Args:
        None
    Returns:
        None
    """
    import time
    lgps = GPS()
    lgps.run()
    while True:
        print(lgps.gps_data)
        time.sleep(1)

if __name__ == "__main__":
    main()
