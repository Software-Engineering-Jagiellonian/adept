#! /usr/bin/python

import SonarTools, DatabaseTools
from loggerTools import initialize_loggers, get_normal_logger, get_exception_logger


initialize_loggers()
normal_logger = get_normal_logger()
try:
    normal_logger.info('Start collecting metrics.')
    metric_tuple = SonarTools.get_compleate_metrics_tuple_list()
    DatabaseTools.update_database(metric_tuple)
    normal_logger.info('End collecting metrics.')
except Exception as e:
    get_exception_logger().exception(e)
