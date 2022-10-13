# Prod
headers = dict(
   Authorization = ''
)
SONAR_URL = ''

__NORMAL_LOGGER_NEME = "logs.log"
__EXCEPTION_LOGGER_NAME = "exception_logs.log"

__EXCEPTION_LOGGER_KEY = 'exception_logger_sonar6_collector'
__NORMAL_LOGGER_KEY = 'normal_logger_sonar6_collector'
db_engine_url = 'mysql://'

# QA
#headers = dict(
#    Authorization = ''
#)
#SONAR_URL = ''

#__NORMAL_LOGGER_NEME = "logs.log"
#__EXCEPTION_LOGGER_NAME = "exception_logs.log"

#__EXCEPTION_LOGGER_KEY = 'exception_logger_sonar6_collector'
#__NORMAL_LOGGER_KEY = 'normal_logger_sonar6_collector'
#db_engine_url = 'mysql://'



#Unwersal 

__FORMATTER_STRING = '%(asctime)s - %(levelname)-10s - %(message)s'
__DATE_FORMAT_STRING = '%m/%d/%Y %I:%M:%S %p'

PREFIX_LOG_LENGTH = 38


RESOURCES_API = 'api/measures/component_tree'
PROJECTS_API = 'api/projects/index'
COMPONENTS_API = 'api/components/show'
METRICS_API = 'api/metrics/search'

PAGE_SIZE = 500
MAX_METRICS_PER_REQUEST = 15 
AVAILABLE_METRICS_TYPE_LIST  = ['INT', 'FLOAT', 'PERCENT', 'BOOL', 'STRING', 'MILLISEC', 'LEVEL', 'RATING', 'WORK_DUR']