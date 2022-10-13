#!/usr/local/bin/python

from tools.logger_tools import initialize_loggers, get_normal_logger, get_exception_logger
from tools.sonar_prediction_tools import make_prediction_for_all_projects

initialize_loggers()
normal_logger = get_normal_logger()
try:
    normal_logger.info('Start predictions')
    make_prediction_for_all_projects()
    normal_logger.info('End predictions')
except Exception as e:
    get_exception_logger().exception(e)
