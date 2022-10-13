import base64

# Authorization
USERNAME = ''
PASSWORD = ''
AUTHORIZATION_STRING = '' + base64.b64encode(USERNAME + ':' + PASSWORD)

# DataBase
MYSQL_HOST = ''
MYSQL_DATABASE = ''
MYSQL_DATABASE_RESULTS = ''
MYSQL_LOGIN = ''
MYSQL_PASSWORD = ''

# Jira
JIRA_URL = ""
PROJECT_API = ""
ISSUES_API = ""

JIRA_BUGS_ISSUE_TYPE_ID_LIST = [1, 14, 15, 18, 22, 29]

# HP Quality Center
QUALITY_CENTER_URL = ''
QUALITY_CENTER_AUTHENTICATE_GET = QUALITY_CENTER_URL + 'qcbin/authentication-point/authenticate'
QUALITY_CENTER_IS_AUTHENTICATED_GET = QUALITY_CENTER_URL + 'qcbin/rest/is-authenticated'
QUALITY_CENTER_LOGOUT_GET = QUALITY_CENTER_URL + 'qcbin/authentication-point/logout'
QUALITY_CENTER_OPENING_SESSION_POST = QUALITY_CENTER_URL + 'qcbin/rest/site-session'
QUALITY_CENTER_CLOSING_SESSION_DELETE = QUALITY_CENTER_URL + 'qcbin/rest/site-session'
QUALITY_CENTER_DEFECT_GET = QUALITY_CENTER_URL + 'qcbin/rest/domains/{0}/projects/{1}/defects?query={{id[{2}]}}'
QUALITY_CENTER_DEFECT_BY_CQ_ID_GET = QUALITY_CENTER_URL + 'qcbin/rest/domains/{0}/projects/{1}/defects?query={{{2}[{3}]}}'

QUALITY_CENTER_ISSUE_CATEGORY_DEFECT_IN_ADEPT_DB = 1
QUALITY_CENTER_ISSUE_CATEGORY_CHANGE_REQUEST_IN_ADEPT_DB = 2
QUALITY_CENTER_ISSUE_CATEGORY_ENHANCEMENT_SUGGESTION_IN_ADEPT_DB = 3
QUALITY_CENTER_ISSUE_CATEGORY_OTHER_IN_ADEPT_DB = 4


# Sonar
SONAR4_EXCLUDED_FEATURE_NAMES_LIST = ['new_violations', 'new_xxxxx_violations', 'violations', 'xxxxx_violations', 'false_positive_issues', 'open_issues', 'confirmed_issues', 'reopened_issues', 'weighted_violations', 'violations_density', 'sqale_index']
SONAR_URL = ''
SONAR_COMPONENTS_API = 'api/components/show'
SONAR_SUBPROJECT_REGEXP = r'\w+([:.]\w+)+:\w+-\w+-\w+-\w+-\w+'

# Adept
R_TABLE_MODEL_ID = 3
R_TABLE_DEFAULT_VERSION = 1
R_TABLE_DEFAULT_PREDICTION_VERSION = 0


#logger
NORMAL_LOGGER_NAME = "logs.log"
EXCEPTION_LOGGER_NAME = "exception_logs.log"
EXCEPTION_LOGGER_KEY = 'exception_logger'
NORMAL_LOGGER_KEY = 'normal_logger'
FORMATTER_STRING = '%(asctime)s - %(levelname)-10s - %(message)s'
DATE_FORMAT_STRING = '%m/%d/%Y %I:%M:%S %p'
PREFIX_LOG_LENGTH = 38
