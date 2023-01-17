import logging

from colorlog import ColoredFormatter


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(log_color)s%(levelname)s [%(asctime)s] Line: %(lineno)s %(filename)s %(message)s"
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOG_FORMAT, datefmt='%b/%d %H:%M:%S')
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream)

logging.basicConfig(filename='log.log', filemode='w')

