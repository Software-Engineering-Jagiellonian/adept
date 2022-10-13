from settings import NORMAL_LOGGER_NAME, EXCEPTION_LOGGER_NAME, EXCEPTION_LOGGER_KEY, NORMAL_LOGGER_KEY, FORMATTER_STRING, DATE_FORMAT_STRING
import logging


def get_exception_logger():
    return logging.getLogger(EXCEPTION_LOGGER_KEY)


def get_normal_logger():
    return logging.getLogger(NORMAL_LOGGER_KEY)


def initialize_loggers():
    setup_logger(NORMAL_LOGGER_KEY, NORMAL_LOGGER_NAME)
    setup_logger(EXCEPTION_LOGGER_KEY, EXCEPTION_LOGGER_NAME)
    

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    
    formatter = logging.Formatter(FORMATTER_STRING, DATE_FORMAT_STRING)
    
    fileHandler = logging.FileHandler(log_file)
    fileHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)