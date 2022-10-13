import logging

__NORMAL_LOGGER_NEME = "/DePress/logs/logs.log"
__EXCEPTION_LOGGER_NAME = "/DePress/logs/exception_logs.log"

__EXCEPTION_LOGGER_KEY = 'exception_logger'
__NORMAL_LOGGER_KEY = 'normal_logger'

__FORMATTER_STRING = '%(asctime)s - %(levelname)-10s - %(message)s'
__DATE_FORMAT_STRING = '%m/%d/%Y %I:%M:%S %p'

PREFIX_LOG_LENGTH = 38

def get_exception_logger():
    return logging.getLogger(__EXCEPTION_LOGGER_KEY)


def get_normal_logger():
    return logging.getLogger(__NORMAL_LOGGER_KEY)


def initialize_loggers():
    setup_logger(__NORMAL_LOGGER_KEY, __NORMAL_LOGGER_NEME)
    setup_logger(__EXCEPTION_LOGGER_KEY, __EXCEPTION_LOGGER_NAME)
    

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    
    formatter = logging.Formatter(__FORMATTER_STRING, __DATE_FORMAT_STRING)
    
    fileHandler = logging.FileHandler(log_file)
    fileHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)

    