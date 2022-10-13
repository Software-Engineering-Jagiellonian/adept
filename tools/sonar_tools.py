"""
tools.db_tools
~~~~~~~~~~~~

Modul obslugi bazy danych z metrykami z Sonar 4 

:copyright:
:license:

"""

from db_tools import get_select_result, get_select_result_list, save_to_db, get_select_result_field_value_or_None
from jira_svn_integrator_tools import merge_svn_with_jira_for_all_project
from dateutil import parser
from settings import AUTHORIZATION_STRING, SONAR_URL, SONAR_COMPONENTS_API, SONAR_SUBPROJECT_REGEXP
from api_tools import get_json_from_api
import re


def get_path_for_sonar_subproject_key(sonar_subproject_key):
    """Metoda zwraca nam rzeczywista scierzek dla klucza subprojektu z sonara

    :param sonar_subproject_key: nazwa zwrzutu w bazie danych
    :return: scierzka bezwzgledna podprojektu
    :rtype: str
    """

    subproject_data = __get_or_update_data_for_sonar_subproject_key(sonar_subproject_key)
    if not subproject_data:
        return None
    return subproject_data['path']


def get_metrics_for_version(db_name):
    """Metoda oczytuje z bazy danych i zwraca najstarszy zrzut metryk podanej nazwy zrzutu metryk z sonara

    :param db_name: nazwa zwrzutu w bazie danych
    :return: Lista slownikow z metrykami
    :rtype: List
    """

    query = 'SELECT * FROM Metrics WHERE db_name=\"' + db_name + '\"'
    return get_select_result_list(query)


def get_metics_for_version_with_subproject_path(db_name):
    """Metoda oczytuje z bazy danych i zwraca najstarszy zrzut metryk podanej nazwy zrzutu metryk z sonara z dodanymi sciezkami dla podprojektow

    :param db_name: nazwa zwrzutu w bazie danych
    :return: Lista slownikow z metrykami
    :rtype: List
    """

    metrics = get_metrics_for_version(db_name)
    regexp = re.compile(SONAR_SUBPROJECT_REGEXP)
    for metric in metrics:
        path = ''
        if regexp.search(metric['file_name']):
            path = str(get_path_for_sonar_subproject_key(regexp.search(metric['file_name']).group())) + '/'
        path = path + metric['file_name'].split(':')[-1]
        metric['path'] = path
    return metrics


def get_latest_db_name_for_project(project_sonar_name):
    """ Zwraca nam najnowszy snapshot z sonar 4 dla danego projektu

    :param project_sonar_name: nazwa projektu
    :return: Nazwa najnowszego shnapshotu z sonra 4 dla projketu
    :rtype: String
    """

    query = 'SELECT db_name FROM Projects WHERE name = \"' + project_sonar_name + '\" ORDER BY db_name DESC LIMIT 1'
    result = get_select_result(query)
    if result:
        return result['db_name']
    else:
        return ''


def get_latest_snapshot_date_adept_prediction_result_for_project(project_sonar_name):
    """ Zwraca nam date majnowszego zrzutu metryk dostepnego dla podanego klucza projektu z sonara

    :param project_sonar_name: nazwa projektu
    :return: Data ostatniego shnapshotu z sonra 4 dla projketu
    :rtype: Datetime
    """

    return __get_date_from_snapshot_name(get_latest_snapshot_name_adept_prediction_result_for_project(project_sonar_name))


def get_latest_snapshot_name_adept_prediction_result_for_project(project_sonar_name):
    """ Zwraca nam date majnowszego zrzutu metryk dostepnego dla podanego klucza projektu z sonara

    :param project_sonar_name: nazwa projektu
    :return: Data ostatniego shnapshotu z sonra 4 dla projketu
    :rtype: Datetime
    """

    select_query = 'SELECT DISTINCT db_name FROM Metrics WHERE prediction>0 AND db_name LIKE "{0}_20%" ORDER BY db_name DESC Limit 1'.format(project_sonar_name)
    return get_select_result_field_value_or_None(select_query, 'db_name')


def get_oldest_db_name_for_project(project_sonar_name):
    """ Zwraca nam najstarszy snapshot z sonar 4 dla danego projektu

    :param project_sonar_name: nazwa projektu
    :return: Nazwa ostatniego shnapshotu z sonra 4 dla projketu
    :rtype: String
    """

    query = 'SELECT db_name FROM Projects WHERE name = \"' + project_sonar_name + '\" LIMIT 1'
    result = get_select_result(query)
    if result:
        return result['db_name']
    else:
        return ''


def add_defect_prone_flag_to_oldest_metric_for_all_projects():
    """ Metoda pobiera dane z jiry i svn a nastepnie oznacza pliki defektogenne w najstarszych metrykach dla sonara 4

    :return: nic nie zwraca 
    :rtype: None
    """
    
    projects_svn_jira_data = merge_svn_with_jira_for_all_project()
    for project_svn_jira_data in projects_svn_jira_data:
        add_defect_prone_flag_to_oldest_metric_for_project(project_svn_jira_data)


def __get_or_update_data_for_sonar_subproject_key(sonar_subproject_key):
    """Metoda zwraca lub pobiera do naszje bazy danych rzeczywista scierzek dla klucza subprojektu z sonara

    :param sonar_subproject_key: nazwa zwrzutu w bazie danych
    :return: scierzka bezwzgledna podprojektu
    :rtype: str
    """

    subproject_data = __get_subproject_data_for_sonar_subproject_key(sonar_subproject_key)
    if not subproject_data:
        api_sonar_subproject_data = __get_sonar_subproject_data_form_soanr_api(sonar_subproject_key)
        if api_sonar_subproject_data:
            subproject_data = __save_and_get_sonar_subproject_data(api_sonar_subproject_data)
    return subproject_data


def __get_subproject_data_for_sonar_subproject_key(sonar_subproject_key):
    """Metoda zwraca danych rzeczywista scierzek dla klucza subprojektu z sonara z bazy danch

    :param sonar_subproject_key: nazwa zwrzutu w bazie danych
    :return: scierzka bezwzgledna podprojektu
    :rtype: str
    """

    return get_select_result("SELECT * FROM SonarSubprojects WHERE subprojectKey = \"" + sonar_subproject_key + "\"")


def __get_sonar_subproject_data_form_soanr_api(sonar_subproject_key):
    """Metoda zwraca danych rzeczywista scierzek dla klucza subprojektu z sonara z api sonara

    :param sonar_subproject_key: nazwa zwrzutu w bazie danych
    :return: scierzka bezwzgledna podprojektu
    :rtype: str
    """

    headers = dict(
       Authorization = AUTHORIZATION_STRING
    )
    api_sonar_subproject_data = get_json_from_api(url = SONAR_URL + SONAR_COMPONENTS_API + "?component=" + sonar_subproject_key, headers = headers, ssl=True)
    if api_sonar_subproject_data.has_key("errors"):
        return None
    return api_sonar_subproject_data['component']


def __save_and_get_sonar_subproject_data(api_sonar_subproject_data):
    """Metoda pobiera do naszje bazy danych rzeczywista scierzek dla klucza subprojektu z sonara

    :param sonar_subproject_key: nazwa zwrzutu w bazie danych
    :return: scierzka bezwzgledna podprojektu
    :rtype: str
    """

    #TODO: remove print
    print "Save " + str(api_sonar_subproject_data['key'])
    save_query  = "INSERT INTO SonarSubprojects VALUES (\"{id}\", \"{key}\", \"{name}\", \"{path}\");".format(**api_sonar_subproject_data)
    save_to_db(save_query)
    return __get_subproject_data_for_sonar_subproject_key(api_sonar_subproject_data['key'])
    

def add_defect_prone_flag_to_oldest_metric_for_project(project_svn_jira_data):
    """ Dla danych z sv i jira oznacza pliki defektogenne w najstarszych metrykach dla sonara 4

    :param project_svn_jira_data: Dane z svn i jira z (jira_svn_integrator_tools.py)
    :return: Nic nie zwraca
    :rtype: None
    """

    db_name = get_oldest_db_name_for_project(project_svn_jira_data['metric_generator_name'])
    __set_all_file_to_none_defect_prone_file_in_db(db_name)
    defect_prone_files_list = list(project_svn_jira_data['defective_file_set'])
    __set_defect_prone_files_in_db(defect_prone_files_list, db_name)


def __set_defect_prone_files_in_db(defect_prone_files_list, db_name):
    """ Dla wszystkich polikow z listy oznacza te ktore sa defektogenne w podanym snapshocie z sonar4

    :param defect_prone_files_list: lista plikow defektogennych
    :param db_name: Nazwa snapshota w koteym oznaczymy pliki defektogenne 
    :return: Nic nie zwraca
    :rtype: None
    """

    for defect_prone_file in defect_prone_files_list:
        __set_defect_prone_file_in_db(defect_prone_file, db_name)


def __set_defect_prone_file_in_db(defect_prone_file, db_name):
    """ Oznacza plik defektogenny w podanym snapshocie z sonar4

    :param defect_prone_file: nazwa pliku  defektogennego
    :param db_name: Nazwa snapshota w koteym oznaczymy plik defektogenny
    :return: Nic nie zwraca
    :rtype: None
    """

    regexp = re.compile(SONAR_SUBPROJECT_REGEXP)
    src_index = defect_prone_file.find("src")
    query = ""
    if src_index > 0:
        query = 'UPDATE Metrics SET defects = 1 WHERE db_name = \"' + db_name + '\" AND file_name LIKE \"%' + defect_prone_file[src_index:] + '\"'
    elif regexp.search(defect_prone_file):
        query = 'UPDATE Metrics SET defects = 1 WHERE db_name = \"' + db_name + '\" AND file_name LIKE \"%' + defect_prone_file + '\"'
    if len(query) > 0:
        save_to_db(query)


def __set_all_file_to_none_defect_prone_file_in_db(db_name):
    """ Oznaczamy wszsytkie pliki jako nie defektogenne dla danego snapshota z sonar 4

    :param db_name: nazwa snapshota z sonar 4
    :return: Nic nie zwraca
    :rtype: None
    """

    query = 'UPDATE Metrics SET defects = 0 WHERE db_name = \"' + db_name + '\"'
    save_to_db(query)


def __get_date_from_snapshot_name(snapshot_name):
    """ zwraca nam date pozyskana z nazwy zrzutu sonara

    :param snapshot_name: nazwa zrzutu z sonar 4
    :return: Data pozyskana z nazwy zrzutu sonara
    :rtype: Datetime
    """

    if snapshot_name:
        date_as_string = snapshot_name.split('_')[-1]
        return parser.parse(date_as_string)
