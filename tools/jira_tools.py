"""
tools.jira_tools
~~~~~~~~~~~~

Modul obslugi jiry

:copyright:
:license:

"""



from api_tools import get_json_from_api
from db_tools import get_select_result, save_to_db
from settings import AUTHORIZATION_STRING, JIRA_URL, PROJECT_API, ISSUES_API


def get_jira_key_for_project(project_name):
    """Zwraca dla podanego projekty jego klucz w jira  
    
    :param project_name: Nazwa projektu w jira
    :return: Klucz projektu w jira
    :rtype: unicode
    """

    return __get_jira_keys_dict_from_api()[project_name]


def __get_jira_keys_dict_from_api():
    """Zwraca slownik z kluczami projektow w jira 
    
    :return: slownik zawieracjacy klucze projektow
    {
        'Project': 'KLUCZ'
    ...
    }
    :rtype: dict
    """

    projects_dict = __get_projects_from_api()
    jira_keys_dict = {}
    for project in projects_dict:
        jira_keys_dict[project] = projects_dict[project]['key']
    return jira_keys_dict


def __get_projects_from_api():
    """Zwraca slownik z danymi projektow przechowywanych w jira 
    
    :return: slownik zawieracjacy dane projektow
    {
        'Project': {
            'name': 
            'self': 
            'avatarUrls': 
            'projectCategory':
            'key':
            'id':
        }
    ...
    }
    :rtype: dict
    
    """

    headers = {
        'Authorization': AUTHORIZATION_STRING,
    }

    project_list = get_json_from_api(url=JIRA_URL + PROJECT_API, headers=headers, ssl=True)

    projects_dict = {}
    for project in project_list:
        projects_dict[project['name']] = project

    return projects_dict 


def get_issue_type_for_jira_key(issue_key):
    issue_data = __get_or_update_issue_data_for_issue_key(issue_key)
    if issue_data == None:
        return None
    return issue_data['issueType']


def __get_or_update_issue_data_for_issue_key(issue_key):
    """Zwraca slownik odnosnie danych dotyczacych issue jiry pobiera go z bazy danych gdy go w niej nie ma to z jiry
    
    :param issue_key: klucz issue z jiry
    :return: slownik zawieracjacy dane odnosnie issue jiry
    {
        'issueType': <type 'long'>
        'issueId': ''
        'versionName': ''
    }
    :rtype: dict
    """

    issue_data = __get_issue_data_for_issue_key_from_db(issue_key)
    if not issue_data:
        api_issue_data = __get_issue_data_for_issue_key_from_jira_api(issue_key)
        if api_issue_data:
            print  issue_key
            __save_issue_to_db(issue_key, __get_issue_type_from_api_issue_data(api_issue_data), __get_issue_version_name_from_api_issue_data(api_issue_data))
    return issue_data


def __get_issue_data_for_issue_key_from_db(issue_key):
    """Zwraca slownik odnosnie danych dotyczacych issue jiry pobierany z bazy danych 
    
    :param issue_key: klucz issue z jiry
    :return: slownik zawieracjacy dane odnosnie issue jiry
    {
        'issueType': <type 'long'>
        'issueId': ''
        'versionName': ''
    }
    :rtype: dict
    """
    
    return get_select_result("SELECT * FROM JiraIssues WHERE issueId = \"" + issue_key + "\"")


def __get_issue_data_for_issue_key_from_jira_api(issue_key):
    """Zwraca slownik odnosnie danych dotyczacych issue jiry pobierany z serwera jira
    
    :param issue_key: klucz issue z jiry
    :return: slownik zawieracjacy dane odnosnie issue jiry
    {
        'issueType': <type 'long'>
        'issueId': ''
        'versionName': ''
    }
    :rtype: dict
    """

    headers = {
        'Authorization': AUTHORIZATION_STRING,
    }

    issue_data = get_json_from_api(url=JIRA_URL + ISSUES_API + issue_key, headers=headers, ssl=True)
    if issue_data.has_key('errorMessages'):
        issue_data = None
    return issue_data


def __save_issue_to_db(issue_id, issue_type, version_name):
    """Zapisuje dane osnosnie issue w bazie danych 
    
    :param issue_id: klucz issue z jiry
    :param issue_type: typ issue 
    :param version_name: nazwa wersji do ktorej tyczy sie zadanie
    :return: Nie zwracamy nic 
    :rtype: None
    """
   
    update_query = "INSERT INTO JiraIssues VALUES (\"" + issue_id + "\", " + issue_type + ", \"" + version_name + "\");"
    save_to_db(update_query)


def __get_issue_type_from_api_issue_data(api_issue_data):
    return api_issue_data['fields']['issuetype']['id']


def __get_issue_version_name_from_api_issue_data(api_issue_data):
    if len(api_issue_data['fields']['versions']) > 0:
        return api_issue_data['fields']['versions'][-1]['name']
    return ""
