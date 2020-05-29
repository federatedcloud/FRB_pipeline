import logging
import datetime

logger = logging.getLogger(__name__)

def start_log():
    logfile = "Logs/run_" + datetime.datetime.now().strftime("%B_%d_%Y_%H_%M_%S") + ".log"
    logging.basicConfig(filename=logfile, level=logging.DEBUG)

def log_it(message=""):
    logger.debug("\n" + message)
    print(message)

