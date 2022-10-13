#!/usr/local/bin/python

from tools.logger_tools import initialize_loggers, get_normal_logger, get_exception_logger
from tools.prediction_result_tools import move_raw_predicton_to_R_tables_for_all_projects

initialize_loggers()
normal_logger = get_normal_logger()
exception_logger = get_exception_logger()
try:
    normal_logger.info('*** START moving RAW results to R_ tables ***')
    move_raw_predicton_to_R_tables_for_all_projects()
    normal_logger.info('*** END of moving RAW results to R_ tables ***')
except Exception as e:
    exception_logger.info('*** START create_results exception log ***')
    exception_logger.exception(e)
    exception_logger.info('*** END create_results exception log ***')
