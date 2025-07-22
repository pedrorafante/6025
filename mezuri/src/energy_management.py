import subprocess
import time
from log.logger import Logger

def check_power_supply(logger):
    """
    Função que verifica se a fonte de energia está conectada ou se o cabo USB está conectado.

    Args:
    Logger: 
    Returns:
    None
    """
    command_str = "/usr/sbin/i2cget -y -f 0 0x24 0xA"
    command = command_str.split()

    result = subprocess.check_output(command)
    value = result.decode("utf-8")
    bytes_str = bin(int(value,16))
    ac_status = bytes_str[6]
    usb_status = bytes_str[7]
    logger.write_log("power checked: ac status is {} and usb status is {}".format(ac_status,usb_status))

    if ac_status == '0' and usb_status == '0':
        return False
    else:
        return True

def run_check(logger):
    """
    Método que avalia se a fonte de energia está conectada. Em caso negativo, o método realiza um desligamento normal de todo o sistema.

    Args:
    None
    Returns:
    None
    """
    command_str = "/sbin/shutdown -h now"
    command = command_str.split()
    checking_time = 10
    loop_time = 3

    while(True):
        logger.write_log("checking power supply...")
        if not check_power_supply(logger):
            logger.write_log("there is no power supply. Rechecking in {} seconds".format(checking_time))
            if not check_power_supply(logger):
                logger.write_log("Gracefully shutting down system...")
                time.sleep(5)
                subprocess.call(command)
            else:
                logger.write_log("Power is back online")
        
        logger.write_log("everything is fine.")
        time.sleep(loop_time)

time.sleep(5*60)
while True:
    logger = Logger('ENERGY.LOG', '/var/log/')
    try:
        run_check(logger)
    except Exception as e:
        logger.write_log_error(e)
        time.sleep(5)
        pass
