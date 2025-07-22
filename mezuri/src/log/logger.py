import logging
from logging.handlers import RotatingFileHandler

class Logger:
    """
    Classe responsável por gerenciar Logs, configurar rotação e definir tamanho de arquivo.
    """
    def __init__(self, logger_name,logger_path="/var/log/"):
        """
        Método de inicialização da classe Logger. Como entrada a classe necessita do nome do arquivo
        de log e o seu caminho.

        Method that initialize the Logger class.

        Args:
            logger_name:: log file name.
            logger_path:: log file path.
        Returns:
            None
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(logger_path+logger_name.lower(), maxBytes=5000000, backupCount=3)

        formatter = logging.Formatter(fmt='%(asctime)s - %(message)s', datefmt='[%Y-%m-%d %H:%M:%S]')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def write_log(self, message):
        """
        Método que grava uma mensagem no log, inserindo data e hora.

        Method that records a message in log, with timestamp.

        Args:
            message:: message to be stored in log.
        Returns:
            None
        """

        print(message)
        self.logger.info(message)

    def write_log_warn(self, message):
        """
        Método que grava uma mensagem de alerta no log, inserindo data e hora.

        Method that records a warning message in log, with timestamp.

        Args:
            message:: message to be stored in log.
        Returns:
            None
        """

        print("WARNING:: " + message)
        self.logger.warning("WARNING: " + message)
    
    def write_log_error(self, message):
        """
        Método que grava uma mensagem de erro no log, inserindo data e hora.

        Method that records an error message in log, with timestamp.

        Args:
            message:: message to be stored in log.
        Returns:
            None
        """

        print("ERROR:: " + str(message))
        self.logger.error("ERROR:: " + str(message))
